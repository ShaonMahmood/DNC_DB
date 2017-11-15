from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.home, name='home'),
    url(r'^phone-validation', views.validate_phone, name='phone-validator'),
    url(r'^key-generate',views.key_generate,name='keygeneration'),
    url(r'^test-form',views.test_form,name='test'),
    ]