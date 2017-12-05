import requests
import json

import time
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

from phone.models import ResourceIdGenerator
from .forms import PhoneForm, KeyGeneratorForm, XencallForm

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from phone.models import PhoneData
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


sending_api_info = {

    "first": {
        "sourceName": "first",
    },

    "second": {
        "sourceName": "second",
    },

    "third": {
        "sourceName": "test1",
    },
}

@csrf_exempt
@require_http_methods(["GET", "POST"])
def validate_phone(request,sourceName, sourceId):

    if sourceName == 'xencall':

        if request.method == 'GET':
            vals = request.GET

        else:
            vals = request.POST

        eventtime = time.time()
        errors = {}

        phone = ''
        try:
            phone = vals['phone1'].strip()
        except KeyError:
            errors['phone1'] = "phone number missing"
        campaign = vals.get('campaign', '').strip()

        # Fetch and decode call result object
        result_name =''
        result_abbrev = ''
        try:
            callresult = json.loads(vals['callResult'])
            if not isinstance(callresult, dict):
                errors['callResult'] = '"callResult" parameter is not a JSON object.'

            result_name = callresult.get('Name', '')
            result_abbrev = callresult.get('Abbrev', '')
        except KeyError:
            errors['callResult'] = 'Missing callResult parameter.'
        except json.decoder.JSONDecodeError:
            errors['callResult'] = 'callResult parameter is not JSON encoded.'

        # Fetch and decode call info object.
        info_tpname = ''
        info_tpnumber = ''
        try:
            callinfo = json.loads(vals['callInfo'])
            if not isinstance(callinfo, dict):
                errors['callInfo'] = '"callInfo" parameter is not a JSON object.'
            info_tpname = callinfo.get('X_TPName', '')
            info_tpnumber = callinfo.get('X_TPNumber', '')
        except KeyError:
            errors['callInfo'] = 'Missing callInfo parameter.'
        except json.decoder.JSONDecodeError:
            errors['callInfo'] = 'callInfo parameter is not JSON encoded.'

        # Collect additional info.
        state = vals.get('state', '').strip()
        city = vals.get('city', '').strip()
        zip_ = vals.get('zip', '').strip()
        address = vals.get('address', '').strip()

        if errors:
            return JsonResponse(errors, status=400)

        data = {
            'phone': phone,
            'campaign': campaign,
            'result_name': result_name,
            'result_abbrev': result_abbrev,
            'info_tpname': info_tpname,
            'info_tpnumber': info_tpnumber,
            'eventtime': eventtime,
            'state': state,
            'city': city,
            'zip': zip_,
            'address': address,
        }

        print("data incomming: ",data)

        form = XencallForm({'phone_number':phone, 'key':result_name})
        if form.is_valid():
            print(form.cleaned_data)
            obj = form.save(commit=False)
            obj.source = sourceName + ":" + sourceId
            obj.save()
            return JsonResponse({"code": "phone number saved"}, status=200)

        else:
            return JsonResponse(form.errors, status=400)

    elif sourceName == 'vicidial':

        if request.method == 'GET':
            vals = request.GET

        else:
            vals = request.POST

        eventtime = time.time()
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

        lead_id = vals.get('leadID', '').strip()
        list_id = vals.get('listID', '').strip()
        dispo = vals.get('dispo', '').strip()
        if not dispo:
            errors['dispo'] = 'dispo not provided'

        talk_time = vals.get('talk_time', '').strip()

        if errors:
            return JsonResponse(errors, status=400)

        data = {
            'phone': phone,
            'phoneCode': phonecode,
            'eventtime': eventtime,
            'leadid': lead_id,
            'listid': list_id,
            'dispo': dispo,
            'talkTime': talk_time,
        }

        print("data incomming: ", data)

        form = XencallForm({'phone_number': phone, 'key': dispo})
        if form.is_valid():
            print(form.cleaned_data)
            obj = form.save(commit=False)
            obj.source = sourceName + ":" + sourceId
            obj.save()
            return JsonResponse({"code": "phone number saved"}, status=200)

        else:
            return JsonResponse(form.errors, status=400)

    else:
        return JsonResponse({'error':"unknown provider"},status=400)







# for testing purpose only
# a random form
def test_form(request):
    return render(request,"plain_form.html")

def test_web_form_xencall(request):
    payload = {'phone1': '4876857757',
               'campaign': '74647',
               'callResult': json.dumps({'Name':'Dnc','Abbrev':'dncdb'}),
               'callInfo': json.dumps({'X_TPName':'fdf','X_TPNumber':'98375985'}),
               'state': 'toronto',
               'city': 'ohio',
               'zip': '44102',
               'address': 'wall street'
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
    payload = {'phone_number': '4876857757',
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
