import os

import openai
import reflex as rx
from pydantic import ValidationError
from sqlmodel import asc, desc, func, or_, select

from .models import Customer

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


class UserState(rx.State):
    """State for customer management and email generation."""

    current_user: Customer = Customer()
    users: list[Customer] = []
    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False
    products: dict[str, str] = {}
    email_content_data: str = (
        "Click 'Generate Email' to generate a personalized sales email."
    )
    gen_response = False
    tone: str = "😊 Formal"
    length: int = 1000

    # Form validation state
    customer_errors: dict[str, str] = {}

    def _map_pydantic_errors(self, exc: ValidationError) -> dict[str, str]:
        """Convert Pydantic ValidationError to field->message dict."""
        errors = {}
        for err in exc.errors():
            field = err["loc"][0] if err["loc"] else "field"
            errors[str(field)] = err["msg"]
        return errors

    @rx.event
    def set_tone(self, value: str):
        self.tone = value

    @rx.event
    def set_length(self, value: list[int | float]):
        self.length = int(value[0])

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

    @rx.event
    def on_mount_load(self):
        """Event wrapper for on_mount to trigger data loading."""
        self.load_entries()

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
        return UserState.call_openai
