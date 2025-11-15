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

### View Component Pattern
- Views are **pure functions returning `rx.Component`** with NO internal state
- Bind state directly: `State.current_user.customer_name` renders reactively
- Use `on_click=State.method_name(arg)` syntax to trigger state methods
- Conditional rendering: `rx.cond(condition, component_if_true, component_if_false)`

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
2. Add form field in table view using `form_field()` helper
3. Update state methods that create/update customers

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
