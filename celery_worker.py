from app import celery
from app.factory import create_app
from app.celery_utils import init_celery
from dotenv import load_dotenv

load_dotenv('.env')
app = create_app()
init_celery(celery, app)
