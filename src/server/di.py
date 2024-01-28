from injector import Injector
from src.settings import AppSettings, load_app_settings_from_env

def create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    
    # Settings
    app_settings = load_app_settings_from_env()
    _injector.binder.bind(AppSettings, to=app_settings)
    
    # Services
    
    return _injector


# NOTE: Use the `request.state.injector` reference, which is bound to every request