from celery import Celery
import os

# تنظیمات Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# ایجاد اپلیکیشن Celery
celery_app = Celery(
    "core",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# تنظیمات Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    result_expires=3600,
    
    # تنظیمات Celery Beat (برای وظایف زمانبندی شده)
    # beat_schedule={
    #     "cleanup-every-day": {
    #         "task": "tasks.tasks.cleanup_expired_data",
    #         "schedule": 86400,  
    #         "args": (),
    #     },
    # }
)