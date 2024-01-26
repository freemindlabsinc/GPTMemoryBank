import os
from dotenv import load_dotenv

load_dotenv()

def get_configured(var_name, default_value=None, is_required=False):
    value = os.getenv(var_name, default_value)
    if is_required and not value:
        raise Exception(f'Required environment variable {var_name} not found')
    return value