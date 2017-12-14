#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function, unicode_literals

import os
import time
import json
import sys
import logging
import urllib
import set_env
import datetime

DEBUG = True


def api_sending_generator(obj):

    """
    generate the payload and url in accordance to the object property
    :param model instance obj:
    :return a list containing payload and url OR a url:

    """

    source = obj.destination[:3]
    list_of_payload_and_url = []
    if source == "vic":
        payload = {
            'source': obj.phoneobject.source,
            'user': API_SENDING_AUTHENTICATION_DICT[obj.destination]["user"],
            'pass': API_SENDING_AUTHENTICATION_DICT[obj.destination]["pass"],
            'function': 'update_lead',
            'phone_number': obj.phoneobject.phone_number,
            'status': 'DNC','addDncOption':'BOTH',
            "alt_phone":obj.phoneobject.backup_phone
                   }

        url = API_SENDING_AUTHENTICATION_DICT[obj.destination]["url"]
        list_of_payload_and_url.extend([payload,url])

    else:
        if obj.phoneobject.backup_phone:
            payload = {
                "API_user": API_SENDING_AUTHENTICATION_DICT[obj.destination]["user"],
                "API_pass": API_SENDING_AUTHENTICATION_DICT[obj.destination]["pass"],
                "entry[0][phone]": obj.phoneobject.phone_number,
                "entry[1][phone]": obj.phoneobject.backup_phone,
            }
        else:
            payload = {
                "API_user": API_SENDING_AUTHENTICATION_DICT[obj.destination]["user"],
                "API_pass": API_SENDING_AUTHENTICATION_DICT[obj.destination]["pass"],
                "entry[0][phone]": obj.phoneobject.phone_number,
            }

        url = API_SENDING_AUTHENTICATION_DICT[obj.destination]["url"] + "?" + urllib.parse.urlencode(payload)
        list_of_payload_and_url.extend([url])

    return list_of_payload_and_url


def main():

    logger = logging.getLogger('send_number')

    for obj in ApiSending.objects.filter(Q(delivered=False),Q(attempt_count__lte=trycount),
                                         Q(attempt_time__isnull=True) |
                                         Q(attempt_time__lte=timezone.now()-datetime.timedelta(minutes=timespan)))[:50]:
        logger.info("Sending number {0} to {1} comming from {2}..".format(obj.phoneobject.phone_number,obj.destination,
                                                                          obj.phoneobject.source))
        obj.attempt_time = timezone.now()
        obj.attempt_count += 1
        update_fields = ["attempt_time","attempt_count"]
        try:
            lis = api_sending_generator(obj)
            if len(lis) == 1:
                r1 = requests.post(lis[0])
            else:
                r1 = requests.get(lis[1], params=lis[0])

            if str(r1.status_code) == '200':

                obj.delivered = True
                obj.delivered_time = timezone.now()
                update_fields += ["delivered","delivered_time"]
                logger.info('number: {0} comming from source: {1} is sent to destination: {2} with '
                            'status: {3} and content: {4}'
                            .format(obj.phoneobject.phone_number, obj.phoneobject.source, obj.destination,
                                    r1.status_code, r1.content))
            else:
                # print("46666666464")
                logger.warning('number: {0} comming from source: {1} can not be sent to '
                            'destination: {2} with status: {3}\n content: {4}\n'
                            .format(obj.phoneobject.phone_number, obj.phoneobject.source,obj.destination,
                                    r1.status_code, r1.content))

        except requests.exceptions.RequestException as err:
            logger.error("Sending Error: {0}--{1}".format(obj.destination,err))
            # print("Sending Error", err)

        finally:
            obj.save(update_fields=update_fields)
            logger.info("processed {0}".format(obj.id))


if __name__ == '__main__':

    set_env.activate_venv()
    import requests
    from phone.models import PhoneData,ApiSending
    from django.db.models import Q
    import datetime
    from django.utils import timezone
    from dnc_db.settings import TIME_SPAN_FOR_DATA_SENDING as timespan, MAX_TRY_COUNT as trycount, \
        API_SENDING_AUTHENTICATION_DICT
    while True:
        main()
        time.sleep(3)

