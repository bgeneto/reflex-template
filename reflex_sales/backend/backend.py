import os

import openai
import reflex as rx
from sqlmodel import asc, desc, func, or_, select

from .models import Car, Customer

products: dict[str, dict] = {
    "T-shirt": {
        "description": "A plain white t-shirt made of 100% cotton.",
        "price": 10.99,
    },
    "Jeans": {
        "description": "A pair of blue denim jeans with a straight leg fit.",
        "price": 24.99,
    },
    "Hoodie": {
        "description": "A black hoodie made of a cotton and polyester blend.",
        "price": 34.99,
    },
    "Cardigan": {
        "description": "A grey cardigan with a V-neck and long sleeves.",
        "price": 36.99,
    },
    "Joggers": {
        "description": "A pair of black joggers made of a cotton and polyester blend.",
        "price": 44.99,
    },
    "Dress": {"description": "A black dress made of 100% polyester.", "price": 49.99},
    "Jacket": {
        "description": "A navy blue jacket made of 100% cotton.",
        "price": 55.99,
    },
    "Skirt": {
        "description": "A brown skirt made of a cotton and polyester blend.",
        "price": 29.99,
    },
    "Shorts": {
        "description": "A pair of black shorts made of a cotton and polyester blend.",
        "price": 19.99,
    },
    "Sweater": {
        "description": "A white sweater with a crew neck and long sleeves.",
        "price": 39.99,
    },
}

_client = None


def get_openai_client():
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    return _client


class State(rx.State):
    """The app state."""

    current_user: Customer = Customer()
    users: list[Customer] = []

    current_car: Car = Car()
    cars: list[Car] = []
    search_car_value: str = ""
    sort_car_value: str = ""
    sort_car_reverse: bool = False
    products: dict[str, str] = {}
    email_content_data: str = (
        "Click 'Generate Email' to generate a personalized sales email."
    )
    gen_response = False
    tone: str = "😊 Formal"
    length: int = 1000
    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    # Form validation states
    show_customer_dialog: bool = False
    show_car_dialog: bool = False
    show_edit_customer_dialog: bool = False
    show_edit_car_dialog: bool = False

    @rx.var
    def can_submit_customer(self) -> bool:
        """Check if customer form is valid."""
        return bool(
            self.current_user.customer_name
            and self.current_user.email
            and "@" in self.current_user.email
            and self.current_user.location
            and self.current_user.job
            and self.current_user.gender
            and self.current_user.age > 0
            and self.current_user.salary >= 0
        )

    @rx.var
    def can_submit_car(self) -> bool:
        """Check if car form is valid."""
        return bool(
            self.current_car.make
            and self.current_car.model
            and self.current_car.version
            and self.current_car.year > 0
            and self.current_car.price >= 0
        )

    @rx.event
    def set_tone(self, value: str):
        self.tone = value

    @rx.event
    def set_length(self, value: list[int | float]):
        self.length = int(value[0])

    @rx.event
    def update_car_field(self, field: str, value: str):
        """Update car field for real-time validation."""
        setattr(self.current_car, field, value)

    @rx.event
    def update_customer_field(self, field: str, value: str):
        """Update customer field for real-time validation."""
        setattr(self.current_user, field, value)

    def load_entries(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            query = select(Customer)
            if self.search_value:
                search_value = f"%{str(self.search_value).lower()}%"
                query = query.where(
                    or_(
                        *[
                            getattr(Customer, field).ilike(search_value)
                            for field in Customer.get_fields()
                        ],
                    )
                )

            if self.sort_value:
                sort_column = getattr(Customer, self.sort_value)
                if self.sort_value == "salary":
                    order = desc(sort_column) if self.sort_reverse else asc(sort_column)
                else:
                    order = (
                        desc(func.lower(sort_column))
                        if self.sort_reverse
                        else asc(func.lower(sort_column))
                    )
                query = query.order_by(order)

            self.users = session.exec(query).all()

    def load_cars_entries(self) -> list[Car]:
        """Get all cars from the database."""
        with rx.session() as session:
            query = select(Car)
            if self.search_car_value:
                search_value = f"%{str(self.search_car_value).lower()}%"
                query = query.where(
                    or_(
                        *[
                            getattr(Car, field).ilike(search_value)
                            for field in Car.model_fields.keys()
                        ],
                    )
                )

            if self.sort_car_value:
                sort_column = getattr(Car, self.sort_car_value)
                if self.sort_car_value == "price":
                    order = (
                        desc(sort_column) if self.sort_car_reverse else asc(sort_column)
                    )
                else:
                    order = (
                        desc(func.lower(sort_column))
                        if self.sort_car_reverse
                        else asc(func.lower(sort_column))
                    )
                query = query.order_by(order)

            self.cars = session.exec(query).all()

    def sort_car_values(self, sort_value: str):
        self.sort_car_value = sort_value
        self.load_cars_entries()

    def toggle_car_sort(self):
        self.sort_car_reverse = not self.sort_car_reverse
        self.load_cars_entries()

    def filter_car_values(self, search_value):
        self.search_car_value = search_value
        self.load_cars_entries()

    def sort_values(self, sort_value: str):
        self.sort_value = sort_value
        self.load_entries()

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    def filter_values(self, search_value):
        self.search_value = search_value
        self.load_entries()

    def get_user(self, user: Customer):
        self.current_user = user

    def add_customer_to_db(self, form_data: dict):
        try:
            # Validate form data
            if not form_data.get("customer_name", "").strip():
                return rx.toast.error(
                    "Customer name is required",
                    position="bottom-right",
                )
            if not form_data.get("email", "").strip():
                return rx.toast.error(
                    "Email is required",
                    position="bottom-right",
                )
            if not form_data.get("location", "").strip():
                return rx.toast.error(
                    "Location is required",
                    position="bottom-right",
                )
            if not form_data.get("job", "").strip():
                return rx.toast.error(
                    "Job is required",
                    position="bottom-right",
                )
            if not form_data.get("gender", "").strip():
                return rx.toast.error(
                    "Gender is required",
                    position="bottom-right",
                )

            # Convert and validate age and salary as integers
            try:
                age = int(form_data.get("age", 0))
                salary = int(form_data.get("salary", 0))
            except (ValueError, TypeError):
                return rx.toast.error(
                    "Age and Salary must be valid numbers",
                    position="bottom-right",
                )

            form_data["age"] = age
            form_data["salary"] = salary

            # Create and validate customer object
            self.current_user = Customer(**form_data)

            with rx.session() as session:
                if session.exec(
                    select(Customer).where(Customer.email == self.current_user.email)
                ).first():
                    return rx.toast.error(
                        "User with this email already exists",
                        position="bottom-right",
                    )
                session.add(self.current_user)
                session.commit()
                session.refresh(self.current_user)
            self.load_entries()
            return rx.toast.success(
                f"User {self.current_user.customer_name} has been added.",
                position="bottom-right",
            )
        except ValueError as e:
            return rx.toast.error(
                str(e),
                position="bottom-right",
            )
        except Exception as e:
            return rx.toast.error(
                f"Error adding customer: {str(e)}",
                position="bottom-right",
            )

    def update_customer_to_db(self, form_data: dict):
        try:
            # Validate form data
            if not form_data.get("customer_name", "").strip():
                return rx.toast.error(
                    "Customer name is required",
                    position="bottom-right",
                )
            if not form_data.get("email", "").strip():
                return rx.toast.error(
                    "Email is required",
                    position="bottom-right",
                )
            if not form_data.get("location", "").strip():
                return rx.toast.error(
                    "Location is required",
                    position="bottom-right",
                )
            if not form_data.get("job", "").strip():
                return rx.toast.error(
                    "Job is required",
                    position="bottom-right",
                )
            if not form_data.get("gender", "").strip():
                return rx.toast.error(
                    "Gender is required",
                    position="bottom-right",
                )

            # Convert and validate age and salary as integers
            try:
                age = int(form_data.get("age", 0))
                salary = int(form_data.get("salary", 0))
            except (ValueError, TypeError):
                return rx.toast.error(
                    "Age and Salary must be valid numbers",
                    position="bottom-right",
                )

            form_data["age"] = age
            form_data["salary"] = salary

            with rx.session() as session:
                customer = session.exec(
                    select(Customer).where(Customer.id == self.current_user.id)
                ).first()
                if not customer:
                    return rx.toast.error(
                        "Customer not found",
                        position="bottom-right",
                    )

                # Check for duplicate email (excluding current customer)
                if customer.email != form_data.get("email"):
                    existing = session.exec(
                        select(Customer).where(Customer.email == form_data.get("email"))
                    ).first()
                    if existing:
                        return rx.toast.error(
                            "Email already exists",
                            position="bottom-right",
                        )

                for key, value in form_data.items():
                    setattr(customer, key, value)
                session.commit()
                session.refresh(customer)
                self.current_user = customer
            self.load_entries()
            return rx.toast.success(
                f"User {self.current_user.customer_name} has been modified.",
                position="bottom-right",
            )
        except ValueError as e:
            return rx.toast.error(
                str(e),
                position="bottom-right",
            )
        except Exception as e:
            return rx.toast.error(
                f"Error updating customer: {str(e)}",
                position="bottom-right",
            )

    def delete_customer(self, id: int):
        """Delete a customer from the database."""
        try:
            with rx.session() as session:
                customer = session.exec(
                    select(Customer).where(Customer.id == id)
                ).first()
                if not customer:
                    return rx.toast.error(
                        "Customer not found",
                        position="bottom-right",
                    )
                customer_name = customer.customer_name
                session.delete(customer)
                session.commit()
            self.load_entries()
            return rx.toast.success(
                f"User {customer_name} has been deleted.", position="bottom-right"
            )
        except Exception as e:
            return rx.toast.error(
                f"Error deleting customer: {str(e)}", position="bottom-right"
            )

    def get_car(self, car: Car):
        self.current_car = car

    def add_car_to_db(self, form_data: dict):
        try:
            # Validate form data
            if not form_data.get("make", "").strip():
                return rx.toast.error(
                    "Make is required",
                    position="bottom-right",
                )
            if not form_data.get("model", "").strip():
                return rx.toast.error(
                    "Model is required",
                    position="bottom-right",
                )
            if not form_data.get("version", "").strip():
                return rx.toast.error(
                    "Version is required",
                    position="bottom-right",
                )

            # Convert and validate year and price as integers
            try:
                year = int(form_data.get("year", 0))
                price = int(form_data.get("price", 0))
            except (ValueError, TypeError):
                return rx.toast.error(
                    "Year and Price must be valid numbers",
                    position="bottom-right",
                )

            form_data["year"] = year
            form_data["price"] = price

            # Create and validate car object
            self.current_car = Car(**form_data)

            with rx.session() as session:
                session.add(self.current_car)
                session.commit()
                session.refresh(self.current_car)
            self.load_cars_entries()
            self.show_car_dialog = False
            return rx.toast.success(
                f"Car {self.current_car.make} {self.current_car.model} has been added.",
                position="bottom-right",
            )
        except ValueError as e:
            return rx.toast.error(
                str(e),
                position="bottom-right",
            )
        except Exception as e:
            return rx.toast.error(
                f"Error adding car: {str(e)}",
                position="bottom-right",
            )

    def update_car_to_db(self, form_data: dict):
        try:
            # Validate form data
            if not form_data.get("make", "").strip():
                return rx.toast.error(
                    "Make is required",
                    position="bottom-right",
                )
            if not form_data.get("model", "").strip():
                return rx.toast.error(
                    "Model is required",
                    position="bottom-right",
                )
            if not form_data.get("version", "").strip():
                return rx.toast.error(
                    "Version is required",
                    position="bottom-right",
                )

            # Convert and validate year and price as integers
            try:
                year = int(form_data.get("year", 0))
                price = int(form_data.get("price", 0))
            except (ValueError, TypeError):
                return rx.toast.error(
                    "Year and Price must be valid numbers",
                    position="bottom-right",
                )

            form_data["year"] = year
            form_data["price"] = price

            with rx.session() as session:
                car = session.exec(
                    select(Car).where(Car.id == self.current_car.id)
                ).first()
                if not car:
                    return rx.toast.error(
                        "Car not found",
                        position="bottom-right",
                    )

                for key, value in form_data.items():
                    setattr(car, key, value)
                session.commit()
                session.refresh(car)
                self.current_car = car
            self.load_cars_entries()
            return rx.toast.success(
                f"Car {self.current_car.make} {self.current_car.model} has been modified.",
                position="bottom-right",
            )
        except ValueError as e:
            return rx.toast.error(
                str(e),
                position="bottom-right",
            )
        except Exception as e:
            return rx.toast.error(
                f"Error updating car: {str(e)}",
                position="bottom-right",
            )

    def delete_car(self, id: int):
        """Delete a car from the database."""
        try:
            with rx.session() as session:
                car = session.exec(select(Car).where(Car.id == id)).first()
                if not car:
                    return rx.toast.error(
                        "Car not found",
                        position="bottom-right",
                    )
                car_name = f"{car.make} {car.model}"
                session.delete(car)
                session.commit()
            self.load_cars_entries()
            return rx.toast.success(
                f"Car {car_name} has been deleted.", position="bottom-right"
            )
        except Exception as e:
            return rx.toast.error(
                f"Error deleting car: {str(e)}", position="bottom-right"
            )

    @rx.event(background=True)
    async def call_openai(self):
        session = get_openai_client().chat.completions.create(
            user=self.router.session.client_token,
            stream=True,
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a salesperson at Reflex, a company that sells clothing. You have a list of products and customer data. Your task is to write a sales email to a customer recommending one of the products. The email should be personalized and include a recommendation based on the customer's data. The email should be {self.tone} and {self.length} characters long.",
                },
                {
                    "role": "user",
                    "content": f"Based on these {products} write a sales email to {self.current_user.customer_name} and email {self.current_user.email} who is {self.current_user.age} years old and a {self.current_user.gender} gender. {self.current_user.customer_name} lives in {self.current_user.location} and works as a {self.current_user.job} and earns {self.current_user.salary} per year. Make sure the email recommends one product only and is personalized to {self.current_user.customer_name}. The company is named Reflex its website is https://reflex.dev.",
                },
            ],
        )
        for item in session:
            if hasattr(item.choices[0].delta, "content"):
                response_text = item.choices[0].delta.content
                async with self:
                    if response_text is not None:
                        self.email_content_data += response_text
                yield

        async with self:
            self.gen_response = False

    def generate_email(self, user: Customer):
        self.current_user = user
        self.gen_response = True
        self.email_content_data = ""
        return State.call_openai
