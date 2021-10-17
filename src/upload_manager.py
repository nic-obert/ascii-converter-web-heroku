from pathlib import Path
from werkzeug.datastructures import FileStorage
import time
import os


class UploadManager:

    def __init__(self, save_path: Path) -> None:
        self.save_path = save_path
        self.last_saved: int = 0
        self.instant_saved_count = 0
    

    def generate_name(self) -> str:
        saved_time = int(time.time())

        if saved_time == self.last_saved:
            self.instant_saved_count += 1
        else:
            self.instant_saved_count = 0
            self.last_saved = saved_time

        return f'{saved_time}-{self.instant_saved_count}'


    def save_image(self, image: FileStorage) -> Path:
        "Save an image, return the image's path"
        extension = Path(image.filename).suffix
        name = self.generate_name() + extension

        image_path = self.save_path.joinpath(name) 
        image.save(image_path)
        
        return image_path

    
    def remove(self, path: Path) -> None:
        os.remove(path)

