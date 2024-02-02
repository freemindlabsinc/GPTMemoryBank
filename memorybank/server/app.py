from fastapi_injector import attach_injector

from memorybank.server.di import setup_services
from memorybank.server.appbuilder import create_app

# Create the FastAPI application
injector = setup_services()
app = create_app()

attach_injector(app, injector)