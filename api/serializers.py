from rest_framework import serializers
from rest_framework import exceptions
from django.conf import settings
from mainapp.models import imageModel

class ImageModelSerializer(serializers.ModelSerializer):
    image=serializers.ImageField(max_length=None,use_url=True)
    class Meta:
        model=imageModel
        fields='__all__'