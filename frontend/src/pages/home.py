from nicegui import ui
from src.utils.drawer import left_drawer

def render_header():
    ui.label('Resume Matcher').classes('text-4xl font-semibold mb-6')
    ui.label(
        'Welcome to Resume Matcher — your intelligent platform designed to seamlessly connect skilled professionals with their ideal career opportunities.'
    ).classes('mb-8 text-lg text-purple-300').style('line-height: 1.5')
    ui.separator().style('margin-bottom: 2rem')

def render_how_it_works():
    ui.label('How It Works').classes('text-2xl font-semibold mb-6')

    steps = [
        ('Upload Your Resume',
         'Simply upload your resume to our secure platform. Our system uses advanced parsing and analysis to understand your skills and experience.'),
        ('Browse Tailored Job Matches',
         'Receive personalized job recommendations perfectly aligned with your profile. Easily save and apply to positions that excite you.'),
        ('Track Your Applications',
         'Stay organized by managing your applications and monitoring their progress in one convenient place.')
    ]

    for i, (title, description) in enumerate(steps, start=1):
        with ui.element('div').style(
                'display: grid; grid-template-columns: 2rem 1fr; gap: 1rem; margin-bottom: 1.5rem; align-items: start;'
        ):
            ui.label(str(i)).style('font-weight: 700; font-size: 1.5rem; color: #7c3aed;')
            with ui.column():
                ui.label(title).classes('font-semibold text-lg mb-1')
                ui.label(description).classes('text-purple-200').style('line-height: 1.4')

    ui.separator().style('margin-bottom: 2rem')

def render_get_started():
    ui.label('Get Started').classes('text-2xl font-semibold mb-6')

    ui.markdown('''
    - Upload your resume to initiate the matching process.
    - Explore curated job offers tailored to your experience and aspirations.
    ''').classes('mb-8')

    ui.label('Ready to take the next step in your career?').classes('mb-2')
    ui.label('Use the navigation menu to Upload Resume or Browse Jobs.').classes('font-semibold')

    ui.separator().style('margin-top: 2rem')

def render_footer():
    ui.label(
        'Powered by advanced matching algorithms to connect talent with the right opportunities.'
    ).classes('text-sm text-purple-200 italic mt-6').style('text-align: center')

@ui.page('/home')
def home_page():
    left_drawer()

    with ui.card().style('max-width: 900px; margin: 2rem auto; padding: 2rem;'):
        render_header()
        render_how_it_works()
        render_get_started()
        render_footer()
