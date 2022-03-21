from typing import Tuple
from ascii_image import ASCIIImage

import c_ascii_converter


MULTI_CHAR_SIGN = 0x00
NEWLINE_CHAR_CODE = 10


# Function for debugging purposes
def count_each_char(data: str) -> None:
    chars = {}
    for char in data:
        if char in chars:
            chars[char] += 1
        else:
            chars[char] = 1
    
    print(chars)


def decompose_int(number: int, span: int) -> Tuple[int]:
    digest = [0] * span
    for i in reversed(range(span)):
        digest[i] = number % 256
        number //= 256
        if number == 0:
            break
    return digest
    

def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder='big')


def generate_header(image: ASCIIImage) -> bytes:
    """Return a 5-byte header including metadata for the image."""
    return bytes([
        image.style_code, # 1 byte
        *decompose_int(image.width, 2), # 2 bytes
        *decompose_int(image.height, 2), # 2 bytes
    ])


def extract_header(data: bytes) -> Tuple[int, int, int]:
    """Extract the header from the first 5 bytes of the data."""
    style_code = data[0] # 1 byte
    width = bytes_to_int(data[1:3]) # 2 bytes
    height = bytes_to_int(data[3:5]) # 2 bytes
    return style_code, width, height


def multi_char(char: str, count: int) -> bytes:
    """Return a 3-byte sequence representing a multi-character sequence."""
    return bytes([MULTI_CHAR_SIGN, count, ord(char)])


def compress_ascii_image(image: ASCIIImage) -> bytes:
    """Return a bytes object representing the compressed ASCII image."""

    print("Compressing image...")
    print("width:", image.width)
    print("height:", image.height)
    print("style_code:", image.style_code)
    return c_ascii_converter.compress_frame(
        image.data,
        image.width,
        image.height,
        image.style_code
    )

'''
def compress_ascii_image(image: ASCIIImage) -> bytes:
    # First create a digest with the image header
    digest = bytearray(generate_header(image))

    count = 1
    current_char = image.data[0]
    for char in image.data[1:]:

        if current_char == char:
            count += 1
            if count == 255:
                digest.extend(multi_char(current_char, 255))
                count = 1
        
        elif count < 4:
            if current_char is not None:
                digest.extend([ord(current_char)] * count)
                count = 1
            current_char = char

        else:
            digest.extend(multi_char(current_char, count))
            count = 1
            current_char = char

    # Add the last character, which should be a newline
    if current_char is not None:
        digest.extend([ord(current_char)] * count)

    return bytes(digest)
'''


'''
def decompress_ascii_image(data: bytes) -> ASCIIImage:
    """Return an ASCIIImage object representing the decompressed ASCII image."""
    ascii_string, width, height, style_code = c_ascii_converter.decompress_frame(data)
    return ASCIIImage(ascii_string, width, height, style_code)
'''

def decompress_ascii_image(data: bytes) -> ASCIIImage:
    style_code, width, height = extract_header(data)

    # The first 5 bytes are the header
    data = data[5:]

    # Create a buffer to store the decompressed image. 
    # Width + 1 is because we need to store the newline character.
    ascii_image: str = ''

    data_index = 0
    while data_index < len(data):
        byte = data[data_index]

        # If the byte is a multi-character sequence, read the count and the character
        if byte == MULTI_CHAR_SIGN:
            count = data[data_index + 1]
            char = data[data_index + 2]
            data_index += 3 # Skip the whole multi-char sequence
            ascii_image += chr(char) * count
        
        # If the byte is a single character, just copy it
        else:
            ascii_image += chr(byte)
            data_index += 1
        
    return ASCIIImage(
        data=ascii_image,
        width=width,
        height=height,
        style_code=style_code
    )


