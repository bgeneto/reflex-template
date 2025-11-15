# Implementation Plan

The plan adds a Cars inventory management feature to the existing personalized sales dashboard, transforming the single-page app into a multi-page dashboard with sidebar navigation.

The existing app focuses on customer management for generating personalized sales emails. This scope follows the same architectural patterns while adding car inventory CRUD operations. The implementation uses SQLAlchemy ORM for the Car model, integrates faker for initial data seeding, and maintains the reactive state-driven UI patterns already established in the codebase. Navigation changes to a sidebar-based layout with two main sections: Personalized Sales and Cars Inventory Management, enabling users to switch between customer email generation and car stock management seamlessly.

[Types]
The Car model introduces car-specific fields following SQLAlchemy and Reflex patterns.

Car(rx.Model, table=True):

- make: str ""
- model: str ""
- version: str ""
- year: int = 0
- price: float = 0.0

[Files]
File modifications support multi-page routing and car CRUD operations.

New files to create:
- reflex_sales/views/sidebar.py: Navigation component with links to / (Personalized Sales) and /cars (Cars Inventory Management)

Existing files to modify:
- backend/models.py: Add Car model import and definition
- backend/backend.py: Extend State class with car-related state variables and CRUD methods (current_car: Car, cars: list[Car], search/sort filters for cars, load_cars, add_car_to_db, update_car_to_db, delete_car methods)
- reflex_sales/reflex_sales.py: Add app.add_page for /cars route, modify index component to include sidebar, rename index to personalized_sales, create cars page component
- reflex_sales/views/__init__.py: Import sidebar component

[Functions]
Functions follow existing CRUD patterns with car-specific implementations.

New functions:
- State.load_cars(): Loads car entries from database with optional search/sort filtering
- State.add_car_to_db(data: dict): Creates new Car, checks for duplicates, adds to DB, shows toast
- State.update_car_to_db(data: dict): Updates existing Car, commits changes, shows toast
- State.delete_car(id: int): Deletes Car from database, shows toast
- State.sort_cars(sort_value: str): Sets sort for cars, reloads
- State.toggle_car_sort(): Reverses car sort order
- State.filter_cars(search_value: str): Filters cars by search string

Modified functions:
- State class (inherits rx.State): Adds car-related state vars (current_car, cars list, search/sort strings for cars)

Removed functions: None

[Classes]
Car model follows Customer pattern with Reflex model conventions.

New classes:
- Car model in backend/models.py: Inherits from rx.Model, marked as table=True, defines car fields with proper types

Modified classes: None

Removed classes: None

[Dependencies]
Existing faker dependency supports car data seeding.

No new dependencies required beyond existing faker package. Car seeding script will be added using faker to generate realistic car makes/models/versions/years/prices.

[Testing]
Seeding validates car CRUD operations during development.

Create seed_cars.py script using faker to populate initial car data in database. Test filtering/sorting with seeded data. Validate add/update/delete on sample cars.

[Implementation Order]
Step-by-step ordering minimizes database conflicts and ensures progressive integration.

1. Add Car model to backend/models.py
2. Run reflex db makemigrations to create Car table migration
3. Run reflex db migrate to apply migration
4. Extend State class in backend/backend.py with car-related variables and methods
5. Create sidebar navigation component in reflex_sales/views/sidebar.py
6. Create car inventory table component in reflex_sales/views/cars.py (similar to table.py but for cars)
7. Modify reflex_sales/reflex_sales.py: add sidebar to layouts, add /cars page, refactor current index to sales page
8. Update components (form_field if needed for car forms)
9. Create and run car seeding script for initial test data
10. Test full CRUD, search/sort, and navigation between pages
11. Final validation of reactive updates and database persistence
