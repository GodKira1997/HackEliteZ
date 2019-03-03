from django.shortcuts import render,redirect
from .models import imageModel,patientModel
from ocr_mod import ocr_image_reader
from django.conf import settings
import os
from datetime import datetime

def homepage(request):
    return render(request,'mainpages/home.html')

def patient_detail_view(request):
    """
    Creating the person object and returning the parsed data using OCR
    :param request:
    return
    """
    #Image file uploaded 
    imagefile=imageModel.objects.last()
    imgpath=imagefile.image
    imgpath=str(imgpath)
    #Creating the image PATH
    imgpath=os.path.join(settings.MEDIA_ROOT,imgpath)
    print(imgpath)
    
    #JSON data recieved from the OCR library function
    #Reference Link - 
    ocr_processed_patient_detail=ocr_image_reader(imgpath)

    patient_object_data={
        'imagefile':imagefile,
        'FHIR':ocr_processed_patient_detail['FHIR'],
        'CCD':ocr_processed_patient_detail['CCD'],
        'OCR':ocr_processed_patient_detail['OCR'],
    }
    aadhar_num=ocr_processed_patient_detail['FHIR']['patient']['aadhar']

    fhirname="fhir"+str(imagefile.pk)+".json"
    fhirname='documents/json/'+fhirname
    fhirname=os.path.join(settings.MEDIA_ROOT,fhirname)
    f=open(fhirname,'w+')
    f.write(str(ocr_processed_patient_detail['FHIR']))
    f.close()

    ccdname="ccd"+str(imagefile.pk)+".xml"
    ccdname='documents/xml/'+ccdname
    ccdname=os.path.join(settings.MEDIA_ROOT,ccdname)
    f=open(ccdname,'w+')
    f.write(str(ocr_processed_patient_detail['CCD']))
    f.close()

    ocrname="ocr"+str(imagefile.pk)+".txt"
    ocrname='documents/txt/'+ocrname
    ocrname=os.path.join(settings.MEDIA_ROOT,ocrname)
    f=open(ocrname,'w+')
    f.write(str(ocr_processed_patient_detail['OCR']))
    f.close()
    print('adaar_num=',aadhar_num)
    if(patientModel.objects.filter(id = aadhar_num)):
        patient_object = patientModel.objects.get(id = aadhar_num)
        patient_object.fhirfile +=" "+fhirname
        patient_object.ccdfile +=" "+ccdname
        patient_object.ocrfile +=" "+ocrname
        patient_object.imageids +=" "+str(imagefile.id)
        patient_object.save()      
    else:
        patient_object=patientModel()
        patient_object.id=ocr_processed_patient_detail['FHIR']['patient']['aadhar']
        patient_object.name=ocr_processed_patient_detail['FHIR']['patient']['name'].strip()
        #pat.gender=ocr_processed_patient_detail['patient']['sex']
        patient_object.doctor=ocr_processed_patient_detail['FHIR']['patient']['doctor'].strip()
        patient_object.timenow=datetime.now()
        patient_object.patientimage=imagefile
        patient_object.fhirfile=fhirname
        patient_object.ccdfile=ccdname
        patient_object.ocrfile=ocrname
        patient_object.imageids=str(imagefile.id)
        patient_object.save()
    print('name=',ocr_processed_patient_detail['FHIR']['patient']['name'])
    return render(request,'mainpages/patientdetail.html',patient_object_data)


def formpage(request):
    """
    Handling requests from the main webpage
    :param request:
    return 
    """
    if request.method == 'POST':
        image_object_patient_data=imageModel()
        image_object_patient_data.image = request.FILES['imgdoc']
        image_object_patient_data.save()
        return redirect('patientdetailpage')
    else:    
        return render(request,'mainpages/form.html')