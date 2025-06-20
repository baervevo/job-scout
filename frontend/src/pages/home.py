from nicegui import ui

from src.styles import PURPLE_BUTTON
from src.utils.drawer import left_drawer


@ui.page('/home')
def home_page():
    left_drawer()
    with ui.column().classes('p-4'):
        ui.label('Welcome to Resume Manager').classes('text-2xl font-bold text-purple-800 dark:text-purple-200')
        ui.button('Go to Resumes', on_click=lambda: ui.navigate.to('/resumes')) \
            .classes(PURPLE_BUTTON)