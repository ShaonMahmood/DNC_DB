import urllib
import requests
import datetime

from celery.task import PeriodicTask
from datetime import datetime, timedelta

from phone.models import ApiSending,API_CONFIG
from django.db.models import Q
from celery.utils.log import get_task_logger
from django.utils import timezone
from dnc_db.settings import TIME_SPAN_FOR_DATA_SENDING as timespan, MAX_TRY_COUNT as trycount
from phone.only_one_task import only_one
from django.conf import settings

logger = get_task_logger('send_number')

DEBUG = True


def api_sending_generator(obj):

    """
    generate the payload and url in accordance to the object property
    :param model instance obj:
    :return a list containing payload and url OR a url:

    """

    source = obj.destination[:3]
    api = API_CONFIG.objects.get(name=obj.destination)
    list_of_payload_and_url = []
    if source == "vic":
        payload = {
            'source': obj.phoneobject.source,
            'user': api.user,
            'pass': api.password,
            'function': 'update_lead',
            'phone_number': obj.phoneobject.phone_number,
            'status': 'DNC','addDncOption':'BOTH',
            "alt_phone":obj.phoneobject.backup_phone
                   }

        url = api.url
        list_of_payload_and_url.extend([payload,url])

    else:
        if obj.phoneobject.backup_phone:
            payload = {
                "API_user": api.user,
                "API_pass": api.password,
                "entry[0][phone]": obj.phoneobject.phone_number,
                "entry[1][phone]": obj.phoneobject.backup_phone,
            }
        else:
            payload = {
                "API_user": api.user,
                "API_pass": api.password,
                "entry[0][phone]": obj.phoneobject.phone_number,
            }

        url = api.url + "?" + urllib.parse.urlencode(payload)
        list_of_payload_and_url.extend([url])

    return list_of_payload_and_url


class DataSendingTask(PeriodicTask):

    # The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=5)

    @only_one(ikey="start_sending_data", timeout=settings.CELERY_TASK_LOCK_EXPIRE)
    def run(self, **kwargs):

        logger.info('Sending Dnc Data')
        logger.info("TASK :: {0}".format(self.__class__.__name__))

        for obj in ApiSending.objects.filter(Q(delivered=False), Q(attempt_count__lte=trycount),
                                             Q(attempt_time__isnull=True) |
                                                     Q(attempt_time__lte=timezone.now() - timedelta(
                                                         minutes=timespan)))[:settings.DATA_SENDING_LIMIT]:
            logger.info(
                "Sending number {0} to {1} comming from {2}..".format(obj.phoneobject.phone_number, obj.destination,
                                                                      obj.phoneobject.source))
            obj.attempt_time = timezone.now()
            obj.attempt_count += 1
            update_fields = ["attempt_time", "attempt_count"]
            try:
                lis = api_sending_generator(obj)
                if len(lis) == 1:
                    r1 = requests.post(lis[0], timeout=(10, 10))
                else:
                    r1 = requests.get(lis[1], params=lis[0], timeout=(10, 10))

                if str(r1.status_code) == '200':

                    obj.delivered = True
                    obj.delivered_time = timezone.now()
                    update_fields += ["delivered", "delivered_time"]
                    logger.info('number: {0} comming from source: {1} is sent to destination: {2} with '
                                'status: {3} and content: {4}'
                                .format(obj.phoneobject.phone_number, obj.phoneobject.source, obj.destination,
                                        r1.status_code, r1.content))
                else:
                    # print("46666666464")
                    logger.warning('number: {0} comming from source: {1} can not be sent to '
                                   'destination: {2} with status: {3}\n content: {4}\n'
                                   .format(obj.phoneobject.phone_number, obj.phoneobject.source, obj.destination,
                                           r1.status_code, r1.content))

            except requests.exceptions.RequestException as err:
                logger.error("Sending Error: {0}--{1}".format(obj.destination, err))
                return False
                # print("Sending Error", err)

            finally:
                obj.save(update_fields=update_fields)
                logger.info("processed {0}".format(obj.id))
                return True