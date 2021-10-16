from typing import Tuple, NewType
from PIL import Image
from pathlib import Path
import time


Pixel = NewType("Pixel", Tuple[int, int, int, int])

CHARACTERS = (' ', '.', '°', '*', 'o', 'O', '#', '@')

MAX_CHANNEL_INTENSITY = 255
MAX_CHANNEL_VALUES = MAX_CHANNEL_INTENSITY * 4

MAX_OPEN_RETRIES = 5
RETRY_TIMEOUT = 0.1


def map_intensity_to_character(intensity: float) -> CHARACTERS:
    return CHARACTERS[round(intensity * len(CHARACTERS))]


def get_pixel_intensity(pixel: Pixel) -> float:
    return sum(pixel) / 1020


def convert_image(image: Image) -> str:
    ascii_string = ''
    width, height = image.size
    
    for col in range(height):
        for row in range(width):
            pixel: Pixel = image.getpixel((row, col))
            intensity = get_pixel_intensity(pixel)
            character = map_intensity_to_character(intensity)
            ascii_string += character
      
        ascii_string += '\n'
  
    return ascii_string


def try_load_image(image_name: Path) -> Image:
    for retry_count in range(MAX_OPEN_RETRIES):
        try:
            image = Image.open(image_name)
            break
        except FileNotFoundError:
            time.sleep(RETRY_TIMEOUT * retry_count)
            continue
    else:
        raise FileNotFoundError(f'No such file: "{image_name}"')

    return image


def image_to_ascii(image_name: Path) -> str:
    image = try_load_image(image_name)
    ascii_image = convert_image(image)
    image.close()
    return ascii_image


def video_to_ascii(video_name: Path) -> str:
    pass

