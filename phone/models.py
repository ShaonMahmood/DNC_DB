from django.db import models

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


class PhoneData(models.Model):

    source = models.CharField(
        max_length=200,
        null=True,blank=True
    )

    key = models.CharField(
       max_length=200
    )

    phone_number = models.CharField(
        max_length=15
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    vicidial_tcm_delivered = models.BooleanField(
        default=False
    )

    vicidial_tcm_attempt = models.IntegerField(
        default=0,
        blank=True
    )

    vicidial_eagent_delivered = models.BooleanField(
        default=False
    )

    vicidial_eagent_attempt = models.IntegerField(
        default=0,
        blank=True
    )

    xencall_delivered = models.BooleanField(
        default=False
    )

    xencall_attempt = models.IntegerField(
        default=0,
        blank=True
    )

    number_delivered = models.BooleanField(
        default = False
    )

    backup_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.source + " : " + self.phone_number

    class Meta:
        ordering = ('created',)








