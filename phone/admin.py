from django.apps import apps
from django.contrib import admin

# Register your models here.
from django.contrib.admin.sites import AlreadyRegistered


class PhoneDataAdmin(admin.ModelAdmin):
    list_display = ["source","phone_number","created"]


class ApiSendingAdmin(admin.ModelAdmin):
    list_display = ["destination","phoneobject","delivered","attempt_time"]


app_models = apps.get_app_config('phone').get_models()
for model in app_models:
    try:
        if model._meta.verbose_name == "phone_data":
            admin.site.register(model,PhoneDataAdmin)

        elif model._meta.verbose_name == "api_sending":
            admin.site.register(model,ApiSendingAdmin)

        else:
            admin.site.register(model)
    except AlreadyRegistered:
        pass

