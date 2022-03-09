import time
import os
from pathlib import Path
from typing import Tuple
from werkzeug.datastructures import FileStorage
from database import Database


class UploadManager:

    def __init__(self, save_path: Path) -> None:
        self.save_path = save_path
        self.last_saved: int = 0
        self.instant_saved_count = 0

        self.check_save_path()

    
    def check_save_path(self) -> None:
        if not self.save_path.exists():
            self.save_path.mkdir()
    

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
    

    def save_ascii_image(self, ascii_image: str, style_code: int) -> str:

        data = bytes([style_code]) + ascii_image.encode('utf-8')

        return str(Database.insert_image(data))
    

    def get_ascii_image(self, image_id: int) -> Tuple[str, int]:
        data = Database.select_image(image_id)
        if data is None:
            return '', 0
        
        style_code = data[0]
        ascii_image = data[1:].decode('utf-8')

        return ascii_image, style_code

