from typing import Union
from flask import Flask, Blueprint, render_template, request, redirect, Response, current_app as app
from werkzeug.datastructures import FileStorage

from upload_manager import UploadManager
from ascii_converter import image_to_ascii
from settings import STATIC_FILES_FOLDER, TEMPLATES_FOLDER, UPLOADS_FOLDER, STYLES
from database import Database


blueprint = Blueprint(
    name='ASCII Converter',
    import_name=__name__,
    static_folder=STATIC_FILES_FOLDER,
    template_folder=TEMPLATES_FOLDER
)


class ASCIIConverterApp(Flask):
    def __init__(self, *args, **kwargs) -> None:
        self.upload_manager: UploadManager
        super().__init__(*args, **kwargs)

app: ASCIIConverterApp


def create_app() -> ASCIIConverterApp:
    application = Flask(__name__)
    application.register_blueprint(blueprint)

    application.upload_manager = UploadManager(UPLOADS_FOLDER)

    Database.init_database()

    return application


@blueprint.route('/')
def index_page():
    return render_template('index.html')


@blueprint.route('/images/<int:image_id>')
def get_image(image_id: int):
    ascii_image, style_code = app.upload_manager.get_ascii_image(image_id)
    return render_template(
        'ascii_image.html',
        ascii_image=ascii_image,
        style=STYLES[style_code],
    )


@blueprint.route('/upload-image', methods=['POST'])
def upload_image_page():

    # Input validation

    image: Union[FileStorage, None] = request.files.get('upload-image')
    if image is None:
        return redirect('/')
    

    image_style = request.form.get('image-style')
    
    if image_style == 'WHITE_ON_BLACK':
        style_code = 0
    elif image_style == 'BLACK_ON_WHITE':
        style_code = 1
    else:
        return Response(f'{image_style} is not an image style')


    try:
        resize_percentage = request.form.get('resize-percentage')
        resize_percentage = float(resize_percentage)
    except TypeError:
        return Response(f'Resize percentage must be a floating point number, not {resize_percentage}')


    generate_url = request.form.get('generate-url') == 'true'


    if resize_percentage > 200:
        resize_percentage = 200

    # Actual page functionalities

    image_name = app.upload_manager.save_image(image)
    ascii_image = image_to_ascii(image_name, resize_percentage)
    app.upload_manager.remove(image_name)

    if generate_url:
        image_id = app.upload_manager.save_ascii_image(ascii_image, style_code)
        return render_template(
            'ascii_image.html',
            ascii_image=ascii_image,
            style=STYLES[style_code],
            image_id=image_id
        )
    
    return render_template(
        'ascii_image.html',
        ascii_image=ascii_image,
        style=STYLES[style_code],
    )


@blueprint.route('/health')
def health_page():
    return Response(status=200)


@blueprint.route('/favicon.ico')
def favicon_page():
    return redirect('/static/favicon.ico')

