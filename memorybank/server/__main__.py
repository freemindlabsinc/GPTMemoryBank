import uvicorn

from memorybank.server.main import app
from memorybank.settings.settings import AppSettings
from memorybank.server.di import global_injector

cfg = global_injector.get(AppSettings)

# Set log_config=None to do not use the uvicorn logging configuration, and
# use ours instead. For reference, see below:
# https://github.com/tiangolo/fastapi/discussions/7457#discussioncomment-5141108
uvicorn.run(app, host=cfg.service.host, port=cfg.service.port, log_config=None)

raise Exception("This should not be reached")