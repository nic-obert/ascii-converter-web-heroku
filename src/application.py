from typing import Type, Union
from flask import Flask, Blueprint, render_template, request, redirect, Response, current_app as app, send_file
from werkzeug.datastructures import FileStorage
from pathlib import Path

from upload_manager import UploadManager
from ascii_converter import image_to_ascii
from settings import WHITE_ON_BLACK_IMAGE_STYLE, BLACK_ON_WHITE_IMAGE_STYLE


blueprint = Blueprint(
    name='ASCII Converter',
    import_name=__name__,
    static_folder=Path('static').resolve(),
    template_folder=Path('templates').resolve()
)


class ASCIIConverterApp(Flask):
    def __init__(self, *args, **kwargs) -> None:
        self.upload_manager: UploadManager
        super().__init__(*args, **kwargs)

app: ASCIIConverterApp


def create_app() -> ASCIIConverterApp:
    application = Flask(__name__)
    application.register_blueprint(blueprint)
    application.upload_manager = UploadManager(Path('src/uploads').resolve())
    return application


@blueprint.route('/')
def index_page():
    return render_template('index.html')


@blueprint.route('/upload-image', methods=['POST'])
def upload_image_page():

    # Input validation

    image: Union[FileStorage, None] = request.files.get('upload-image')
    if image is None:
        return redirect('/')
    

    image_style = request.form.get('image-style')
    if image_style == 'BLACK_ON_WHITE':
        image_style = BLACK_ON_WHITE_IMAGE_STYLE
    elif image_style == 'WHITE_ON_BLACK':
        image_style = WHITE_ON_BLACK_IMAGE_STYLE
    else:
        return Response(f'{image_style} is not an image style')


    try:
        resize_percentage = request.form.get('resize-percentage')
        resize_percentage = float(resize_percentage)
    except TypeError:
        return Response(f'Resize percentage must be a floating point number, not {resize_percentage}')

    if resize_percentage > 200:
        resize_percentage = 200

    # Actual page functionalities

    image_name = app.upload_manager.save_image(image)
    ascii_image = image_to_ascii(image_name, resize_percentage)
    app.upload_manager.remove(image_name)
    
    return render_template('ascii_image.html', ascii_image=ascii_image, style=image_style)


@blueprint.route('/health')
def health_page():
    return Response(status=200)

