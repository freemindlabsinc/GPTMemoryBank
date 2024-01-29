from injector import Injector
from injector import Module, Injector, singleton
from memorybank.settings.settings import AppSettings, load_app_settings_from_env
from memorybank.datastore.datastore import DataStore
from memorybank.datastore.providers.llamaindex import LlamaIndexDataStore

def create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    
    # Settings
    app_settings = load_app_settings_from_env()
    _injector.binder.bind(AppSettings, to=app_settings, scope=singleton)
    
    # Services
    _injector.binder.bind(DataStore, to=LlamaIndexDataStore, scope=singleton)
    
    return _injector


"""
Global injector for the application.

Avoid using this reference, it will make your code harder to test.

Instead, use the `request.state.injector` reference, which is bound to every request
"""
global_injector: Injector = create_application_injector()
