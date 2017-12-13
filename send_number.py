#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import print_function, unicode_literals
import os
import time
import json

import sys
import logging
import urllib

import set_env

import datetime


DEBUG = True


def main():

    logger = logging.getLogger('send_number')

    for obj in ApiSending.objects.filter(Q(delivered=False),Q(attempt_count__lte=trycount),
                                         Q(attempt_time__isnull=True) |
                                                 Q(attempt_time__lte=timezone.now()-datetime.timedelta(minutes=timespan)))[:50]:
        try:

            if obj.destination == "vicidial 1":

                vicidial_tcm_payload = {'source': obj.phoneobject.source, 'user': '101', 'pass': '451USXB32N4mD',
                           'function': 'update_lead', 'phone_number': obj.phoneobject.phone_number, 'status': 'DNC','addDncOption':'BOTH',
                           "alt_phone":obj.phoneobject.backup_phone}

                url1 = "http://tcm.ytel.com/x5/api/non_agent.php"

                obj.attempt_time = timezone.now()

                r1 = requests.get(url1, params=vicidial_tcm_payload)
                if str(r1.status_code) == '200':

                    obj.delivered = True
                    logger.info('{0}--{1}--{2}'.format(obj.phoneobject.phone_number, r1.status_code, r1.content))
                    obj.attempt_count += 1
                    obj.delivered_time = timezone.now()

                else:
                    print("46666666464")
                    logger.info('{0}--{1}--{2}'.format(obj.phoneobject.phone_number, r1.status_code, r1.content))
                    obj.attempt_count += 1

            elif obj.destination == "vicidial 2":

                vicidial_eagent_payload = {'source': obj.phoneobject.source, 'user': '101', 'pass': '046USXB32N4xyDK',
                           'function': 'update_lead', 'phone_number': obj.phoneobject.phone_number, 'status': 'DNC','addDncOption':'BOTH',
                           "alt_phone":obj.phoneobject.backup_phone}

                url2 = "http://eagent.ytel.com/x5/api/non_agent.php"

                obj.attempt_time = timezone.now()

                r1 = requests.get(url2, params=vicidial_eagent_payload)
                if str(r1.status_code) == '200':

                    obj.delivered = True
                    logger.info('{0}--{1}--{2}'.format(obj.phoneobject.phone_number, r1.status_code, r1.content))
                    obj.attempt_count += 1
                    obj.delivered_time = timezone.now()

                else:
                    print("46666666464")
                    logger.info('{0}--{1}--{2}'.format(obj.phoneobject.phone_number, r1.status_code, r1.content))
                    obj.attempt_count += 1

            elif obj.destination == "xencall":
                if obj.phoneobject.backup_phone:
                    xencall_payload = {
                        "API_user":"evan",
                        "API_pass":"boat1234",
                        "entry[0][phone]":obj.phoneobject.phone_number,
                        "entry[1][phone]":obj.phoneobject.backup_phone,
                    }

                else:
                    xencall_payload = {
                        "API_user": "evan",
                        "API_pass": "boat1234",
                        "entry[0][phone]": obj.phoneobject.phone_number,
                    }

                url3 = "https://nha-beta.xencall.com/TPI/DNC?" + urllib.parse.urlencode(xencall_payload)

                obj.attempt_time = timezone.now()

                r1 = requests.post(url3)
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
    from dnc_db.settings import TIME_SPAN_FOR_DATA_SENDING as timespan, MAX_TRY_COUNT as trycount
    while True:
        main()
        time.sleep(3)


# for eagent : user=101&pass=046USXB32N4xyDK
# for tcm: user=101&pass=451USXB32N4mD