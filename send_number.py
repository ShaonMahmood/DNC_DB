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

#logger = set_env.get_logger(debug=DEBUG)


#exclude_condition = ['trying', 'failed', 'no-answer', 'busy']


#json_decoder = json.JSONDecoder()

def main():

    logger = logging.getLogger('send_number')

    for obj in PhoneData.objects.filter(number_delivered=False)[:50]:

        vicidial_tcm_payload = {'source': obj.source, 'user': '101', 'pass': '451USXB32N4mD',
                   'function': 'update_lead', 'phone_number': obj.phone_number, 'status': 'DNC','addDncOption':'BOTH',
                   "alt_phone":obj.backup_phone}

        vicidial_eagent_payload = {'source': obj.source, 'user': '101', 'pass': '046USXB32N4xyDK',
                   'function': 'update_lead', 'phone_number': obj.phone_number, 'status': 'DNC','addDncOption':'BOTH',
                   "alt_phone":obj.backup_phone}

        xencall_payload = {
            "API_user":"evan",
            "API_pass":"boat1234",
            "entry[0][phone]":obj.phone_number,
            "entry[1][phone]":obj.backup_phone,
        }

        # json.dumps({
        #     "phone": obj.phone_number,
        # })

        url1 = "http://tcm.ytel.com/x5/api/non_agent.php"
        url2 = "http://eagent.ytel.com/x5/api/non_agent.php"
        url3 = "https://nha-beta.xencall.com/TPI/DNC?" + urllib.parse.urlencode(xencall_payload)

        try:
            count = 0
            if not obj.vicidial_tcm_delivered:
                r1 = requests.get(url1, params=vicidial_tcm_payload)
                if str(r1.status_code) == '200':
                    count = count + 1
                    obj.vicidial_tcm_delivered = True
                    logger.info('{0}--{1}--{2}'.format(obj.phone_number, r1.status_code, r1.content))
                    obj.vicidial_tcm_attempt += 1

                else:
                    print("46666666464")
                    logger.info('{0}--{1}--{2}'.format(obj.phone_number, r1.status_code, r1.content))
                    obj.vicidial_tcm_attempt += 1

            if not obj.vicidial_eagent_delivered:
                r2 = requests.get(url2, params=vicidial_eagent_payload)
                if str(r2.status_code) == '200':
                    count = count + 1
                    obj.vicidial_eagent_delivered = True
                    obj.vicidial_eagent_attempt += 1
                    logger.info('{0}--{1}--{2}'.format(obj.phone_number, r2.status_code, r2.content))
                else:
                    print("46666666464")
                    logger.info('{0}--{1}--{2}'.format(obj.phone_number, r2.status_code, r2.content))
                    obj.vicidial_eagent_attempt += 1

            if not obj.xencall_delivered:
                r3 = requests.post(url3)
                if str(r3.status_code) == '200':
                    count = count + 1
                    obj.xencall_delivered = True
                    obj.xencall_attempt += 1
                    logger.info('{0}--{1}--{2}'.format(obj.phone_number, r3.status_code, r3.content))
                else:
                    print("46666666464")
                    logger.info('{0}--{1}--{2}'.format(obj.phone_number, r3.status_code, r3.content))
                    obj.xencall_attempt += 1
            # print("url: ",r3.url)
            # print("status code: ", r3.status_code)
            # print("content: ", r3.content)
            # print("r1: ", r1.text, r1.content, r1.status_code)
            # print("r2: ", r2.text, r2.content, r2.status_code)
            # print("r3 ", r3.text, r3.content, r3.status_code)


            # logger.info('{0}--{1}--{2}'.format(obj.phone_number,r1.status_code,r1.content))
            # logger.info('{0}--{1}--{2}'.format(obj.phone_number, r2.status_code, r2.content))
            # logger.info('{0}--{1}--{2}'.format(obj.phone_number, r3.status_code, r3.content))
            if count == 3:
                obj.number_delivered = True
                obj.save(update_fields=['number_delivered','xencall_delivered','vicidial_eagent_delivered',
                                        'vicidial_tcm_delivered','xencall_attempt','vicidial_eagent_attempt',
                                        'vicidial_tcm_attempt'])
            else:
                obj.save(update_fields=['xencall_delivered', 'vicidial_eagent_delivered',
                                        'vicidial_tcm_delivered','xencall_attempt','vicidial_eagent_attempt',
                                        'vicidial_tcm_attempt'])
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
        time.sleep(3)


# for eagent : user=101&pass=046USXB32N4xyDK
# for tcm: user=101&pass=451USXB32N4mD