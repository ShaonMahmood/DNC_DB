from django import forms
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


class KeyGeneratorForm(forms.ModelForm):

    class Meta:
        model = ResourceIdGenerator
        exclude = ['created','resource_id']