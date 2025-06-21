import httpx
from fastapi import Request
from nicegui import ui

from src.styles import PURPLE_BUTTON

API_URL = 'http://localhost:8000'


@ui.page('/login')
def login_page(request: Request):
    msg = request.query_params.get('msg')
    if msg:
        ui.notify(msg, color='green')

    with ui.row().classes('justify-center w-full mt-10'):
        ui.label('Resume Matcher').classes('text-5xl font-bold text-purple-800 dark:text-purple-200 mb-4')

    with ui.column().classes('absolute-center items-center w-64 h-96'):
        ui.label('Login').classes('text-2xl font-bold text-purple-800 dark:text-purple-200 mb-4')
        username_input = ui.input('Username').classes('w-full mb-4')
        password_input = ui.input('Password', password=True).classes('w-full mb-4')
        ui.button('Login', on_click=lambda: handle_login(username_input.value, password_input.value)).classes(
            f'{PURPLE_BUTTON} w-full')
        ui.link(f'Register', '/register').classes('text-purple-400 no-underline')


async def handle_login(username, password):
    if not username or not password:
        ui.notify('All fields are required!', color='red')
        return
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f'{API_URL}/auth/login',
                json={
                    'username': username,
                    'password': password
                })
            response.raise_for_status()
            ui.notify('Login successful!', color='green')
            ui.navigate.to('/home')
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Unknown error")
            ui.notify(f'Login failed: {error_detail}', color='red')
