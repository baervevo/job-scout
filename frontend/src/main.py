from nicegui import ui
from config import settings


def main():
    ui.run(
        host=settings.FRONTEND_HOST,
        port=settings.FRONTEND_PORT,
        dark=True
    )


if __name__ in {"__main__", "__mp_main__"}:
    from src.pages.root import *
    from src.pages.login import *
    from src.pages.home import *
    from src.pages.resumes import *
    from src.pages.matches import *
    from src.pages.register import *
    main()
