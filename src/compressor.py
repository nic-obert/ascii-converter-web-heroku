from typing import Tuple
from ascii_image import ASCIIImage


MULTI_CHAR_SIGN = 0x00


def decompose_int(number: int, span: int) -> Tuple[int]:
    digest = [0] * span
    for i in range(span):
        digest[i] = number % 256
        number //= 256
        if number == 0:
            break
    return digest
    

def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little')


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
    # First create an digest with the image header
    digest = bytearray(generate_header(image))
    data = image.data[5:]
    current_char = ''
    count = 1
    for char in data:
        if char == '\n':
            continue
        
        if char == current_char:
            count += 1
        else:
            if count == 1:
                digest.append(ord(current_char))
            elif count < 4:
                digest.extend([ord(current_char)] * count)
            else:
                digest.extend(multi_char(current_char, count))
                count = 1
            
            current_char = char

    return bytes(digest)


def decompress_ascii_image(data: bytes) -> ASCIIImage:
    style_code, width, height = extract_header(data)

    data = data[5:]

    ascii_data = bytearray([b'\n'] * (width + 1) * height)

    # Index is -1 because at the first iteration, the index will be incremented
    ascii_index = -1
    for byte_index in range(len(data)):

        # Skip one byte for the newline character
        if byte_index % (width + 1) == 0:
            ascii_index += 1

        if data[byte_index] == MULTI_CHAR_SIGN:
            count = data[byte_index + 1]
            char = data[byte_index + 2]
            ascii_data[ascii_index:ascii_index + count] = [chr(char)] * count
            ascii_index += count

        else:
            ascii_data[ascii_index] = chr(data[byte_index])
            ascii_index += 1
        
    return ASCIIImage(
        data=ascii_data.decode('ascii'),
        width=width,
        height=height,
        style_code=style_code
    )

