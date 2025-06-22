from typing import List
import asyncio
import logging
import base64

from nicegui import ui

from src.styles import PURPLE_BUTTON_SM
from src.utils.drawer import left_drawer
from src.api_client import api_client


@ui.page('/resumes')
def resumes_page():
    left_drawer()
    container = ui.grid(columns=6).classes('gap-4 p-4 w-full')
    
    # Location and radius inputs (initially hidden)
    location_input = ui.input('Job Location (e.g., "New York, NY" or "Remote")').classes('w-full mb-2').style('display: none')
    radius_input = ui.number('Search Radius (km)', value=50, min=1, max=500).classes('w-full mb-2').style('display: none')
    
    uploader = ui.upload(
        label='Upload your resume',
        on_upload=lambda file: handle_upload(file, location_input.value, radius_input.value, refresh_callback=refresh_resumes),
        auto_upload=True
    ).props('accept=.pdf,.doc,.docx').props('hide-upload-button').classes('hidden')

    def open_uploader():
        # Show location and radius inputs in a dialog first
        with ui.dialog().classes('w-96') as dialog, ui.card():
            ui.label('Job Search Preferences').classes('text-lg font-bold mb-4')
            
            location_dialog_input = ui.input('Preferred Job Location').classes('w-full mb-4').props('placeholder="e.g., New York, NY or Remote"')
            radius_dialog_input = ui.number('Search Radius (km)', value=50, min=1, max=500).classes('w-full mb-4')
            
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500')
                def proceed_with_upload():
                    location_input.value = location_dialog_input.value
                    radius_input.value = radius_dialog_input.value
                    dialog.close()
                    uploader.run_method('pickFiles')
                ui.button('Continue', on_click=proceed_with_upload).classes(PURPLE_BUTTON_SM)
        
        dialog.open()

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
                            'w-full h-40 flex items-center justify-center shadow-lg border border-purple-200 dark:border-purple-800')
                        with card:
                            with ui.column().classes('w-full p-4'):
                                ui.label(f'{resume.id}. {resume.file_name}').classes(
                                    'text-purple-800 dark:text-purple-200 truncate max-w-full font-semibold')
                                
                                # Location and radius info
                                if resume.location or resume.radius:
                                    location_text = resume.location or "Any location"
                                    radius_text = f" ({resume.radius}km radius)" if resume.radius else ""
                                    ui.label(f"📍 {location_text}{radius_text}").classes('text-sm text-gray-600 dark:text-gray-400')
                                
                                if not resume.keywords:
                                    ui.label('Processing...').classes('text-sm text-yellow-500')
                                
                                with ui.row().classes('mt-2 justify-center'):
                                    if resume.keywords:
                                        ui.icon('list', color='purple').on('click',
                                            lambda r=resume: show_string_list(r.keywords, "Keywords")).classes('cursor-pointer')
                                    else:
                                        ui.icon('list', color='gray').classes('opacity-50').tooltip('Keywords being processed...')
                                    ui.icon('download', color='purple').on('click',
                                        lambda r=resume: download_resume(r.id)).classes('cursor-pointer')
                                    ui.icon('delete', color='purple').on('click',
                                        lambda r=resume: delete_resume(r.id)).classes('cursor-pointer')
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
            resumes = await api_client.get_resumes()
            resume = next((r for r in resumes if r.id == resume_id), None)
            if not resume:
                try:
                    ui.notify('Resume not found', color='red')
                except Exception:
                    logging.error('Resume not found (notification failed)')
                return
            try:
                ui.notify('Downloading resume...', color='blue')
            except Exception:
                logging.info('Download started (notification failed)')
            file_content = await api_client.download_resume(resume_id)
            file_b64 = base64.b64encode(file_content).decode()
            filename = resume.file_name
            mime_type = 'application/pdf' if filename.lower().endswith('.pdf') else 'application/octet-stream'
            ui.download(file_content, filename)
            try:
                ui.notify(f'Downloaded {filename} successfully', color='green')
            except Exception:
                logging.info(f'Download successful: {filename} (notification failed)')
                
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

async def handle_upload(file, location, radius, refresh_callback=None):
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
            file_type=file.type,
            location=location,  # Include location in the upload
            radius=radius       # Include radius in the upload
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
