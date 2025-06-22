import asyncio
import logging

import httpx
from nicegui import ui

from src.styles import PAGE_BUTTON

API_URL = 'http://localhost:8000'


def left_drawer():
    with ui.left_drawer(top_corner=True, bottom_corner=True).classes('bg-purple-700'):
        ui.label('RESUME MATCHER').classes('text-white text-xl font-bold p-4')

        ui.button('Home', on_click=lambda: ui.navigate.to('/home')).classes(PAGE_BUTTON).props('flat align=left')
        ui.button('Resumes', on_click=lambda: ui.navigate.to('/resumes')).classes(PAGE_BUTTON).props('flat align=left')
        ui.button('Matches', on_click=lambda: ui.navigate.to('/matches')).classes(PAGE_BUTTON).props('flat align=left')
        ui.space()
        ui.button('Logout', on_click=handle_logout).classes(PAGE_BUTTON).props('flat align=left')


async def handle_logout():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{API_URL}/auth/logout')
            response.raise_for_status()
        except Exception as e:
            logging.error(f'Logout error: {str(e)}')
    logging.info('Successfully logged out')
    ui.navigate.to('/login')