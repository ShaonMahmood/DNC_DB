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
        try:
            lis = api_sending_generator(obj)
            obj.attempt_time = timezone.now()
            if len(lis) == 1:
                r1 = requests.post(lis[0])
            else:
                r1 = requests.get(lis[1], params=lis[0])

            if str(r1.status_code) == '200':

                obj.delivered = True
                logger.info('{0}--{1}--{2}'.format(obj.phoneobject.phone_number, r1.status_code, r1.content))
                obj.attempt_count += 1
                obj.delivered_time = timezone.now()
            else:
                print("46666666464")
                logger.info('{0}--{1}--{2}'.format(obj.phoneobject.phone_number, r1.status_code, r1.content))
                obj.attempt_count += 1

            obj.save(update_fields=['attempt_time', 'delivered', 'delivered_time', 'attempt_count'])

        except requests.exceptions.RequestException as err:
            print("Sending Error", err)


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

