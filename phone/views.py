import requests
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

from phone.models import ResourceIdGenerator
from .forms import PhoneForm,KeyGeneratorForm

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


@csrf_exempt
def validate_phone(request):
    if request.method == 'POST':

        print(request.POST)
        form = PhoneForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            print(form.cleaned_data)
            payload = {'source': 'test','phone_code':'1', 'list_id':'999', 'user': '6666', 'pass':'1234',
                       'function':'add_lead', 'phone_number':form.cleaned_data['phone_number']}
            url = "http://tcm.ytel.com/x5/api/non_agent.php"
            #r1= requests.get(url,params=payload)

            try:
                r1 = requests.get(url, params=payload)
                print("status code: ", r1.status_code)
                print("content: ", r1.content)
                print("text: ", r1.text)
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print(e)

            obj = form.save(commit=False)
            obj.save()
            return JsonResponse({"code": "phone number saved"}, status=200)
        else:
            return JsonResponse(form.errors, status=400)




# for testing purpose only
# a random form
def test_form(request):
    return render(request,"plain_form.html")



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
                print("text: ", r1.text)
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
