# Reflex Sales App - Copilot Instructions

## Architecture Overview

This is a **Reflex-based full-stack web application** that generates personalized sales emails using OpenAI. The architecture is strictly layered:

- **`reflex_sales/backend/backend.py`**: Centralized `State` class managing all business logic (customer CRUD, OpenAI integration, filtering/sorting)
- **`reflex_sales/backend/models.py`**: SQLModel-based `Customer` model for database persistence
- **`reflex_sales/views/`**: Reusable view components (navbar, table, email generator) - these are **UI only**, never contain state logic
- **`reflex_sales/components/`**: Primitive reusable UI components (form_field, gender_badge) - purely presentational

**Data Flow**: Database ↔ State ↔ Views (unidirectional). State drives all reactive updates.

## Key Patterns

### State Management
- Single `State` class in `backend.py` is the source of truth for all application data
- Use `@rx.event` decorators for state mutations
- Background events use `@rx.event(background=True)` for async operations (like OpenAI calls) with `async with self:` locks
- Direct database access via `rx.session()` context manager using SQLModel queries

### Database Operations
- All queries use SQLModel's `select()` with `session.exec()`
- Filter operations: convert search input to lowercase patterns (`f"%{str(value).lower()}%"`) for case-insensitive `ilike()` matching
- Sorting: use `asc()`/`desc()` for ascending/descending; for strings use `func.lower(sort_column)` for case-insensitive sorting
- Always check for duplicate emails before adding customers: `session.exec(select(Customer).where(Customer.email == ...)).first()`

### OpenAI Integration
- Client initialized lazily in `get_openai_client()` with module-level caching (`_client` global)
- Uses `chat.completions.create()` with `stream=True` for streaming responses
- System prompt defines Reflex as the company selling predefined products in `products` dict
- Stream processing: check `hasattr(item.choices[0].delta, "content")` before accessing response text

### Form Validation Pattern (CRITICAL)
**This project uses Pydantic server-side validation as the authoritative validation layer.**

#### Validation Architecture
1. **Pydantic Models**: All validation rules live in `models.py` using `@field_validator` decorators
2. **State Error Tracking**: State class maintains `{model}_errors: dict[str, str]` for each form (e.g., `customer_errors`, `car_errors`)
3. **Error Mapping**: Use `_map_pydantic_errors(exc: ValidationError) -> dict[str, str]` to convert Pydantic errors to field->message dict
4. **UI Display**: Form fields accept `server_error` parameter to display validation errors below the field

#### Implementation Contract
```python
# backend.py - State class
class State(rx.State):
    # Error state for each form
    customer_errors: dict[str, str] = {}
    car_errors: dict[str, str] = {}

    def _map_pydantic_errors(self, exc: ValidationError) -> dict[str, str]:
        """Convert Pydantic ValidationError to field->message dict."""
        errors = {}
        for err in exc.errors():
            field = err["loc"][0] if err["loc"] else "field"
            errors[str(field)] = err["msg"]
        return errors

    def add_entity_to_db(self, form_data: dict):
        # Clear previous errors
        self.entity_errors = {}

        try:
            # Type conversion BEFORE Pydantic validation
            form_data["numeric_field"] = int(form_data.get("numeric_field", 0))

            # Let Pydantic validate via model instantiation
            entity = EntityModel(**form_data)

            # Database operations...
            return rx.toast.success("Success message")

        except ValidationError as e:
            self.entity_errors = self._map_pydantic_errors(e)
            first_error = next(iter(self.entity_errors.values()), "Validation failed")
            return rx.toast.error(first_error, position="bottom-right")
        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}", position="bottom-right")
```

```python
# models.py - Validation rules
from pydantic import field_validator

class Entity(rx.Model, table=True):
    field_name: str

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field name is required")
        if len(v.strip()) < 2:
            raise ValueError("Field name must be at least 2 characters")
        return v.strip()
```

```python
# views/form.py - UI integration
form_field(
    "Field Name",
    "Placeholder",
    "text",
    "field_name",
    "icon-name",
    server_error=State.entity_errors.get("field_name", ""),
)
```

#### Validation Rules
- **Client-side**: HTML5 validation with `required` attribute prevents empty submission
- **Server-side**: Pydantic validates ALL constraints (format, length, range, custom logic)
- **Error Display**: Combination of `rx.form.message` for HTML5 validation + `server_error` for Pydantic errors
- **Toast Notifications**: Show first error on validation failure, success message on save
- **No Duplicate Logic**: All validation rules exist ONLY in Pydantic model validators

#### Form Field Component Contract
```python
def form_field(
    label: str,
    placeholder: str,
    type: str,
    name: str,
    icon: str,
    default_value: str = "",
    required: bool = True,
    on_change=None,
    server_error: str = "",  # REQUIRED: Pass State.errors.get(field_name, "")
) -> rx.Component:
```

### View Component Pattern
- Views are **pure functions returning `rx.Component`** with NO internal state
- Bind state directly: `State.current_user.customer_name` renders reactively
- Use `on_click=State.method_name(arg)` syntax to trigger state methods
- Conditional rendering: `rx.cond(condition, component_if_true, component_if_false)`
- **Always pass server validation errors** to form fields via `server_error` parameter

### Responsive Design
- Use list-based breakpoints: `width=["100%", "100%", "100%", "60%"]` = `[mobile, tablet, laptop, desktop]`
- Flex direction changes: `flex_direction=["column", "column", "column", "row"]`
- All major components use Radix UI primitives via Reflex's high-level API

## Development Workflow

### Environment Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your-key
reflex db init
```

### Database Migrations
After modifying `Customer` model:
```bash
reflex db makemigrations --message "Brief description"
reflex db migrate
```

### Running the App
```bash
reflex run
```
Launches at `http://localhost:3000`

### Testing Changes
- Reflex hot-reloads on file saves
- Database persists in SQLite (default) unless configured otherwise
- Test state changes by triggering buttons; check browser console for errors

## Common Implementation Tasks

**Adding a new field to Customer**:
1. Add field to `Customer` model in `models.py`
2. Add `@field_validator` with validation rules (required, format, range, etc.)
3. Add form field in view using `form_field()` helper with `server_error=State.customer_errors.get("field_name", "")`
4. Update state methods that create/update customers
5. Ensure type conversion happens before Pydantic validation in state methods

**Adding a new form/model**:
1. Create model in `models.py` with Pydantic `@field_validator` decorators
2. Add `{model}_errors: dict[str, str] = {}` to State class
3. Create add/update methods in State that:
   - Clear errors: `self.model_errors = {}`
   - Convert types before validation
   - Catch `ValidationError` and map with `_map_pydantic_errors()`
   - Return appropriate toasts
4. Create view with form fields passing `server_error` from state
5. Bind form `on_submit` to State method

**Extending OpenAI integration**:
- Modify system prompt in `State.call_openai()` method
- Update `products` dict to change available items for recommendations

**New filtering/sorting**:
- Add state variable for the filter/sort criteria
- Update `load_entries()` query with new conditions
- Bind UI control to state setter method

## Key Dependencies
- **reflex 0.7.13+**: React-like Python framework with automatic frontend/backend routing
- **openai 1+**: Official OpenAI Python client for GPT access
- **sqlmodel**: SQLAlchemy + Pydantic for ORM and validation
- **faker**: Used for test data generation (optional utility)

## File Organization
- All URLs in Radix (Reflex components) go through `reflex_sales.py`'s `app.add_page()` - currently single-page app
- Alembic migrations in `alembic/versions/` managed by Reflex CLI commands
