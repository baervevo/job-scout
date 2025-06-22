import asyncio
import logging

from nicegui import ui

from src.styles import PAGE_BUTTON
from src.api_client import api_client


def left_drawer():
    with ui.left_drawer(top_corner=True, bottom_corner=True).classes('bg-purple-700'):
        ui.label('RESUME MATCHER').classes('text-white text-xl font-bold p-4')

        ui.button('Home', on_click=lambda: ui.navigate.to('/home')).classes(PAGE_BUTTON).props('flat align=left')
        ui.button('Resumes', on_click=lambda: ui.navigate.to('/resumes')).classes(PAGE_BUTTON).props('flat align=left')
        ui.button('Matches', on_click=lambda: ui.navigate.to('/matches')).classes(PAGE_BUTTON).props('flat align=left')
        ui.space()
        ui.button('Logout', on_click=handle_logout).classes(PAGE_BUTTON).props('flat align=left')


async def handle_logout():
    try:
        await api_client.logout()
        logging.info('Successfully logged out')
        ui.navigate.to('/login')
    except Exception as e:
        logging.error(f'Logout error: {str(e)}')
        # Even if logout fails on backend, redirect to login
        ui.navigate.to('/login')