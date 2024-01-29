from injector import Injector
from injector import Module, Injector, singleton
from llama_index import VectorStoreIndex
from memorybank.services.indexUtils import IndexFactory
from memorybank.settings.settings import AppSettings, load_app_settings_from_env
from memorybank.datastore.datastore import DataStore
from memorybank.datastore.providers.llamaindex import LlamaIndexDataStore

def _create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    
    # Settings
    app_settings = load_app_settings_from_env()
    _injector.binder.bind(AppSettings, to=app_settings, scope=singleton)
    
    # Services
    _injector.binder.bind(DataStore, to=LlamaIndexDataStore, scope=singleton)
    _injector.binder.bind(IndexFactory, to=IndexFactory, scope=singleton)
    
    return _injector

global_injector = None

def setup_services() -> Injector:    
    global global_injector
    if global_injector is None:
        global_injector = _create_application_injector()
    return global_injector