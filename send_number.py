#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import print_function, unicode_literals
import os
import time
import json

import sys
import logging

import set_env

import datetime


DEBUG = True

#logger = set_env.get_logger(debug=DEBUG)


#exclude_condition = ['trying', 'failed', 'no-answer', 'busy']


#json_decoder = json.JSONDecoder()

def main():

    logger = logging.getLogger('send_number')
    # logger.info("hello shaon,how are u")

    for obj in PhoneData.objects.filter(number_delivered=False):

        # logger.info("lead_info: {0}".format(obj.subject))
        # 'phone_code': '1', 'list_id': '999',

        vicidial_payload = {'source': obj.source, 'user': '101', 'pass': '451USXB32N4mD',
                   'function': 'update_lead', 'phone_number': obj.phone_number, 'status': 'DNC','addDncOption':'BOTH',
                   "alt_phone":obj.backup_phone}

        xencall_payload = {
            "API_user":"evan",
            "API_pass":"boat1234",
            "entry":{
                "phone":obj.phone_number,
            }
        }

        url1 = "http://tcm.ytel.com/x5/api/non_agent.php"
        url2 = "http://eagent.ytel.com/x5/api/non_agent.php"
        url3 = "https://nha-api.xencall.com/DNC"

        try:
            r1 = requests.get(url1, params=vicidial_payload)
            r2 = requests.get(url2, params=vicidial_payload)
            r3 = requests.post(url3, data=xencall_payload)

            logger.info('{0}--{1}--{2}'.format(obj.phone_number,r1.status_code,r1.content))
            logger.info('{0}--{1}--{2}'.format(obj.phone_number, r2.status_code, r2.content))
            logger.info('{0}--{1}--{2}'.format(obj.phone_number, r3.status_code, r3.content))

            obj.number_delivered = True
            obj.save(update_fields=['number_delivered',])
            # server.quit()

        except requests.exceptions.RequestException as err:
            print("Sending Error", err)
            # server.quit()


if __name__ == '__main__':

    set_env.activate_venv()
    import requests
    from phone.models import PhoneData
    while True:
        main()
        time.sleep(2)


# for eagent : user=101&pass=046USXB32N4xyDK
# for tcm: user=101&pass=451USXB32N4mD