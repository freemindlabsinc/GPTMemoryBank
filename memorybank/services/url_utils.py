from urllib.parse import urlparse
from enum import Enum

class Service(Enum):
    Unsupported = 0
    YouTube = 1
    GoogleDrive = 2
    WebAddress = 3

def get_service_from_url(url: str) -> Service:
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc:
        return Service.YouTube
    elif "drive.google.com" in parsed_url.netloc:
        return Service.GoogleDrive
    elif parsed_url.scheme in ['http', 'https']:
        return Service.WebAddress
    else:
        return Service.Unsupported