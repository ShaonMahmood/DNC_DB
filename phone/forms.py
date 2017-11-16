from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import PhoneData, ResourceIdGenerator


class PhoneForm(forms.ModelForm):

    class Meta:
        model = PhoneData
        exclude = ['created']

    def clean_phone_number(self):

        import re

        raw_phone_number = self.cleaned_data["phone_number"].strip()

        validated_phone_number = "".join(re.split("\D+",raw_phone_number))

        if len(validated_phone_number) != 10:
            print("invalid phone number")
            raise forms.ValidationError('Invalid phone number, must be 10 digit')

        return self.cleaned_data["phone_number"]

    def clean_key(self):
        accepted_key = self.cleaned_data["key"]
        try:
            re_obj = ResourceIdGenerator.objects.get(resource_id=accepted_key)
        except ObjectDoesNotExist:
            re_obj = None
        if re_obj is None:
            raise forms.ValidationError("Invalid key,ask the provider")
        else:
            return accepted_key





class KeyGeneratorForm(forms.ModelForm):

    class Meta:
        model = ResourceIdGenerator
        exclude = ['created','resource_id']