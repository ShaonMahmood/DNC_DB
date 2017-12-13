from django.apps import apps
from django.contrib import admin

# Register your models here.
from django.contrib.admin.sites import AlreadyRegistered


class PhoneDataAdmin(admin.ModelAdmin):
    list_display = ["source","phone_number","created"]


class ApiSendingAdmin(admin.ModelAdmin):
    list_display = ["destination","phoneobject","delivered","attempt_time","attempt_count","created"]


model_admin_dict = {
    "phone_data":PhoneDataAdmin,
    "api_sending":ApiSendingAdmin
}

app_models = apps.get_app_config('phone').get_models()
for model in app_models:
    try:
        try:
            admin.site.register(model, model_admin_dict[model._meta.verbose_name])
        except KeyError:
            admin.site.register(model)
    except AlreadyRegistered:
        pass

