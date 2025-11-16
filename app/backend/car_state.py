import reflex as rx
from pydantic import ValidationError
from sqlmodel import asc, desc, func, or_, select

from .models import Car


class CarState(rx.State):
    """State for managing car inventory."""

    current_car: Car = Car()
    cars: list[Car] = []
    search_car_value: str = ""
    sort_car_value: str = ""
    sort_car_reverse: bool = False
    add_car_dialog_open: bool = False
    edit_car_dialog_open: bool = False

    # Car filtering and pagination
    filter_car_make: str = "all"
    filter_car_min_year: str = ""
    filter_car_max_year: str = ""
    filter_car_min_price: str = ""
    filter_car_max_price: str = ""
    car_current_page: int = 1
    car_page_size: int = 10
    car_total_items: int = 0
    _unique_car_makes: list[str] = []

    # Form validation state
    car_errors: dict[str, str] = {}

    @rx.var
    def unique_car_makes(self) -> list[str]:
        """Get unique car makes for filter dropdown."""
        return self._unique_car_makes

    @rx.var
    def car_makes_options(self) -> list[str]:
        """Get car makes options including 'all' for filter dropdown."""
        return ["all"] + self._unique_car_makes

    @rx.var
    def car_total_pages(self) -> int:
        """Calculate total pages for car pagination."""
        return (
            -(-self.car_total_items // self.car_page_size)
            if self.car_total_items > 0
            else 1
        )

    def _map_pydantic_errors(self, exc: ValidationError) -> dict[str, str]:
        """Convert Pydantic ValidationError to field->message dict."""
        errors = {}
        for err in exc.errors():
            field = err["loc"][0] if err["loc"] else "field"
            errors[str(field)] = err["msg"]
        return errors

    @rx.event
    def set_edit_car_dialog_open(self, value: bool):
        self.edit_car_dialog_open = value
        if not value:
            self.car_errors = {}

    @rx.event
    def set_add_car_dialog_open(self, value: bool):
        self.add_car_dialog_open = value
        if not value:
            self.car_errors = {}

    # REMOVED: delete_car_dialog_open state and handler - using internal dialog state for consistency with working modals

    def load_cars_entries(self) -> list[Car]:
        """Get all cars from the database."""
        with rx.session() as session:
            query = select(Car)

            # Apply search filter
            if self.search_car_value:
                search_value = f"%{str(self.search_car_value).lower()}%"
                query = query.where(
                    or_(
                        Car.make.ilike(search_value),
                        Car.model.ilike(search_value),
                        Car.version.ilike(search_value),
                    )
                )

            # Apply make filter
            if self.filter_car_make and self.filter_car_make != "all":
                query = query.where(Car.make == self.filter_car_make)

            # Apply year range filter
            if self.filter_car_min_year:
                try:
                    min_year = int(self.filter_car_min_year)
                    query = query.where(Car.year >= min_year)
                except ValueError:
                    pass

            if self.filter_car_max_year:
                try:
                    max_year = int(self.filter_car_max_year)
                    query = query.where(Car.year <= max_year)
                except ValueError:
                    pass

            # Apply price range filter
            if self.filter_car_min_price:
                try:
                    min_price = float(self.filter_car_min_price)
                    query = query.where(Car.price >= min_price)
                except ValueError:
                    pass

            if self.filter_car_max_price:
                try:
                    max_price = float(self.filter_car_max_price)
                    query = query.where(Car.price <= max_price)
                except ValueError:
                    pass

            # Get total count for pagination
            total_count_query = select(func.count()).select_from(
                query.with_only_columns(Car.id).alias()
            )
            self.car_total_items = session.exec(total_count_query).one()

            # Apply sorting
            if self.sort_car_value:
                sort_column = getattr(Car, self.sort_car_value)
                if self.sort_car_value in ["price", "year"]:
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

            # Apply pagination
            offset = (self.car_current_page - 1) * self.car_page_size
            query = query.offset(offset).limit(self.car_page_size)

            self.cars = session.exec(query).all()

            # Load unique makes for filter dropdown
            if not self._unique_car_makes:
                makes_query = select(Car.make).distinct()
                makes = session.exec(makes_query).all()
                self._unique_car_makes = sorted(makes)

    @rx.event
    def on_mount_load(self):
        """Event wrapper for on_mount to trigger data loading."""
        self.load_cars_entries()

    def sort_car_values(self, sort_value: str):
        self.sort_car_value = sort_value
        self.load_cars_entries()

    def toggle_car_sort(self):
        self.sort_car_reverse = not self.sort_car_reverse
        self.load_cars_entries()

    def filter_car_values(self, search_value):
        self.search_car_value = search_value
        self.car_current_page = 1
        self.load_cars_entries()

    @rx.event
    def set_filter_car_make(self, value: str):
        self.filter_car_make = value

    @rx.event
    def set_filter_car_min_year(self, value: str):
        self.filter_car_min_year = value

    @rx.event
    def set_filter_car_max_year(self, value: str):
        self.filter_car_max_year = value

    @rx.event
    def set_filter_car_min_price(self, value: str):
        self.filter_car_min_price = value

    @rx.event
    def set_filter_car_max_price(self, value: str):
        self.filter_car_max_price = value

    @rx.event
    def apply_car_filters(self):
        self.car_current_page = 1
        self.load_cars_entries()

    @rx.event
    def reset_car_filters(self):
        self.filter_car_make = "all"
        self.filter_car_min_year = ""
        self.filter_car_max_year = ""
        self.filter_car_min_price = ""
        self.filter_car_max_price = ""
        self.car_current_page = 1
        self.load_cars_entries()

    @rx.event
    def set_car_page_size(self, size: str):
        self.car_page_size = int(size)
        self.car_current_page = 1
        self.load_cars_entries()

    @rx.event
    def go_to_car_page(self, page_num: int):
        self.car_current_page = max(1, min(page_num, self.car_total_pages))
        self.load_cars_entries()

    def get_car(self, car: Car):
        self.current_car = car
        self.edit_car_dialog_open = True
        self.car_errors = {}

    def add_car_to_db(self, form_data: dict):
        # Clear previous errors
        self.car_errors = {}

        try:
            # Convert string inputs to proper types
            form_data["year"] = int(form_data.get("year", 0))
            form_data["price"] = int(form_data.get("price", 0))

            # Pydantic validation via Car model
            self.current_car = Car(**form_data)

            with rx.session() as session:
                session.add(self.current_car)
                session.commit()
                session.refresh(self.current_car)

            self.load_cars_entries()
            self.add_car_dialog_open = False
            return rx.toast.success(
                f"Car {self.current_car.make} {self.current_car.model} has been added.",
                position="bottom-right",
            )
        except ValidationError as e:
            # Map Pydantic errors to state
            self.car_errors = self._map_pydantic_errors(e)
            # Show first error as toast
            first_error = next(iter(self.car_errors.values()), "Validation failed")
            return rx.toast.error(first_error, position="bottom-right")
        except (ValueError, TypeError) as e:
            return rx.toast.error(
                f"Invalid input: {str(e)}",
                position="bottom-right",
            )
        except Exception as e:
            return rx.toast.error(
                f"Error adding car: {str(e)}",
                position="bottom-right",
            )

    def update_car_to_db(self, form_data: dict):
        # Clear previous errors
        self.car_errors = {}

        try:
            # Convert string inputs to proper types
            form_data["year"] = int(form_data.get("year", 0))
            form_data["price"] = int(form_data.get("price", 0))

            # Pydantic validation via Car model
            validated_car = Car(**form_data)

            with rx.session() as session:
                car = session.exec(
                    select(Car).where(Car.id == self.current_car.id)
                ).first()
                if not car:
                    return rx.toast.error(
                        "Car not found",
                        position="bottom-right",
                    )

                # Update car attributes with validated data
                car.make = validated_car.make
                car.model = validated_car.model
                car.version = validated_car.version
                car.year = validated_car.year
                car.price = validated_car.price

                session.commit()
                session.refresh(car)
                self.current_car = car

            self.load_cars_entries()
            self.edit_car_dialog_open = False
            return rx.toast.success(
                f"Car {self.current_car.make} {self.current_car.model} has been modified.",
                position="bottom-right",
            )
        except ValidationError as e:
            # Map Pydantic errors to state
            self.car_errors = self._map_pydantic_errors(e)
            # Show first error as toast
            first_error = next(iter(self.car_errors.values()), "Validation failed")
            return rx.toast.error(first_error, position="bottom-right")
        except (ValueError, TypeError) as e:
            return rx.toast.error(
                f"Invalid input: {str(e)}",
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
