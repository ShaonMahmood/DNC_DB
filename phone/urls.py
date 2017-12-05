from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns1 = [
    url(r'^$',views.home, name='home'),

    url(r'^api/(?P<sourceName>[a-z0-9]+)/(?P<sourceId>[a-z0-9]+)/$', views.validate_phone, name='phone-validator'),

    url(r'^key-generate',views.key_generate,name='keygeneration'),
    url(r'^test-form',views.test_form,name='test'),
    url(r'^test-web-form-xencall',views.test_web_form_xencall,name='testwebformxencall'),
    url(r'^test-web-form-vicidial',views.test_web_form_vicidial,name='testwebformvicidial'),
    ]

urlpatterns2 = [
    url(r'^api/numberlist/$', views.number_list),
    url(r'^api/number/(?P<pk>[0-9]+)/$', views.number_detail),
]

urlpatterns2 = format_suffix_patterns(urlpatterns2)

urlpatterns = urlpatterns1 + urlpatterns2