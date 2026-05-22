from django.urls import path
from .views import *

urlpatterns = [
	    path('', index, name="index"),
	    path('contact/submit/', contact_submit, name='contact_submit'),
    ]