from django.db import models
from django.conf import settings
import os
# Create your models here.
class imageModel(models.Model):
    """
    Inherits Model class from Django and represents PATIENT IMAGE DETAIL.
    """
    image=models.ImageField(upload_to='images/')
    #imformat=models.CharField(max_length=10)
    timenow=models.DateTimeField(auto_now_add=True)


class patientModel(models.Model):
    """
    Inherits Model class from Django and represents PATIENT DETAILS.
    """
    GENDER_CHOICES = (
        ('m','Male'),
        ('f','Female'),
        ('o','Other'),
    )
    id = models.CharField(primary_key=True,max_length=12)
    name=models.CharField(max_length=50,blank=True)
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES,blank=True)
    doctor=models.CharField(max_length=50,default='chinu')
    timenow=models.DateTimeField(auto_now_add=False)
    patientimage=models.ForeignKey('imageModel',on_delete=models.CASCADE)
    fhirfile=models.TextField(blank=True)
    ccdfile=models.TextField(blank=True)
    ocrfile=models.TextField(blank=True)
    imageids = models.TextField()
    """
    age=models.IntegerField(null=True)
    dateofcollection=models.DateField(auto_now=False,auto_now_add=False,blank=True,null=True)
    birthdate=models.DateField(auto_now=False,auto_now_add=False,blank=True,null=True)
    history=models.CharField(max_length=100,blank=True) """

    def __str__(self):
        return self.name+' '+str(self.timenow)


    
