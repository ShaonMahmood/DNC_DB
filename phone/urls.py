from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns1 = [
    url(r'^$',views.home, name='home'),
    url(r'^phone-validation', views.validate_phone, name='phone-validator'),
    url(r'^key-generate',views.key_generate,name='keygeneration'),
    url(r'^test-form',views.test_form,name='test'),
    ]

urlpatterns2 = [
    url(r'^api/numberlist/$', views.number_list),
    url(r'^api/number/(?P<pk>[0-9]+)/$', views.number_detail),
]

urlpatterns2 = format_suffix_patterns(urlpatterns2)

urlpatterns = urlpatterns1 + urlpatterns2