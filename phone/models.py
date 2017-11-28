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

    number_delivered = models.BooleanField(
        default = False
    )

    class Meta:
        ordering = ('created',)









