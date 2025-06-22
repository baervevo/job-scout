from typing import List
import asyncio
import logging

from nicegui import ui

from src.styles import PURPLE_BUTTON_SM
from src.utils.drawer import left_drawer
from src.api_client import api_client


@ui.page('/resumes')
def resumes_page():
    left_drawer()
    container = ui.grid(columns=6).classes('gap-4 p-4 w-full')
    uploader = ui.upload(
        label='Upload your resume',
        on_upload=lambda file: handle_upload(file, refresh_callback=refresh_resumes),
        auto_upload=True
    ).props('accept=.pdf,.doc,.docx').props('hide-upload-button').classes('hidden')

    def open_uploader():
        uploader.run_method('pickFiles')

    async def refresh_resumes():
        try:
            container.clear()
            with container:
                ui.label('Loading resumes...').classes('text-lg text-center')
            logging.info(f"Fetching resumes from API client at {api_client.base_url}")
            resumes = await api_client.get_resumes()
            container.clear()
            with container:
                if not resumes:
                    ui.label('No resumes found. Upload your first resume!').classes('text-lg text-center text-gray-500')
                    ui.button('Add New Resume', on_click=open_uploader).classes(f'{PURPLE_BUTTON_SM} mt-4 mx-auto')
                else:
                    for resume in resumes:
                        card = ui.card().tight().classes(
                            'w-full h-32 flex items-center justify-center shadow-lg border border-purple-200 dark:border-purple-800')
                        with card:
                            ui.label(f'{resume.id}. {resume.file_name}').classes(
                                'text-purple-800 dark:text-purple-200')
                            if not resume.keywords:
                                ui.label('Processing...').classes('text-sm text-yellow-500')
                            with ui.row().classes('mt-2'):
                                if resume.keywords:
                                    ui.icon('list', color='purple').on('click',
                                        lambda r=resume: show_string_list(r.keywords, "Keywords"))
                                else:
                                    ui.icon('list', color='gray').classes('opacity-50').tooltip('Keywords being processed...')
                                ui.icon('download', color='purple').on('click',
                                    lambda r=resume: download_resume(r.id))
                                ui.icon('delete', color='purple').on('click',
                                    lambda r=resume: delete_resume(r.id))
                    ui.button('Add New Resume', on_click=open_uploader).classes(f'{PURPLE_BUTTON_SM} mt-9 mx-auto h-8')
        except Exception as e:
            logging.error(f'Failed to fetch resumes: {str(e)}')
            container.clear()
            if hasattr(e, 'response') and e.response.status_code == 401:
                with container:
                    ui.label('Please log in first to view your resumes.').classes('text-red-500')
                    ui.button('Go to Login', on_click=lambda: ui.navigate.to('/login')).classes('mt-2')
            else:
                with container:
                    ui.label('Failed to load resumes. Please check your connection.').classes('text-red-500')
                    ui.button('Retry', on_click=lambda: ui.timer(0.1, refresh_resumes, once=True)).classes('mt-2')

    async def delete_resume(resume_id: int):
        try:
            await api_client.delete_resume(resume_id)
            await refresh_resumes()
            try:
                ui.notify('Resume deleted successfully', color='green')
            except Exception:
                logging.info('Resume deleted successfully (notification failed)')
        except Exception as e:
            logging.error(f'Failed to delete resume: {str(e)}')
            try:
                ui.notify('Failed to delete resume', color='red')
            except Exception:
                logging.error('Failed to delete resume (notification failed)')

    async def download_resume(resume_id: int):
        try:
            file_content = await api_client.download_resume(resume_id)
            try:
                ui.notify('Download functionality would be implemented here', color='blue')
            except Exception:
                logging.info('Download initiated (notification failed)')
        except Exception as e:
            logging.error(f'Failed to download resume: {str(e)}')
            try:
                ui.notify('Failed to download resume', color='red')
            except Exception:
                logging.error('Failed to download resume (notification failed)')
    global current_page_refresh
    current_page_refresh = refresh_resumes
    async def initial_load():
        try:
            await refresh_resumes()
        except Exception as e:
            logging.error(f'Initial load failed: {str(e)}')
            with container:
                ui.label('Failed to load resumes. Please log in first.').classes('text-red-500')
    ui.timer(0.1, initial_load, once=True)


def show_string_list(strings: List[str], title: str = "Keywords"):
    with ui.dialog().classes('w-full max-w-[90vw] h-[90vh]') as dialog, ui.card().classes('w-full h-full'):
        ui.label(title).classes('text-lg font-bold mb-4')
        with ui.scroll_area().classes('w-full h-[calc(100%-100px)] border rounded-lg'):
            with ui.column().classes('w-full p-2 space-y-2'):
                for i, text in enumerate(strings, 1):
                    ui.markdown(f"**{i}.** {text}").classes('text-md')
        ui.button('Close', on_click=dialog.close).classes('mt-4')
    dialog.open()

current_page_refresh = None

async def handle_upload(file, refresh_callback=None):
    """Handle file upload with proper error handling"""
    if not file:
        try:
            ui.notify('No file selected', color='red')
        except Exception:
            logging.error('Failed to show notification: No file selected')
        return

    try:
        try:
            ui.notify('Uploading resume...', color='blue')
        except Exception:
            logging.info('Upload started (notification failed)')

        # Use API client for upload
        result = await api_client.upload_resume(
            file_name=file.name,
            file_content=file.content.read(),
            file_type=file.type
        )
        
        if result.get('success'):
            try:
                ui.notify('Resume uploaded and queued for processing!', color='green')
            except Exception:
                logging.info('Upload successful (notification failed)')
            
            # Add a small delay to ensure database transaction is committed
            await asyncio.sleep(0.5)
            
            # Refresh the current page instead of navigating
            try:
                if refresh_callback:
                    await refresh_callback()
                elif current_page_refresh:
                    await current_page_refresh()
            except Exception as refresh_error:
                logging.error(f'Failed to refresh page after upload: {str(refresh_error)}')
                # If refresh fails, try again after a longer delay
                try:
                    await asyncio.sleep(1.0)
                    if refresh_callback:
                        await refresh_callback()
                    elif current_page_refresh:
                        await current_page_refresh()
                except Exception as retry_error:
                    logging.error(f'Failed to refresh page on retry: {str(retry_error)}')
        else:
            try:
                ui.notify('Upload failed', color='red')
            except Exception:
                logging.error('Upload failed (notification failed)')

    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response'):
            try:
                error_detail = e.response.json().get('detail', 'Unknown error')
                error_msg = f'Upload failed: {error_detail}'
            except:
                error_msg = f'Upload error: {str(e)}'
        
        try:
            ui.notify(error_msg, color='red')
        except Exception:
            logging.error(f'Upload error (notification failed): {error_msg}')
        
        logging.error(f'Upload error: {str(e)}')
