import os

from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "placement_portal",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
)
celery_app.conf.broker_connection_retry_on_startup = True
_initialized = False


def init_celery(app=None):
    global _initialized
    if _initialized:
        return

    if app is None:
        from app import create_app
        app = create_app()

    celery_app.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
        result_backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
        broker_connection_retry_on_startup=True,
        timezone="Asia/Kolkata",
        imports=("tasks.mail_tasks", "tasks.report_tasks"),
        beat_schedule={
            "send-daily-reminders": {
                "task": "tasks.mail_tasks.send_daily_reminders",
                "schedule": crontab(hour=9, minute=0),
            },
            "generate-monthly-report": {
                "task": "tasks.report_tasks.generate_monthly_report",
                "schedule": crontab(day_of_month=1, hour=0, minute=0),
            },
        },
    )

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    _initialized = True
