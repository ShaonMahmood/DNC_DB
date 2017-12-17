import logging
import random

import requests
import json

import time
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

from dnc_db import settings
from phone.models import ResourceIdGenerator
from .forms import PhoneForm, KeyGeneratorForm, XencallForm, VicidialForm

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from phone.models import PhoneData,ApiSending
from phone.serializers import PhoneSerializer
# Create your views here.


logger = logging.getLogger('receive_number')

def check_admin(user):
    return user.is_superuser


def home(request):
    keylist = ResourceIdGenerator.objects.all()
    return render(request, 'home.html',{"keylist":keylist})


@login_required(login_url='/accounts/login/')
@user_passes_test(check_admin)
def key_generate(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = KeyGeneratorForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            obj = form.save(commit=False)
            import uuid
            obj.resource_id = str(uuid.uuid1())
            obj.save()
            print(obj)
            return redirect('phone:home')

            # if a GET (or any other method) we'll create a blank form
    else:
        form = KeyGeneratorForm()

    return render(request, 'generate_form.html', {'form': form})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def validate_phone(request,sourceName, sourceId):

    logger.info("Receiving number from source: {0} and sourceId: {1}".format(sourceName,sourceId))

    logger.info("start validating : {0}".format(time.time()))
    raw_source = sourceName + "-" + sourceId
    try:

        a = settings.API_SENDING_DICT[raw_source]

    except KeyError:
        logger.error("source is invalid {0}".format(raw_source))
        return JsonResponse({'error':"unknown provider"},status=400)

    logger.info("start validating : {0}".format(time.time()))


    if sourceName == 'xencall':

        logger.info("start time for xencall : {0}".format(time.time()))

        if request.method == 'GET':
            vals = request.GET

        else:
            vals = request.POST

        eventtime = time.time()

        accepted_list = ["DNC", "dnc", "Dnc", "Do Not Call",]
        result = vals.get('result', '').strip()

        if result not in accepted_list:
            return JsonResponse({"code": "Thank u for your submission"}, status=200)

        else:

            logger.info("start time for real : {0}".format(time.time()))
            errors = {}

            phone = ''
            try:
                phone = vals['phone1'].strip()
            except KeyError:
                errors['phone1'] = "phone number missing"

            backupphone = vals.get('phone2', '').strip()

            source = vals.get('source', '').strip()

            lead_id = ''
            try:
                lead_id = vals['leadid'].strip()
            except KeyError:
                errors['leadid'] = "leadid missing"


            if errors:
                return JsonResponse(errors, status=400)

            data = {
                'source':source,
                'phone': phone,
                'alternate_phone': backupphone,
                'result': result,
                'eventtime': eventtime,
                'lead_id': lead_id,
            }

            # print("data incomming: ",data)

            form = XencallForm({'phone_number':phone, 'key':result, 'backup_phone':backupphone})
            if form.is_valid():
                logger.info("before form data saving : {0}".format(time.time()))
                # raw_source = sourceName + "-" + sourceId
                apiLength = len(settings.API_SENDING_DICT[raw_source])
                apiList = settings.API_SENDING_DICT[raw_source]
                obj = form.save(commit=False)
                obj.source = raw_source + "-" + source

                logger.info("before transaction : {0}".format(time.time()))
                with transaction.atomic():
                    obj.save()
                    logger.info("transaction first save : {0}".format(time.time()))
                    for i in range(0,apiLength):
                        logger.info("transaction for {0} and time : {1}".format(i,time.time()))
                        ApiSending.objects.create(destination=apiList[i], phoneobject=obj)
                        logger.info("each transaction: {0}".format(time.time()))

                    logger.info("within transaction: {0}".format(time.time()))

                logger.info('the number {0} with source name {1} is saved'.format(obj.phone_number, obj.source))
                logger.info("after form data saving : {0}".format(time.time()))

                return JsonResponse({"code": "phone number sucessfully saved"}, status=200)

            else:
                logger.warning("form validation failed, Errors: {0}".format(form.errors))
                return JsonResponse(form.errors, status=400)

    elif sourceName == 'vicidial':

        if request.method == 'GET':
            vals = request.GET

        else:
            vals = request.POST

        eventtime = time.time()
        accepted_list = ["DNC", "dnc", "Dnc", "Do Not Call",]
        dispo = vals.get('dispo', '').strip()

        if dispo not in accepted_list:
            return JsonResponse({"code":"Thank u for your submission"},status=200)

        else:
            errors = {}

            phone = ''
            try:
                phone = vals['phone_number'].strip()
            except KeyError:
                errors['phone_number'] = "phone number missing"

            phonecode = ''
            try:
                phonecode = vals['phone_code'].strip()
            except KeyError:
                errors['phone_code'] = "phone code missing"

            leadid = vals.get('leadID', '').strip()
            listid = vals.get('listID', '').strip()

            source = vals.get('source', '').strip()

            talk_time = vals.get('talk_time', '').strip()

            if errors:
                return JsonResponse(errors, status=400)

            data = {
                'phone': phone,
                'source': source,
                'phoneCode': phonecode,
                'eventtime': eventtime,
                'leadid': leadid,
                'listid': listid,
                'dispo': dispo,
                'talkTime': talk_time,
            }

            # print("data incomming: ", data)

            form = VicidialForm({'phone_number': phone, 'key': dispo})
            if form.is_valid():
                # raw_source = sourceName + "-" + sourceId
                apiLength = len(settings.API_SENDING_DICT[raw_source])
                apiList = settings.API_SENDING_DICT[raw_source]
                # print(form.cleaned_data)
                obj = form.save(commit=False)
                obj.source = raw_source + "-" + source
                obj.save()

                with transaction.atomic():
                    obj.save()
                    for i in range(0,apiLength):
                        ApiSending.objects.create(destination=apiList[i], phoneobject=obj)

                logger.info('the number {0} with source name {1} is saved'.format(obj.phone_number, obj.source))

                return JsonResponse({"code": "phone number successfully saved"}, status=200)

            else:
                logger.warning("form validation failed, Errors: {0}".format(form.errors))
                return JsonResponse(form.errors, status=400)

    else:
        logger.error("the provider is unknown")
        return JsonResponse({'error':"unknown provider"},status=400)




# for testing purpose only
# a random form
@login_required
def test_form(request):

    start =time.time()

    logger.info("start sampling : {0}".format(start))

    numlist = random.sample(range(2000000000, 9999999999), 10)

    end = time.time()

    logger.info("start sampling : {0}".format(start))

    logger.info("random sampling time {0}".format(int((end - start) * 1000)))

    api_list = [
        "http://dnc-db.dev.concitus.com/api/xencall/1/",
        "http://dnc-db.dev.concitus.com/api/vicidial/1/",
        "http://dnc-db.dev.concitus.com/api/vicidial/2/",
        # "http://" + request.get_host() + "/api/xencall/1/",
        # "http://" + request.get_host() + "/api/vicidial/1/",
        # "http://" + request.get_host() + "/api/vicidial/2/",
        # "http://" + request.get_host() + "/api/xencall/2/",
        # "http://" + request.get_host() + "/api/xencall/3/",
    ]

    result = []
    for i in range(0, len(api_list)):

        logger.info("inside {0} loop in time {1}".format(i,time.time()))
        if i < len(api_list)-2:
            payload = {
                'source': 'xx',
                'result': 'Do Not Call',
                'leadid': '33',
                'phone1': numlist[i],
                'phone2': numlist[i + 5],
            }

        else:
            payload = {
                'phone_number': numlist[i],
                'phone_code': '1',
                'listID': '354',
                'leadID': '33',
                'dispo': 'Dnc',
                'talk_time': '5456'
            }

        url = api_list[i]

        try:
            r1 = requests.get(url, params=payload, timeout=(2, 6))
            # print("status code: ", r1.status_code)
            # print("content: ", r1.content)
            # print('url:', r1.url)
            result_string = "{0}---{1}".format(r1.status_code, r1.content)
            result.append(result_string)
        except requests.exceptions.RequestException as e:  # This is the error catching syntax
            logger.error("test_form: {0}".format(e))
            result.append("internal error")
    final_end = time.time()
    logger.info("program ending time before render : {0}".format(final_end))
    logger.info("total time conceeded {0}".format(int((final_end - start) * 1000)))
    return render(request, "plain_form.html", {"result": result})


def test_web_form_xencall(request):
    payload = { 'source': 'xxcrr',
                'result': 'Do Not Call',
                'leadid': '33',
                'phone1': '5456547546',
                'phone2': '5456654567',

    }

    url = "http://dnc-db.dev.concitus.com/api/xencall/1/"

    try:
        r1 = requests.get(url, params=payload)
        print("status code: ", r1.status_code)
        print("content: ", r1.content)
        print('url:',r1.url)
        return JsonResponse({'success':str(r1.content)},status=200)
    except requests.exceptions.RequestException as e:  # This is the error catching syntax
        print(e)
        return Response({"code": "server don't responded properly"},
                        status=500)


def test_web_form_vicidial(request):
    payload = {'phone_number': '4876859999',
               'phone_code': '1',
               'listID': '354',
               'leadID': '33',
               'dispo': 'Dnc',
               'talk_time': '5456'
               }
    url = "http://dnc-db.dev.concitus.com/api/vicidial/1/"

    try:
        r1 = requests.get(url, params=payload)
        print("status code: ", r1.status_code)
        print("content: ", r1.content)
        print('url:', r1.url)
        return JsonResponse({'success': str(r1.content)}, status=200)
    except requests.exceptions.RequestException as e:  # This is the error catching syntax
        print(e)
        return Response({"code": "server don't responded properly"},
                        status=500)



# rest API
@api_view(['GET', 'POST'])
@authentication_classes((BasicAuthentication,TokenAuthentication))
def number_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = PhoneData.objects.all()
        serializer = PhoneSerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PhoneSerializer(data=request.data)
        if serializer.is_valid():
            print("serialized data: ",serializer.validated_data)
            #print("serialized data: ",serializer.data)
            payload = {'source': 'test', 'phone_code': '1', 'list_id': '999', 'user': '6666', 'pass': '1234',
                       'function': 'add_lead', 'phone_number': serializer.validated_data['phone_number']}
            url = "http://tcm.ytel.com/x5/api/non_agent.php"
            try:
                r1 = requests.get(url, params=payload)
                print("status code: ", r1.status_code)
                print("content: ", r1.content)
                # print("text: ", r1.text)
                print("url: ", r1.url)
            except requests.exceptions.RequestException as e:  # This is the error catching syntax
                print(e)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
def number_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        phoneobject = PhoneData.objects.get(pk=pk)
    except PhoneData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PhoneSerializer(phoneobject)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PhoneSerializer(phoneobject, data=request.data)
        if serializer.is_valid():
            payload = {'source': 'test', 'phone_code': '1', 'list_id': '999', 'user': '6666', 'pass': '1234',
                       'function': 'update_lead','search_location':'LIST','search_method':'PHONE_NUMBER',
                       'phone_number': serializer.validated_data['phone_number']}
            url = "http://tcm.ytel.com/x5/api/non_agent.php"
            try:
                r1 = requests.get(url, params=payload)
                print("status code: ", r1.status_code)
                print("content: ", r1.content)
                print("text: ", r1.text)
            except requests.exceptions.RequestException as e:  # This is the error catching syntax
                print(e)
                return Response({"code": "server don't responded properly"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        phoneobject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

