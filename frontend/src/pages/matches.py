import colorsys
import asyncio
import logging
from typing import List

from nicegui import ui

from src.styles import PURPLE_BUTTON
from src.utils.drawer import left_drawer
from src.api_client import api_client
from src.models import Match, ListingKeywordData


@ui.page('/matches')
def matches_page():
    left_drawer()
    
    container = ui.column().classes('w-full p-4')
    
    async def load_matches():
        """Load matches from the API"""
        try:
            # Show loading message
            container.clear()
            with container:
                ui.label('Loading matches...').classes('text-lg')
            
            # Fetch matches from API
            matches_data = await api_client.get_matches()
            
            # Clear loading message and display results
            container.clear()
            
            with container:
                if not matches_data:
                    ui.label('No matches found. Upload a resume to start finding job matches!').classes('text-lg text-center')
                    return
                
                # Display matches
                ui.label(f'Found {len(matches_data)} job matches').classes('text-2xl font-bold mb-4')
                
                for match_data in matches_data:
                    create_match_card(match_data, container)
                    
        except Exception as e:
            container.clear()
            with container:
                ui.label(f'Error loading matches: {str(e)}').classes('text-red-500 text-lg')
                ui.button('Retry', on_click=lambda: ui.timer(0.1, load_matches, once=True)).classes(PURPLE_BUTTON)
            logging.error(f'Error loading matches: {str(e)}')
    
    # Initial load using timer for proper context
    ui.timer(0.1, load_matches, once=True)


def create_match_card(match_data: dict, parent_container):
    """Create a match card from API data"""
    match_info = match_data
    listing_info = match_data.get('listing', {})
    
    if not listing_info:
        return  # Skip if no listing data
    
    with parent_container:
        card = ui.card().tight().classes('w-full cursor-pointer hover:bg-gray-800 relative z-10 mb-4')
        card.on("click", lambda: open_match_details(match_data))
        
        with card:
            with ui.column().classes('p-4'):
                # Top row with similarity score and job info
                with ui.row().classes('w-full items-start justify-between'):
                    # Left side: Similarity score and job details
                    with ui.row().classes('items-center flex-1'):
                        # Similarity score
                        similarity = match_info.get('cosine_similarity', 0)
                        color = interpolate_color(similarity, saturation_boost=1, brightness_factor=1)
                        ui.label(f'{similarity * 100:.0f}%').classes('text-7xl mr-4').style(f'color: {color}')
                        
                        # Job details
                        with ui.column().classes('flex-1'):
                            ui.label(listing_info.get('title', 'Unknown Position')).classes('text-3xl font-bold mb-2')
                            with ui.row().style('gap: 8px; align-items: center;'):
                                with ui.row().style('gap: 4px; align-items: center;'):
                                    ui.icon('business').style('margin: 0')
                                    ui.label(listing_info.get('company', 'Unknown Company'))
                                with ui.row().style('gap: 4px; align-items: center;'):
                                    ui.icon('place').style('margin: 0')
                                    ui.label(listing_info.get('location', 'Location not specified'))

                    # Right side: Salary info
                    with ui.column().classes('text-right min-w-fit'):
                        salary_min = listing_info.get('salary_min')
                        salary_max = listing_info.get('salary_max')
                        currency = listing_info.get('currency', 'USD')
                        
                        if salary_min is not None and salary_max is not None:
                            salary = f"{currency} {salary_min} - {salary_max}"
                        else:
                            salary = "Salary not specified"
                        ui.label(salary).classes('text-xl font-semibold text-purple-300')

                # Missing keywords section
                missing_keywords = match_info.get('missing_keywords', [])
                if missing_keywords:
                    with ui.row().classes('flex-wrap gap-2 mt-4'):
                        ui.label('Missing Keywords:').classes('text-sm text-gray-500')
                        for kw in missing_keywords:
                            ui.chip(kw).classes('bg-transparent border-2 border-purple-700 text-white font-mono')


def open_match_details(match_data: dict):
    """Open detailed match information"""
    match_info = match_data
    listing_info = match_data.get('listing', {})
    resume_info = match_data.get('resume', {})
    
    with ui.dialog().classes('w-full max-w-[90vw] h-[90vh]') as dialog, ui.card().classes('w-full h-full'):
        with ui.scroll_area().classes('w-full h-full'):
            with ui.column().classes('p-6'):
                ui.label('Match Details').classes('text-4xl font-bold mb-4')
                
                # Job info
                job_title = listing_info.get('title', 'Unknown Position')
                company = listing_info.get('company', 'Unknown Company')
                job_link = listing_info.get('link', '')
                
                if job_link:
                    ui.link(f'{job_title} at {company}', job_link, new_tab=True).classes(
                        'text-2xl text-purple-400 no-underline mb-4')
                else:
                    ui.label(f'{job_title} at {company}').classes('text-2xl mb-4')
                
                # Similarity score
                similarity = match_info.get('cosine_similarity', 0)
                ui.label(f"Match Score: {similarity * 100:.2f}%").classes('text-xl mb-4')
                
                # Keywords comparison
                resume_keywords = resume_info.get('keywords', [])
                listing_keywords = listing_info.get('keywords', [])
                missing_keywords = match_info.get('missing_keywords', [])
                
                if resume_keywords or listing_keywords:
                    ui.label("Skills Analysis:").classes('font-semibold text-lg mb-2')
                    create_keywords_chips(missing_keywords, listing_keywords, resume_keywords)
                
                # AI Summary
                summary = match_info.get('summary', 'No summary available')
                if summary:
                    ui.label("AI Analysis:").classes('font-semibold text-lg mb-2 mt-4')
                    ui.label(summary).classes('mb-4')
                
                # Additional details
                ui.separator().classes('my-4')
                ui.label("Details:").classes('font-semibold')
                
                if resume_info:
                    ui.label(f"Resume: {resume_info.get('file_name', 'Unknown')}").classes('text-sm text-gray-500')
                
                matched_at = match_info.get('matched_at')
                if matched_at:
                    ui.label(f"Matched: {matched_at}").classes('text-sm text-gray-500')
                
                # Job description
                description = listing_info.get('description', '')
                if description:
                    ui.label("Job Description:").classes('font-semibold mt-4 mb-2')
                    ui.label(description).classes('text-sm')
                
                ui.button('Close', on_click=dialog.close).classes(f'{PURPLE_BUTTON} mt-6')
    dialog.open()


def create_keywords_chips(missing_keywords: List[str], listing_keywords: List[str], resume_keywords: List[str]):
    """Create keyword chips showing missing and fulfilled keywords"""
    with ui.column().classes('gap-4'):
        # Missing keywords (red)
        if missing_keywords:
            with ui.row().classes('flex-wrap gap-2'):
                ui.label('Missing Skills:').classes('text-sm font-semibold text-red-400')
                for kw in missing_keywords:
                    ui.chip(kw).classes('bg-transparent border-2 border-red-800 text-white font-mono')
        
        # Fulfilled keywords (green)
        fulfilled_keywords = set(listing_keywords) - set(missing_keywords)
        if fulfilled_keywords:
            with ui.row().classes('flex-wrap gap-2'):
                ui.label('Matching Skills:').classes('text-sm font-semibold text-green-400')
                for kw in fulfilled_keywords:
                    ui.chip(kw).classes('bg-transparent border-2 border-green-800 text-white font-mono')


def interpolate_color(value: float, saturation_boost: float = 1.5, brightness_factor: float = 0.6) -> str:
    """Generate color based on similarity score"""
    value = max(0, min(1, value))

    def lerp(a, b, t):
        return a + (b - a) * t

    r_start, g_start, b_start = 48, 25, 52
    r_end, g_end, b_end = 255, 255, 255

    r = lerp(r_start, r_end, value)
    g = lerp(g_start, g_end, value)
    b = lerp(b_start, b_end, value)

    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

    s = min(s * saturation_boost, 1.0)
    v = min(v * brightness_factor, 1.0)

    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)

    r_final = int(r_new * 255)
    g_final = int(g_new * 255)
    b_final = int(b_new * 255)

    return f'#{r_final:02x}{g_final:02x}{b_final:02x}'
