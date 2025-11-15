import reflex as rx
from pydantic import field_validator


class Customer(rx.Model, table=True):  # type: ignore
    """The customer model."""

    customer_name: str
    email: str
    age: int
    gender: str
    location: str
    job: str
    salary: int

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Customer name is required")
        if len(v.strip()) < 2:
            raise ValueError("Customer name must be at least 2 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email is required")
        # Simple email validation
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.strip().lower()

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 18 or v > 120:
            raise ValueError("Age must be between 18 and 120")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ["Male", "Female", "Other"]:
            raise ValueError("Gender must be Male, Female, or Other")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Location is required")
        if len(v.strip()) < 2:
            raise ValueError("Location must be at least 2 characters")
        return v.strip()

    @field_validator("job")
    @classmethod
    def validate_job(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Job is required")
        if len(v.strip()) < 2:
            raise ValueError("Job must be at least 2 characters")
        return v.strip()

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Salary must be a positive number")
        return v


class Car(rx.Model, table=True):  # type: ignore
    """The car model."""

    make: str
    model: str
    version: str
    year: int
    price: int

    @field_validator("make")
    @classmethod
    def validate_make(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Make is required")
        if len(v.strip()) < 2:
            raise ValueError("Make must be at least 2 characters")
        return v.strip()

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Model is required")
        if len(v.strip()) < 2:
            raise ValueError("Model must be at least 2 characters")
        return v.strip()

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Version is required")
        if len(v.strip()) < 1:
            raise ValueError("Version must not be empty")
        return v.strip()

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = 2025
        if v < 1900 or v > current_year + 1:
            raise ValueError(f"Year must be between 1900 and {current_year + 1}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Price must be a positive number")
        return v
