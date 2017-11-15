from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from phone.models import ResourceIdGenerator
from .forms import PhoneForm,KeyGeneratorForm
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

        key = request.POST.get('key',"")

        if key:
            try:
                re_obj = ResourceIdGenerator.objects.get(resource_id=key)
            except ObjectDoesNotExist:
                re_obj = None

            if re_obj is None:
                return JsonResponse({"code":"Not applicable"},status=400)
            else:
                # create a form instance and populate it with data from the request:
                form = PhoneForm(request.POST)
                # check whether it's valid:
                if form.is_valid():

                    # process the data in form.cleaned_data as required
                    print(form.cleaned_data)
                    obj = form.save(commit=False)
                    obj.resource_id_generator = re_obj
                    form.save()
                    return JsonResponse({"code": "phone number saved"}, status=200)
                else:
                    return JsonResponse(form.errors, status=400)

        else:
            return JsonResponse({"code": "Not applicable"}, status=400)


# for testing purpose only
# a random form
def test_form(request):
    return render(request,"plain_form.html")

