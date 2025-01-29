from celery import Celery, Task
from celery.schedules import crontab
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.name, task_cls=FlaskTask)
    celery.config_from_object(app.config["CELERY"])
    celery.set_default()
    app.extensions["celery"] = celery

    # Define scraping schedule
    celery.conf.beat_schedule = {
        "scrape-next-batch": {
            "task": "solidarityzone.tasks.scrape_next_batch",
            # Run every 15 minutes
            "schedule": crontab(minute="*/15"),
            # Scrape 5 courts per batch (multiplied by number of articles)
            "args": (5,),
        },
        "clean-sessions": {
            "task": "solidarityzone.tasks.clean_sessions",
            # Run every day at midnight
            "schedule": crontab(minute=0, hour=0),
            "args": (),
        },
    }

    return celery
