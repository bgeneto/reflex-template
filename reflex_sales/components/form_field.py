import reflex as rx


def form_field(
    label: str,
    placeholder: str,
    type: str,
    name: str,
    icon: str,
    default_value: str = "",
    required: bool = True,
    on_change=None,
    server_error: str = "",
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.hstack(
                rx.icon(icon, size=16, stroke_width=1.5),
                rx.hstack(
                    rx.form.label(label),
                    (
                        rx.text("*", color="red", size="2", weight="bold")
                        if required
                        else rx.fragment()
                    ),
                    spacing="1",
                ),
                align="center",
                spacing="2",
            ),
            rx.form.control(
                rx.input(
                    placeholder=placeholder,
                    type=type,
                    default_value=default_value,
                    required=required,
                    on_change=on_change,
                ),
                as_child=True,
            ),
            # Client-side HTML5 validation messages
            rx.form.message(
                f"{label} is required",
                match="valueMissing",
                color="red",
                size="1",
            ),
            rx.form.message(
                f"Please enter a valid {label.lower()}",
                match="typeMismatch",
                color="red",
                size="1",
            ),
            rx.form.message(
                f"{label} must be a valid number",
                match="badInput",
                color="red",
                size="1",
            ),
            # Server-side validation error
            rx.cond(
                server_error != "",
                rx.text(
                    server_error,
                    color="red",
                    size="1",
                ),
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )
