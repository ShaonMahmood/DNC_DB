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

    if sourceName == 'xencall':

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

            print("data incomming: ",data)

            form = XencallForm({'phone_number':phone, 'key':result, 'backup_phone':backupphone})
            if form.is_valid():
                apiLength = len(settings.API_SENDING_LIST)
                apiList = settings.API_SENDING_LIST
                print(form.cleaned_data)
                obj = form.save(commit=False)
                obj.source = sourceName + "-" + sourceId + "-" + source


                with transaction.atomic():
                    obj.save()
                    for i in range(0,apiLength):
                        ApiSending.objects.create(destination=apiList[i], phoneobject=obj)

                return JsonResponse({"code": "phone number sucessfully saved"}, status=200)

            else:
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

            print("data incomming: ", data)

            form = VicidialForm({'phone_number': phone, 'key': dispo})
            if form.is_valid():
                apiLength = len(settings.API_SENDING_LIST)
                apiList = settings.API_SENDING_LIST
                print(form.cleaned_data)
                obj = form.save(commit=False)
                obj.source = sourceName + "-" + sourceId + "-" + source
                obj.save()

                with transaction.atomic():
                    obj.save()
                    for i in range(0,apiLength):
                        ApiSending.objects.create(destination=apiList[i], phoneobject=obj)

                return JsonResponse({"code": "phone number successfully saved"}, status=200)

            else:
                return JsonResponse(form.errors, status=400)

    else:
        return JsonResponse({'error':"unknown provider"},status=400)







# for testing purpose only
# a random form
def test_form(request):
    return render(request,"plain_form.html")

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

