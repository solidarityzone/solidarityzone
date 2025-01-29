import os

from flask import Flask, render_template


def init_app() -> Flask:
    # Initialize Flask HTTP server
    app = Flask(
        __name__,
        template_folder="./frontend/templates",
        static_folder="./frontend/static",
    )
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite",
        CELERY=dict(
            timezone="Asia/Yekaterinburg",
            broker_url="redis://127.0.0.1:6379/0",
            beat_schedule_filename=os.path.join(
                app.instance_path, "celerybeat-schedule"
            ),
        ),
        TEMPLATES_AUTO_RELOAD=True,
    )
    app.config.from_prefixed_env()

    # Initialize SQLite database
    from .models import db

    db.init_app(app)

    # Initialize Celery task queue
    from .scheduler import celery_init_app

    celery_init_app(app)

    # Serve static page from root
    @app.route("/")
    def index():
        from . import __version__

        return render_template("index.html", VERSION=__version__)

    with app.app_context():
        from . import commands
        from .api import api

        # Initialize CLI commands
        app.cli.add_command(commands.clean_sessions)
        app.cli.add_command(commands.init_db_command)
        app.cli.add_command(commands.scrape)
        app.cli.add_command(commands.scrape_all)
        app.cli.add_command(commands.scrape_next_batch)
        app.cli.add_command(commands.scrape_test_courts)

        # Register API routes
        app.register_blueprint(api)

    return app
