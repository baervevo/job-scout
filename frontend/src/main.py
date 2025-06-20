from nicegui import ui


def main():
    ui.run(dark=True)


if __name__ in {"__main__", "__mp_main__"}:
    from src.pages.root import *
    from src.pages.login import *
    from src.pages.home import *
    from src.pages.resumes import *
    from src.pages.matches import *
    main()
