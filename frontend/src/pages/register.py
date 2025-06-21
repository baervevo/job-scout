import httpx
from nicegui import ui

from src.styles import PURPLE_BUTTON

API_URL = 'http://localhost:8000'


@ui.page('/register')
def register_page():
    with ui.row().classes('justify-center w-full mt-10'):
        ui.label('Resume Matcher').classes('text-5xl font-bold text-purple-800 dark:text-purple-200 mb-4')

    with ui.column().classes('absolute-center items-center w-64 h-96'):
        ui.label('Register').classes('text-2xl font-bold text-purple-800 dark:text-purple-200 mb-4')
        username_input = ui.input('Username').classes('w-full mb-4')
        password_input = ui.input('Password', password=True).classes('w-full mb-4')
        rep_password_input = ui.input('Repeat password', password=True).classes('w-full mb-4')
        ui.button('Register', on_click=lambda: handle_register(username_input.value, password_input.value,
                                                               rep_password_input.value)).classes(
            f'{PURPLE_BUTTON} w-full')
        ui.link(f'Back to login page', '/login').classes('text-purple-400 no-underline')


async def handle_register(username, password, rep_password):
    if not username or not password or not rep_password:
        ui.notify('All fields are required!', color='red')
        return
    if not check_password_match(password, rep_password):
        return
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_URL}/auth/register',
                json={'username': username, 'password': password}
            )

        if response.status_code == 200:
            await ui.navigate.to('/login?msg=Registration%20successful')
        else:
            detail = response.json().get('detail', 'Unknown error')
            ui.notify(f'Registration failed: {detail}', color='red')

    except Exception as e:
        ui.notify(f'Error: {str(e)}', color='red')


def check_password_match(password: str, rep_password: str) -> bool:
    if password != rep_password:
        ui.notify('Passwords do not match!', color='red')
        return False
    return True
