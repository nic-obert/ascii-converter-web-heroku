from pathlib import Path
from os import getenv


STYLES = (
    "white-on-black",
    "black-on-white",
)

STATIC_FILES_FOLDER = Path('static')
TEMPLATES_FOLDER = Path('templates')
UPLOADS_FOLDER = Path('uploads')


DEBUG = getenv('PRODUCTION') != 'TRUE'
if DEBUG:
    import dotenv
    dotenv.load_dotenv()

DATABASE_URL = getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise ValueError('DATABASE_URL is not set')    

