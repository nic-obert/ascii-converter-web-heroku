from typing import Union
from flask import Flask, Blueprint, render_template, request, redirect, Response, current_app
from werkzeug.datastructures import FileStorage
from pathlib import Path
import os


app = Blueprint(
    name='ASCII Converter',
    import_name=__name__,
    static_folder=Path('static').resolve(),
    template_folder=Path('templates').resolve()
)


def create_app() -> Flask:
    application = Flask(__name__)
    application.register_blueprint(app)
    application.config['UPLOAD_FOLDER'] = Path('src/uploads').resolve()
    return application


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/upload-image', methods=['POST'])
def upload_image_page():

    image: Union[FileStorage, None] = request.files.get('upload-image')
    if image is None:
        return redirect('/')

    image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename))

    return Response(status=200)


