from nicegui import ui

from src.styles import PURPLE_BUTTON


@ui.page('/login')
def login_page():
    with ui.column().classes('absolute-center items-center w-64'):
        ui.label('Login Page').classes('text-2xl font-bold text-purple-800 dark:text-purple-200 mb-4')
        ui.input('Username').classes('w-full mb-4')
        ui.input('Password').classes('w-full mb-4')
        ui.button('Login', on_click=lambda: ui.navigate.to('/home')) \
            .classes(f'{PURPLE_BUTTON} w-full')

