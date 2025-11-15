import reflex as rx

from ..backend.backend import Car, State
from ..components.form_field import form_field


def _header_cell(text: str, icon: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )


def _show_car(car: Car):
    """Show a car in a table row."""
    return rx.table.row(
        rx.table.row_header_cell(car.make),
        rx.table.cell(car.model),
        rx.table.cell(car.version),
        rx.table.cell(car.year),
        rx.table.cell(f"${car.price:,}"),
        rx.table.cell(
            rx.hstack(
                _update_car_dialog(car),
                _delete_car_dialog(car),
                min_width="max-content",
            )
        ),
        style={"_hover": {"bg": rx.color("accent", 2)}},
        align="center",
    )


def _add_car_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=26),
                rx.text("Add Car", size="4", display=["none", "none", "block"]),
                size="3",
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="car", size=34),
                    color_scheme="blue",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Add New Car",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Fill the form with the car's info",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5em",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        rx.hstack(
                            # Make
                            form_field(
                                "Make",
                                "Toyota",
                                "text",
                                "make",
                                "factory",
                                server_error=State.car_errors.get("make", ""),
                            ),
                            # Model
                            form_field(
                                "Model",
                                "Camry",
                                "text",
                                "model",
                                "car",
                                server_error=State.car_errors.get("model", ""),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.hstack(
                            # Version
                            form_field(
                                "Version",
                                "LE",
                                "text",
                                "version",
                                "settings",
                                server_error=State.car_errors.get("version", ""),
                            ),
                            # Year
                            form_field(
                                "Year",
                                "2023",
                                "number",
                                "year",
                                "calendar",
                                server_error=State.car_errors.get("year", ""),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        # Price
                        form_field(
                            "Price",
                            "25000",
                            "number",
                            "price",
                            "dollar-sign",
                            server_error=State.car_errors.get("price", ""),
                        ),
                        width="100%",
                        direction="column",
                        spacing="3",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.button(
                            "Submit Car",
                            type="submit",
                        ),
                        padding_top="2em",
                        spacing="3",
                        mt="4",
                        justify="end",
                    ),
                    on_submit=State.add_car_to_db,
                    reset_on_submit=True,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            width="100%",
            max_width="450px",
            justify=["end", "end", "start"],
            padding="1.5em",
            border=f"2.5px solid {rx.color('accent', 7)}",
            border_radius="25px",
        ),
    )


def _update_car_dialog(car):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon("square-pen", size=22),
                color_scheme="green",
                size="2",
                variant="solid",
                on_click=lambda: State.get_car(car),
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="square-pen", size=34),
                    color_scheme="blue",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Edit Car",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Edit the car's info",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5em",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        rx.hstack(
                            # Make
                            form_field(
                                "Make",
                                "Toyota",
                                "text",
                                "make",
                                "factory",
                                car.make,
                            ),
                            # Model
                            form_field(
                                "Model",
                                "Camry",
                                "text",
                                "model",
                                "car",
                                car.model,
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.hstack(
                            # Version
                            form_field(
                                "Version",
                                "LE",
                                "text",
                                "version",
                                "settings",
                                car.version,
                            ),
                            # Year
                            form_field(
                                "Year",
                                "2023",
                                "number",
                                "year",
                                "calendar",
                                car.year.to(str),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        # Price
                        form_field(
                            "Price",
                            "25000",
                            "number",
                            "price",
                            "dollar-sign",
                            car.price.to(str),
                        ),
                        direction="column",
                        spacing="3",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button("Update Car"),
                            ),
                            as_child=True,
                        ),
                        padding_top="2em",
                        spacing="3",
                        mt="4",
                        justify="end",
                    ),
                    on_submit=State.update_car_to_db,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            max_width="450px",
            padding="1.5em",
            border=f"2px solid {rx.color('accent', 7)}",
            border_radius="25px",
        ),
    )


def _delete_car_dialog(car):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon("trash-2", size=22),
                color_scheme="red",
                size="2",
                variant="solid",
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="triangle_alert", size=34),
                    color_scheme="red",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Delete Car",
                        weight="bold",
                        margin="0",
                        color="red",
                    ),
                    rx.dialog.description(
                        f"Are you sure you want to delete '{car.year} {car.make} {car.model}'? This action cannot be undone.",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5em",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Delete Car",
                        color_scheme="red",
                        on_click=lambda: State.delete_car(car.id),
                    ),
                ),
                padding_top="2em",
                spacing="3",
                mt="4",
                justify="end",
            ),
            max_width="400px",
            padding="1.5em",
            border=f"2px solid {rx.color('red', 6)}",
            border_radius="25px",
        ),
    )


def cars_table():
    return rx.fragment(
        rx.flex(
            _add_car_button(),
            rx.spacer(),
            rx.cond(
                State.sort_car_reverse,
                rx.icon(
                    "arrow-down-z-a",
                    size=28,
                    stroke_width=1.5,
                    cursor="pointer",
                    on_click=State.toggle_car_sort,
                ),
                rx.icon(
                    "arrow-down-a-z",
                    size=28,
                    stroke_width=1.5,
                    cursor="pointer",
                    on_click=State.toggle_car_sort,
                ),
            ),
            rx.select(
                [
                    "make",
                    "model",
                    "version",
                    "year",
                    "price",
                ],
                placeholder="Sort By: Make",
                size="3",
                on_change=lambda sort_value: State.sort_car_values(sort_value),
            ),
            rx.input(
                rx.input.slot(rx.icon("search")),
                placeholder="Search here...",
                size="3",
                min_width="225px",
                width="225px",
                variant="surface",
                on_change=lambda value: State.filter_car_values(value),
            ),
            justify="end",
            align="center",
            spacing="3",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
            overflow_x="auto",
            min_width="0",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Make", "factory"),
                    _header_cell("Model", "car"),
                    _header_cell("Version", "settings"),
                    _header_cell("Year", "calendar"),
                    _header_cell("Price", "dollar-sign"),
                    _header_cell("Actions", "cog"),
                ),
            ),
            rx.table.body(rx.foreach(State.cars, _show_car)),
            variant="surface",
            size="3",
            width="100%",
            overflow_x="auto",
        ),
    )
