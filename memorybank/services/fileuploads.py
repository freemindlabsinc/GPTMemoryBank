
from fastapi import UploadFile
import os

def store_uploaded_file(file: UploadFile):
    path_name = "uploads"
    
    if os.path.exists(path_name) == False:
        os.mkdir(path_name)        
    file_location = f"{path_name}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    return path_name