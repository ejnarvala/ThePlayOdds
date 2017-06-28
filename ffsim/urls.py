from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^contact/$',views.contact, name='contact'),
    url(r'^results/$',views.submit_local, name='submit_local'),
    url(r'^simcall/',views.simcall, name='simcall'),
    ]
