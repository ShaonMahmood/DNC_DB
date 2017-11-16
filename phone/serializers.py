from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import PhoneData, ResourceIdGenerator


class PhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhoneData
        fields = ('id', 'phone_number','key')

    def validate_phone_number(self,value):
        import re

        raw_phone_number = value.strip()

        validated_phone_number = "".join(re.split("\D+", raw_phone_number))

        if len(validated_phone_number) != 10:
            print("invalid phone number")
            raise serializers.ValidationError('Invalid phone number, must be 10 digit')

        return value

    def validate_key(self,value):
        accepted_key = value
        try:
            re_obj = ResourceIdGenerator.objects.get(resource_id=accepted_key)
        except ObjectDoesNotExist:
            re_obj = None
        if re_obj is None:
            raise serializers.ValidationError("Invalid key,ask the provider")
        else:
            return accepted_key