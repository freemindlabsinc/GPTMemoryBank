from injector import Injector, singleton

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.abstractions.transcriber import Transcriber
from memorybank.services.llamaindex_index_factory import LlamaIndexIndexFactory
from memorybank.services.llamaindex_memory_store import LlamaIndexMemoryStore

from memorybank.abstractions.index_factory import IndexFactory
from memorybank.settings.app_settings import AppSettings

def _create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    
    # Settings
    app_settings = AppSettings()
    _injector.binder.bind(AppSettings, to=app_settings, scope=singleton)
    
    # Services
    _injector.binder.bind(IndexFactory, to=LlamaIndexIndexFactory, scope=singleton)
    _injector.binder.bind(Transcriber, to=Transcriber, scope=singleton)
    _injector.binder.bind(MemoryStore, to=LlamaIndexMemoryStore, scope=singleton)
    
    return _injector

global_injector = None

def setup_services() -> Injector:    
    global global_injector
    if global_injector is None:
        global_injector = _create_application_injector()            

    return global_injector