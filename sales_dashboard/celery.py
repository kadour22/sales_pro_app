import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings')  # ✅ Change this if needed

app = Celery('sales_dashboard')
app.config_from_object('django.conf:settings', namespace='CELERY')  # ✅ Make sure this is here
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'notify-admin-every-day': {
        'task': 'api.tasks.send_upload_notification',
        'schedule': crontab(minute=1), 
    },
}