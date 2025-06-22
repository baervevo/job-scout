from nicegui import ui

from src.styles import PURPLE_BUTTON
from src.utils.drawer import left_drawer

ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />', shared=True)

def render_header():
    ui.label('JobScout').classes('text-5xl font-bold mb-4 text-purple-800 dark:text-purple-200')
    ui.label('AI-Powered Resume Matching Platform').classes('text-2xl text-slate-600 dark:text-slate-300 mb-4')
    ui.label(
        'Discover your perfect job match with our intelligent platform that combines AI keyword extraction and advanced matching algorithms to connect you with opportunities that truly fit.').classes(
        'text-lg text-slate-500 dark:text-slate-400 mb-8 leading-relaxed')
    ui.separator().classes('border-slate-200 dark:border-slate-700')


def render_features():
    ui.label('Key Features').classes('text-3xl font-bold mb-6 text-purple-800 dark:text-purple-200')

    features = [
        ('eva-bulb-outline', 'AI Keyword Extraction',
         'Advanced AI analyzes your resume to extract relevant skills and experience automatically.'),
        ('eva-trending-up', 'Smart Job Matching',
         'Cosine similarity algorithms match you with jobs based on skill alignment and missing keyword analysis.'),
        ('eva-flash-outline', 'Real-Time Processing',
         'Upload your resume and get instant keyword processing with automatic job search generation.'),
        ('eva-lock', 'Match Analytics',
         'View detailed match scores, missing skills, and AI-generated summaries for each job opportunity.'),
        ('eva-shield-outline', 'Secure & Private', 'Your data is protected with encrypted passwords and secure session management.')
    ]

    with ui.grid(columns=2).classes('gap-6 mb-8'):
        for icon, title, description in features:
            with ui.card().classes(
                    'p-6 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:shadow-lg'):
                with ui.row().classes('items-start gap-4'):
                    ui.icon(icon).classes('text-6xl text-purple-800 dark:text-purple-200')
                    with ui.column().classes('flex-1'):
                        ui.label(title).classes('font-semibold text-lg text-purple-800 dark:text-purple-200 mb-2')
                        ui.label(description).classes('text-slate-600 dark:text-slate-400 leading-relaxed')

    ui.separator().classes('border-slate-200 dark:border-slate-700 my-8')


def render_how_it_works():
    ui.label('How It Works').classes('text-3xl font-bold mb-6 text-purple-800 dark:text-purple-200')

    steps = [
        ('Upload Resume', 'Upload your resume in PDF, DOC, or DOCX format to get started.'),
        ('AI Processing', 'Our AI engine extracts keywords and analyzes your skills and experience.'),
        ('Smart Matching', 'Advanced algorithms compare your profile with job listings and calculate match scores.'),
        ('Review Results', 'Browse personalized job matches with detailed analytics and insights.')
    ]

    with ui.column().classes('gap-4 mb-8'):
        for i, (title, description) in enumerate(steps, 1):
            with ui.card().classes(
                    'p-6 border-l-4 border-purple-500 bg-gray-900 dark:bg-gray-900 border border-slate-200 dark:border-slate-700'):
                with ui.row().classes('items-start gap-4'):
                    ui.label(str(i)).classes(
                        'flex-shrink-0 w-10 h-10 rounded-full bg-purple-500 text-white text-lg font-bold flex items-center justify-center')
                    with ui.column().classes('flex-1'):
                        ui.label(title).classes('font-semibold text-xl text-slate-800 dark:text-slate-200 mb-2')
                        ui.label(description).classes('text-slate-600 dark:text-slate-400 leading-relaxed')

    ui.separator().classes('border-slate-200 dark:border-slate-700 my-8')


def render_get_started():
    ui.label('Get Started Today').classes('text-3xl font-bold mb-6 text-slate-800 dark:text-purple-200')

    with ui.card().classes('p-8 border border-purple-200 dark:border-purple-700'):
        ui.label('Ready to find your perfect job match?').classes('text-xl font-semibold mb-6 text-purple-800 dark:text-purple-200')

        with ui.row().classes('gap-4 mb-6'):
            with ui.button(on_click=lambda: ui.navigate.to('/resumes')).classes(f'{PURPLE_BUTTON}'):
                ui.icon('eva-file-text')
                ui.label('     Upload Resume')

            with ui.button(on_click=lambda: ui.navigate.to('/matches')).classes(f'{PURPLE_BUTTON}'):
                ui.icon('eva-search')
                ui.label('     View Matches')

        ui.label('New to JobScout? Create an account to get started with AI-powered job matching.').classes(
            'text-slate-600 dark:text-slate-400'
        )


@ui.page('/home')
def home_page():
    left_drawer()

    with ui.column().classes('w-full max-w-6xl mx-auto p-8 min-h-screen'):
        render_header()
        render_features()
        render_how_it_works()
        render_get_started()
