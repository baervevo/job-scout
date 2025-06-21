import colorsys
from typing import List

from nicegui import ui

from src.mock_data import listings, matches
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.match import Match
from src.styles import PURPLE_BUTTON
from src.utils.drawer import left_drawer


@ui.page('/matches')
def matches_page():
    left_drawer()
    with ui.column().classes('w-full'):
        for i in range(len(matches)):
            create_match_card(matches[i], listings[i])


def create_match_card(match: Match, listing: ListingKeywordData):
    card = ui.card().tight().classes('w-full cursor-pointer hover:bg-gray-800 relative z-10')
    card.on("click", lambda m=match, l=listing: open_match_details(m, l))
    with card:
        with ui.column():
            with ui.row():
                color = interpolate_color(match.cosine_similarity, saturation_boost=1.8, brightness_factor=1)
                ui.label(f'{match.cosine_similarity * 100:.0f}% ').classes('text-7xl font-mono').style(f'color: {color}')
                with ui.column():
                    ui.label(f'{listing.title}').classes('text-3xl font-bold')
                    with ui.row():
                        ui.label(f'{listing.company}')
                        ui.label(f'{listing.location}')

                if listing.salary_min is not None and listing.salary_max is not None:
                    salary = f"{listing.currency} {listing.salary_min} - {listing.salary_max}"
                else:
                    salary = "Salary not specified"
                ui.label(f'{salary}').classes('text-2xl absolute right-4')

            with ui.row().classes('flex-wrap gap-2'):
                ui.label(f'Missing Keywords:').classes('text-sm text-gray-500')
                for kw in match.missing_keywords:
                    ui.chip(kw).classes('bg-transparent border-2 border-purple-700 text-white font-mono')


def open_match_details(match: Match, listing: ListingKeywordData):
    with ui.dialog().classes('w-full max-w-[90vw] h-[90vh]') as dialog, ui.card().classes('w-full h-full'):
        ui.label(f'Match Details').classes('text-4xl font-bold mb-2')
        ui.link(f'{listing.title} at {listing.company}', listing.link, new_tab=True).classes(
            'text-2xl text-purple-400 no-underline')
        ui.label(f"Cosine Similarity: {match.cosine_similarity * 100:.2f}%")
        create_keywords_chips(match.missing_keywords, listing.keywords)
        ui.label(f"AI Summary: ").classes('font-semibold')
        ui.label(f"{match.summary}")
        ui.space()
        ui.label(f"Resume ID: {match.resume_id}").classes('text-sm text-gray-500')
        ui.label(f"Listing ID: {match.listing_id}").classes('text-sm text-gray-500')
        ui.label(
            f"Updated At: {listing.updated_at.strftime('%Y-%m-%d %H:%M:%S') if listing.created_at else 'N/A'}").classes(
            'text-sm text-gray-500')
        ui.button('Close', on_click=dialog.close).classes(f'{PURPLE_BUTTON} mt-4')
    dialog.open()


def create_keywords_chips(missing_keywords: List[str], keywords: List[str]):
    with ui.row():
        for kw in missing_keywords:
            ui.chip(kw).classes('bg-transparent border-2 border-red-800 text-white font-mono')
        fullfilled_keywords = set(keywords) - set(missing_keywords)
        for kw in fullfilled_keywords:
            ui.chip(kw).classes('bg-transparent border-2 border-green-800 text-white font-mono')


def interpolate_color(value: float, saturation_boost: float = 1.5, brightness_factor: float = 0.6) -> str:
    """
    Interpolate smoothly between red → yellow → green,
    then boost saturation and lower brightness for neon-dark effect.

    - saturation_boost > 1 increases saturation
    - brightness_factor < 1 darkens the color
    """
    value = max(0, min(1, value))

    def lerp(a, b, t):
        return a + (b - a) * t

    if value <= 0.5:
        t = value / 0.5
        r = 255
        g = lerp(0, 255, t)
        b = 0
    else:
        t = (value - 0.5) / 0.5
        r = lerp(255, 0, t)
        g = lerp(255, 128, t)
        b = 0

    # Convert to 0-1 range
    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255

    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

    # Apply saturation boost and brightness reduction
    s = min(s * saturation_boost, 1.0)
    v = v * brightness_factor

    # Convert back to RGB
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)

    # Convert to 0-255 range and hex
    r_final = int(r_new * 255)
    g_final = int(g_new * 255)
    b_final = int(b_new * 255)

    return f'#{r_final:02x}{g_final:02x}{b_final:02x}'