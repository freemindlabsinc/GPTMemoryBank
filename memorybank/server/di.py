from injector import Injector, singleton

from memorybank.services.indexUtils import IndexFactory
from memorybank.settings.app_settings import AppSettings

def _create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    
    # Settings
    app_settings = AppSettings()
    _injector.binder.bind(AppSettings, to=app_settings, scope=singleton)
    
    # Services
    _injector.binder.bind(IndexFactory, to=IndexFactory, scope=singleton)
    
    return _injector

global_injector = None

def setup_services() -> Injector:    
    global global_injector
    if global_injector is None:
        global_injector = _create_application_injector()
    return global_injector