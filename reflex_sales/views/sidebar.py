import reflex as rx


def sidebar_link(text: str, url: str, icon: str):
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="4", weight="medium"),
            width="100%",
            padding="2",
            border_radius="md",
            _hover={
                "bg": rx.color("gray", 3),
                "color": rx.color("gray", 11),
            },
            align="center",
        ),
        href=url,
        width="100%",
    )


def sidebar():
    return rx.box(
        rx.vstack(
            rx.heading(
                "Sales Dashboard",
                size="6",
                margin_bottom="1rem",
                padding_left="1rem",
            ),
            rx.vstack(
                sidebar_link("Personalized Sales", "/sales", "users"),
                sidebar_link("Cars Inventory", "/cars", "car"),
                width="100%",
                spacing="1",
                align="start",
            ),
            height="100vh",
            padding="1.5rem",
            background=rx.color("gray", 2),
            border_right=f"1px solid {rx.color('gray', 5)}",
        ),
        display=["none", "none", "block"],  # Hide on mobile/tablet
        width="250px",
        position="fixed",
        left=0,
        top=0,
    )
