import logging

from nicegui import ui

from src.styles import PURPLE_BUTTON
from src.api_client import api_client


@ui.page('/register')
def register_page():
    with ui.row().classes('justify-center w-full mt-10'):
        ui.label('JobScout').classes('text-5xl font-bold text-purple-800 dark:text-purple-200 mb-4')

    with ui.column().classes('absolute-center items-center w-64 h-96'):
        ui.label('Register').classes('text-2xl font-bold text-purple-800 dark:text-purple-200 mb-4')
        username_input = ui.input('Username').classes('w-full mb-4')
        password_input = ui.input('Password', password=True).classes('w-full mb-4')
        rep_password_input = ui.input('Repeat password', password=True).classes('w-full mb-4')
        ui.button('Register', on_click=lambda: handle_register(username_input.value, password_input.value,
                                                               rep_password_input.value)).classes(
            f'{PURPLE_BUTTON} w-full')
        ui.link('Back to login page', '/login').classes('text-purple-400 no-underline')


async def handle_register(username, password, rep_password):
    if not username or not password or not rep_password:
        ui.notify('All fields are required!', color='red')
        return
    if password != rep_password:
        ui.notify("Passwords do not match!", color='red')
        return

    try:
        result = await api_client.register(username, password)
        if result.get('success'):
            ui.navigate.to('/login?msg=Registration%20successful')
        else:
            ui.notify('Registration failed', color='red')
    except Exception as e:
        error_msg = 'Registration failed'
        if hasattr(e, 'response'):
            try:
                error_detail = e.response.json().get('detail', 'Unknown error')
                error_msg = f'Registration failed: {error_detail}'
            except:
                pass
        ui.notify(error_msg, color='red')
        logging.error(f'Registration error: {str(e)}')
