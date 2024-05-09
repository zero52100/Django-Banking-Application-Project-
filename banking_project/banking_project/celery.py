from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_project.settings')

app = Celery('banking_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'calculate-interest-every-month': {
        'task': 'account.tasks.calculate_interest_and_update',  # Task from account.tasks
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
    'reset-remaining-budget-monthly': {
        'task': 'financial_planning.tasks.reset_remaining_budget',  # Task from financial_planning.tasks
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Run at midnight on the 1st of every month
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
