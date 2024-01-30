from memorybank.server.di import setup_services
from memorybank.server.appbuilder import create_app

# Create the FastAPI application
app_injector = setup_services()
app = create_app(app_injector)