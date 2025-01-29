from .app import init_app
from .version import version

flask_app = init_app()
celery_app = flask_app.extensions["celery"]
__version__ = version
