from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from phone.models import ResourceIdGenerator
from .forms import PhoneForm,KeyGeneratorForm

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
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
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        phoneobject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
