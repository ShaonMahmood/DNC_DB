from django.db import models
from django.core.validators import URLValidator
# Create your models here.


class ResourceIdGenerator(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name= "security_key_name"
    )

    resource_id = models.CharField(
        max_length=200
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "resource"


class PhoneData(models.Model):

    source = models.CharField(
        max_length=200,
        null=True,blank=True
    )

    key = models.CharField(
       max_length=200
    )

    phone_number = models.CharField(
        max_length=15,
        db_index=True,
    )

    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    # vicidial_tcm_delivered = models.BooleanField(
    #     default=False
    # )
    #
    # vicidial_tcm_attempt = models.IntegerField(
    #     default=0,
    #     blank=True
    # )
    #
    # vicidial_eagent_delivered = models.BooleanField(
    #     default=False
    # )
    #
    # vicidial_eagent_attempt = models.IntegerField(
    #     default=0,
    #     blank=True
    # )
    #
    # xencall_delivered = models.BooleanField(
    #     default=False
    # )
    #
    # xencall_attempt = models.IntegerField(
    #     default=0,
    #     blank=True
    # )
    #
    # number_delivered = models.BooleanField(
    #     default = False
    # )

    backup_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.source + " : " + self.phone_number

    class Meta:
        ordering = ('-created',)
        verbose_name = "phone_data"


class ApiSending(models.Model):

    destination = models.CharField(
        max_length=30
    )

    phoneobject = models.ForeignKey(
        PhoneData,
        on_delete=models.CASCADE
    )

    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    attempt_time = models.DateTimeField(
        blank=True,
        null=True
    )

    delivered = models.BooleanField(
        default=False
    )

    delivered_time = models.DateTimeField(
        blank=True,
        null=True
    )

    attempt_count = models.IntegerField(
        default=0,
        blank=True
    )

    def __str__(self):
        return self.destination

    class Meta:
        ordering = ('-created',)
        verbose_name = "api_sending"



class API_CONFIG(models.Model):

    name = models.CharField(
        max_length=100
    )

    user = models.CharField(
        max_length=100
    )

    password = models.CharField(
        max_length=50
    )

    url = models.TextField(
        validators=[URLValidator()]
    )

    def __str__(self):
        return self.name