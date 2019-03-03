from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import ImageModelSerializer
from mainapp.models import imageModel
from rest_framework.response import Response
from ocr_mod import ocr_image_reader
from django.conf import settings
import os

# Create your views here.
class ImageModelAPIView(CreateAPIView):
    queryset=imageModel.objects.all()
    serializer_class=ImageModelSerializer  
    def post(self,request):
        data=request.data
        image=data.get('image')
        #imformat=data.get('imformat')
        #remark=data.get('remark')
        print(image)   
        if image:
            im=imageModel.objects.create()
            im.image=image
            im.save()
            #im.imformat=imformat
            imgpath=str(image)
            imgpath=os.path.join(os.path.join(settings.MEDIA_ROOT,'images'),imgpath)
            print(imgpath)
            result=ocr_image_reader(imgpath)
            
            return Response({'status':result['OCR']}) 
        else:
            return Response({'status':'Failure of image store'})   

