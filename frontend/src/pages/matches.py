from nicegui import ui

from src.mock_data import listings, matches
from src.utils.drawer import left_drawer


@ui.page('/matches')
def matches_page():
    left_drawer()
    with ui.column():
        for i in range(len(matches)):
            create_match_card(i)


def create_match_card(i: int):
    card = ui.card().tight().classes('cursor-pointer hover:bg-gray-100 relative z-10')
    card.on("click", lambda index=i: open_match_details(index))
    with card:
        with ui.column():
            with ui.row():
                ui.label(f'{matches[i].cosine_similarity * 100:.0f}%')
                with ui.column():
                    ui.label(f'{listings[i].title}')
                    with ui.row():
                        ui.label(f'{listings[i].company}')
                        ui.label(f'{listings[i].location}')

                if listings[i].salary_min is not None and listings[i].salary_max is not None:
                    salary = f"{listings[i].currency} {listings[i].salary_min} - {listings[i].salary_max}"
                else:
                    salary = "Salary not specified"
                ui.label(f'{salary}')
            with ui.row().classes('flex-wrap gap-2'):
                for kw in matches[i].missing_keywords:
                    ui.chip(kw)


def open_match_details(i: int):
    with ui.dialog().classes('w-full max-w-[90vw] h-[90vh]') as dialog, ui.card().classes('w-full h-full'):
        ui.link(f'{listings[i].title} at {listings[i].company}', listings[i].link, new_tab=True)
        ui.label(f'Match Details').classes('text-lg font-bold mb-2')
        ui.label(f"Cosine Similarity: {matches[i].cosine_similarity * 100:.2f}%")
        with ui.grid(columns=4):
            for kw in matches[i].missing_keywords:
                ui.chip(kw) # highlight
            fullfilled_keywords = set(listings[i].keywords) - set(matches[i].missing_keywords)
            for kw in fullfilled_keywords:
                ui.chip(kw).classes('text-sm text-gray-700')
        ui.label(f"Summary: {matches[i].summary}")
        ui.space()
        ui.label(f"Resume ID: {matches[i].resume_id}").classes('text-sm text-gray-500')
        ui.label(f"Listing ID: {matches[i].listing_id}").classes('text-sm text-gray-500')
        ui.label(f"Updated At: {listings[i].updated_at.strftime('%Y-%m-%d %H:%M:%S') if listings[i].created_at else 'N/A'}").classes('text-sm text-gray-500')
        ui.button('Close', on_click=dialog.close).classes('mt-4')
    dialog.open()
