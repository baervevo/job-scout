from nicegui import ui


@ui.page('/')
def root_page():
    ui.navigate.to('/login')
