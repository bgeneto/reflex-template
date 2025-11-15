"""Script to seed the cars table with initial test data using faker."""

import random

import reflex as rx
from faker import Faker
from sqlalchemy import text

from reflex_sales.backend.models import Car

# Initialize faker
fake = Faker()

# Car data generation
CAR_MAKES = [
    "Toyota",
    "Honda",
    "Ford",
    "Chevrolet",
    "BMW",
    "Mercedes-Benz",
    "Audi",
    "Lexus",
    "Nissan",
    "Volkswagen",
    "Hyundai",
    "Kia",
    "Volvo",
    "Subaru",
    "Mazda",
    "Tesla",
    "Porsche",
    "Ferrari",
]

CAR_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Tacoma"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit", "Ridgeline"],
    "Ford": ["F-150", "Mustang", "Explorer", "Fusion", "Focus", "Escape"],
    "Chevrolet": ["Silverado", "Malibu", "Equinox", "Traverse", "Camaro"],
    "BMW": ["X3", "X5", "3 Series", "5 Series", "X1", "1 Series"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "A-Class"],
    "Audi": ["A3", "A4", "Q5", "Q7", "A6", "Q3"],
    "Lexus": ["RX", "ES", "GX", "LX", "NX", "IS"],
    "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Titan"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf"],
    "Hyundai": ["Sonata", "Elantra", "Tucson", "Santa Fe", "Kona"],
    "Kia": ["Sorento", "Sportage", "Telluride", "Seltos", "Forte"],
    "Volvo": ["XC60", "XC90", "S60", "V60", "XC40"],
    "Subaru": ["Outback", "Forester", "Crosstrek", "Impreza", "Ascent"],
    "Mazda": ["CX-5", "CX-9", "Mazda3", "Mazda6", "MX-5 Miata"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X"],
    "Porsche": ["911", "Cayenne", "Macan", "Panamera", "Taycan"],
    "Ferrari": ["488 Spider", "Roma", "Portofino", "SF90 Stradale"],
}

CAR_VERSIONS = [
    "Base",
    "Sport",
    "Touring",
    "Luxury",
    "Premium",
    "Limited",
    "Platinum",
    "Executive",
    "Grand Touring",
    "Signature",
    "Ultimate Choice",
    "Reserve",
    "High Country",
]


def generate_cars(num_cars: int = 50):
    """Generate list of Car objects with fake data."""
    cars = []

    for _ in range(num_cars):
        make = random.choice(CAR_MAKES)
        model = random.choice(CAR_MODELS[make])
        version = random.choice(CAR_VERSIONS)
        year = random.randint(2018, 2024)

        # Generate realistic prices based on make and year
        base_price = {
            "Toyota": (20000, 45000),
            "Honda": (20000, 50000),
            "Ford": (25000, 55000),
            "Chevrolet": (22000, 52000),
            "BMW": (35000, 80000),
            "Mercedes-Benz": (40000, 90000),
            "Audi": (35000, 85000),
            "Lexus": (40000, 100000),
            "Nissan": (18000, 40000),
            "Volkswagen": (18000, 40000),
            "Hyundai": (17000, 35000),
            "Kia": (17000, 35000),
            "Volvo": (35000, 70000),
            "Subaru": (22000, 45000),
            "Mazda": (20000, 45000),
            "Tesla": (45000, 120000),
            "Porsche": (60000, 200000),
            "Ferrari": (250000, 500000),
        }

        min_price, max_price = base_price[make]
        # Adjust for year (newer cars tend to be more expensive)
        year_adjustment = (year - 2018) * 2000
        price = random.randint(min_price + year_adjustment, max_price + year_adjustment)

        car = Car(make=make, model=model, version=version, year=year, price=price)
        cars.append(car)

    return cars


def seed_cars():
    """Seed the cars table with fake data."""
    print("🌱 Seeding cars data...")

    # Generate car data
    cars = generate_cars(50)

    # Insert cars into database
    with rx.session() as session:
        # Clear existing cars (optional)
        session.exec(text("DELETE FROM car"))

        # Add new cars
        for car in cars:
            session.add(car)

        session.commit()

        print(f"✅ Successfully seeded {len(cars)} cars into the database!")

        # Print a few examples
        print("\n📋 Sample cars:")
        for car in cars[:5]:
            print(
                f"  - {car.year} {car.make} {car.model} {car.version}: ${car.price:,}"
            )


if __name__ == "__main__":
    seed_cars()
