from nicegui import ui

from src.utils.drawer import left_drawer


def render_header():
    ui.label('JobScout').classes('text-5xl font-bold mb-4 text-indigo-700 dark:text-indigo-300')
    ui.label('AI-Powered Resume Matching Platform').classes('text-2xl text-slate-600 dark:text-slate-300 mb-4')
    ui.label('Discover your perfect job match with our intelligent platform that combines AI keyword extraction and advanced matching algorithms to connect you with opportunities that truly fit.').classes('text-lg text-slate-500 dark:text-slate-400 mb-8 leading-relaxed')
    ui.separator().classes('border-slate-200 dark:border-slate-700')


def render_features():
    ui.label('Key Features').classes('text-3xl font-bold mb-6 text-slate-800 dark:text-slate-200')

    features = [
        ('🤖', 'AI Keyword Extraction', 'Advanced AI analyzes your resume to extract relevant skills and experience automatically.'),
        ('🎯', 'Smart Job Matching', 'Cosine similarity algorithms match you with jobs based on skill alignment and missing keyword analysis.'),
        ('⚡', 'Real-Time Processing', 'Upload your resume and get instant keyword processing with automatic job search generation.'),
        ('📊', 'Match Analytics', 'View detailed match scores, missing skills, and AI-generated summaries for each job opportunity.'),
        ('🔒', 'Secure & Private', 'Your data is protected with encrypted passwords and secure session management.')
    ]

    with ui.grid(columns=2).classes('gap-6 mb-8'):
        for icon, title, description in features:
            with ui.card().classes('p-6 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:shadow-lg'):
                with ui.row().classes('items-start gap-4'):
                    ui.label(icon).classes('text-3xl')
                    with ui.column().classes('flex-1'):
                        ui.label(title).classes('font-semibold text-lg text-slate-800 dark:text-slate-200 mb-2')
                        ui.label(description).classes('text-slate-600 dark:text-slate-400 leading-relaxed')

    ui.separator().classes('border-slate-200 dark:border-slate-700 my-8')


def render_how_it_works():
    ui.label('How It Works').classes('text-3xl font-bold mb-6 text-slate-800 dark:text-slate-200')

    steps = [
        ('Upload Resume', 'Upload your resume in PDF, DOC, or DOCX format to get started.'),
        ('AI Processing', 'Our AI engine extracts keywords and analyzes your skills and experience.'),
        ('Smart Matching', 'Advanced algorithms compare your profile with job listings and calculate match scores.'),
        ('Review Results', 'Browse personalized job matches with detailed analytics and insights.')
    ]

    with ui.column().classes('gap-4 mb-8'):
        for i, (title, description) in enumerate(steps, 1):
            with ui.card().classes('p-6 border-l-4 border-indigo-500 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700'):
                with ui.row().classes('items-start gap-4'):
                    ui.label(str(i)).classes('flex-shrink-0 w-10 h-10 rounded-full bg-indigo-500 text-white text-lg font-bold flex items-center justify-center')
                    with ui.column().classes('flex-1'):
                        ui.label(title).classes('font-semibold text-xl text-slate-800 dark:text-slate-200 mb-2')
                        ui.label(description).classes('text-slate-600 dark:text-slate-400 leading-relaxed')

    ui.separator().classes('border-slate-200 dark:border-slate-700 my-8')


def render_get_started():
    ui.label('Get Started Today').classes('text-3xl font-bold mb-6 text-slate-800 dark:text-slate-200')

    with ui.card().classes('p-8 bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 border border-indigo-200 dark:border-indigo-700'):
        ui.label('Ready to find your perfect job match?').classes('text-xl font-semibold mb-6 text-slate-800 dark:text-slate-200')
        
        with ui.row().classes('gap-4 mb-6'):
            ui.button('📄 Upload Resume', on_click=lambda: ui.navigate.to('/resumes')).classes(
                'bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200'
            )
            ui.button('🎯 View Matches', on_click=lambda: ui.navigate.to('/matches')).classes(
                'bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200'
            )
        
        ui.label('New to JobScout? Create an account to get started with AI-powered job matching.').classes(
            'text-slate-600 dark:text-slate-400'
        )


def render_stats():
    ui.label('Why Choose JobScout?').classes('text-3xl font-bold mb-6 text-slate-800 dark:text-slate-200')
    
    stats = [
        ('🚀', 'AI-Powered', 'Advanced keyword extraction using state-of-the-art NLP models'),
        ('📈', 'Skill Analysis', 'Detailed gap analysis to help you improve your profile'),
        ('⚡', 'Real-Time', 'Instant processing and immediate job matching results'),
        ('🎯', 'Smart Matching', 'Intelligent algorithms for precise job-resume compatibility')
    ]
    
    with ui.grid(columns=2).classes('gap-6 mb-8'):
        for icon, title, description in stats:
            with ui.card().classes('p-6 text-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300'):
                ui.label(icon).classes('text-4xl mb-3')
                ui.label(title).classes('font-bold text-xl text-slate-800 dark:text-slate-200 mb-2')
                ui.label(description).classes('text-slate-600 dark:text-slate-400 text-sm leading-relaxed')


@ui.page('/home')
def home_page():
    left_drawer()

    with ui.column().classes('w-full max-w-6xl mx-auto p-8 bg-slate-50 dark:bg-slate-900 min-h-screen'):
        render_header()
        render_features()
        render_how_it_works()
        render_get_started()
        render_stats()
