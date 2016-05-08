'''
RescueTime Reports

Reports for https://www.rescuetime.com/
'''
import datetime
import logging
import os

from celery.schedules import crontab
from celery.task.base import periodic_task

import simplestats.requests as requests
from simplestats.models import Stat

from django.utils import timezone

logger = logging.getLogger(__name__)

RESCUE_TIME_KEY = os.environ.get('RESCUE_TIME_KEY')

PRODUCTIVITY = {
    -2: 'rescuetime.verydistracting',
    -1: 'rescuetime.distracting',
    0: 'rescuetime.neutral',
    1: 'rescuetime.productive',
    2: 'rescuetime.veryproductive',
}


@periodic_task(run_every=crontab(minute=0, hour=0))
def collect():
    '''Collect daily stats from RescueTime'''
    response = requests.get('https://www.rescuetime.com/anapi/data', params={
        'key': RESCUE_TIME_KEY,
        'format': 'json',
        'resolution_time': 'day',
        'restrict_begin': datetime.date.today() - datetime.timedelta(days=7),
        'restrict_end': datetime.date.today() - datetime.timedelta(days=1),
        'perspective': 'interval',
        'restrict_kind': 'productivity',
    })

    response.raise_for_status()
    data = response.json()

    for date, time, _, productivity in data['rows']:
        date = datetime.datetime.strptime(date, '%Y-%m-%dT00:00:00')
        Stat.insert(
            created=timezone.make_aware(date),
            key=PRODUCTIVITY[productivity],
            value=time,
        )