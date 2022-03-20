#from c_ascii_converter import ASCIIImage



class ASCIIImage:

    __slots__ = ('data', 'width', 'height', 'style_code')

    def __init__(self, data: str, width: int, height: int, style_code: int) -> None:
        self.data = data
        self.width = width
        self.height = height
        self.style_code = style_code


