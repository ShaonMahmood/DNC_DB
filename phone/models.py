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


class PhoneData(models.Model):

    source = models.CharField(
        max_length=200,
        null=True,blank=True
    )

    resource_id_generator = models.ForeignKey(
        ResourceIdGenerator,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=15
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ('created',)









