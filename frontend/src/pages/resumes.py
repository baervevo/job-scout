from typing import Dict, List

from nicegui import ui

from src.mock_data import resumes, sample_kw_list, path_pdf
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.styles import PURPLE_BUTTON_SM
from src.utils.drawer import left_drawer


@ui.page('/resumes')
def resumes_page():
    left_drawer()

    container = ui.grid(columns=6).classes('gap-4 p-4 w-full')

    def refresh_resumes():
        container.clear()
        for resume in resumes:
            with container:
                card = ui.card().tight().classes(
                    'w-full h-32 flex items-center justify-center shadow-lg border border-purple-200 dark:border-purple-800')
                with card:
                    ui.label(f'{resume.internal_id}. {resume.file_name}').classes('text-purple-800 dark:text-purple-200')
                    with ui.row().classes('mt-2'):
                        ui.icon('list', color='purple').on('click', lambda: show_string_list(sample_kw_list))
                        ui.icon('picture_as_pdf', color='purple').on('click', show_pdf)
                        ui.icon('delete', color='purple').on('click', lambda r=resume: delete_resume(r))
        with container:
            ui.button('Add New Resume', on_click=add_resume).classes(f'{PURPLE_BUTTON_SM} mt-9 mx-auto h-8')

    def delete_resume(resume: ResumeKeywordData):
        resumes.remove(resume)
        refresh_resumes()
        ui.notify(f'Deleted resume: {resume.file_name}', color='purple')

    refresh_resumes()


def add_resume():
    ui.notify('Add Resume button clicked!')


def show_pdf():
    with ui.dialog().classes('w-full max-w-[90vw] h-[90vh]') as dialog, ui.card().classes('w-full h-full'):
        ui.label("Resume Preview").classes('text-lg font-bold mb-2')
        ui.html(
            f'<embed src="{path_pdf}" type="application/pdf" width="100%" height="100%">'
        ).classes('w-full h-[calc(100%-50px)]')
        ui.button('Close', on_click=dialog.close).classes('mt-4')
    dialog.open()


def show_string_list(strings: List[str], title: str = "Keywords"):
    with ui.dialog().classes('w-full max-w-[90vw] h-[90vh]') as dialog, ui.card().classes('w-full h-full'):
        ui.label(title).classes('text-lg font-bold mb-4')
        with ui.scroll_area().classes('w-full h-[calc(100%-100px)] border rounded-lg'):
            with ui.column().classes('w-full p-2 space-y-2'):
                for i, text in enumerate(strings, 1):
                    ui.markdown(f"**{i}.** {text}").classes('text-md')
        ui.button('Close', on_click=dialog.close).classes('mt-4')
    dialog.open()
