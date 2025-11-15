import reflex as rx

from .backend.backend import State
from .views.cars import cars_table
from .views.email import email_gen_ui
from .views.sidebar import sidebar
from .views.table import main_table


def sales_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.vstack(
            rx.heading("Personalized Sales", size="8", margin_bottom="1rem"),
            rx.flex(
                rx.box(main_table(), width=["100%", "100%", "100%", "60%"]),
                email_gen_ui(),
                spacing="6",
                width="100%",
                flex_direction=["column", "column", "column", "row"],
            ),
            height="100vh",
            bg=rx.color("accent", 1),
            max_width="calc(100vw - 250px)",
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
            padding_y=["1em", "1em", "2em"],
            margin_left=["0px", "0px", "250px"],
        ),
        width="100%",
        overflow_x="hidden",
    )


def cars_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.vstack(
            rx.heading("Cars Inventory Management", size="8", margin_bottom="1rem"),
            rx.box(cars_table(), width="100%", overflow_x="auto"),
            height="100vh",
            bg=rx.color("accent", 1),
            max_width="calc(100vw - 250px)",
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
            padding_y=["1em", "1em", "2em"],
            margin_left=["0px", "0px", "250px"],
        ),
        width="100%",
        overflow_x="hidden",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="blue"
    ),
)
app.add_page(
    sales_page,
    route="/",
    on_load=[State.load_entries, State.load_cars_entries],
    title="Sales App",
    description="Generate personalized sales emails.",
)
app.add_page(
    sales_page,
    route="/sales",
    on_load=[State.load_entries, State.load_cars_entries],
    title="Sales App",
    description="Generate personalized sales emails.",
)
app.add_page(
    cars_page,
    route="/cars",
    on_load=State.load_cars_entries,
    title="Cars Inventory",
    description="Manage cars inventory.",
)
