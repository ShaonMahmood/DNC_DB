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

        payload = {'source': obj.source, 'phone_code': '1', 'list_id': '999', 'user': '6666', 'pass': '1234',
                   'function': 'add_lead', 'phone_number': obj.phone_number}

        url = "http://tcm.ytel.com/x5/api/non_agent.php"

        try:
            r1 = requests.get(url, params=payload)

            logger.info('{0}--{1}--{2}'.format(obj.phone_number,r1.status_code,r1.content))
            # print("text: ", r1.text)
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
