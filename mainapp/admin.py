from django.contrib import admin
from .models import imageModel,patientModel
# Register your models here.
admin.site.register(imageModel)
admin.site.register(patientModel)