import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
import xml.dom.minidom as xmd
from django.conf import settings
import os


data_forms_mapping={
    'name':['name of the patient','name of patient','patient name','claimant name','patient','name','claimant'],
    'referred':['referred by','ref. by','refby','refd.by.','doctor', 'dr.' ,'md:' ,'dr:' , 'from whom was treatment'  ],
    'age':['age'],
    'date':['date received','date of collection','date'],
    'dob':['date of birth','dob'],
    'sex':['sex','gender'],
    'sino':['file no'],
    'labno':['lab no'],
    'history':['history'],
    "aadhar":["aadhar number" , "aadharnumber", "aadharnum" , "aadharid", "aadhar_id" , "aadhar"]
}
worddict={}
seperators = [':' , "-" , "|" , "_"]

numarray = [str(i) for i in range(100,0,-1)]

def num(line):
    for age in numarray:
        if(age in line):
            return age
    return ""
            
def preprocessor(input_data):
    """
    This function cleans the OCR data
    :param input_data:
    return pre_processed_data
    """
    final_data = ""
    for line in input_data.splitlines():
        final_data += line.strip() + "\n"
    input_data = final_data
    #Push Arbitrary Spacing to new line i.e 2 or more
    input_data = re.sub(r" [' ']+","\n",input_data)
    input_data = re.sub(r'[^\x00-\x7f]',r'', input_data)
    input_data_list = input_data.splitlines()       
    #Collapsing the new lines into one new line
    input_data = re.sub(r"\n+","\n",input_data).strip()       
    return input_data.lower()


################################################
############# GETS TO GENERATE #################
############# DICTIONARY KEYS  #################
################################################

def get_name(input_data):
    input_data = input_data.split("\n")
    name = ["",0]
    value = 0
    indexer = 0
    #print input_data
    #extracted the line from which has name or previous line
    for line in input_data:
        flag = 0
        for tag in data_forms_mapping['name']:
            if(tag in line):
                name[0] = line
                name[1] = indexer
                flag = 1
        if(flag):
            break
        curr_value = max(fuzz.ratio(line, tags) for tags in data_forms_mapping['name'])
        if(curr_value > value):
            value = curr_value
            name[0] = line
            name[1] = indexer
        indexer+=1
    #print name
    for tag in data_forms_mapping['name']:
        name[0]=name[0].replace(tag , "")    
    name[0] = name[0].strip()        
    for i in seperators:
        name[0]=name[0].replace(i, "")    
    if(name[0] == "" or len(name[0])<= 3):
        name[0] = input_data[name[1]+1]    
    return name[0]


def get_doctor(input_data):
    input_data = input_data.split("\n")
    while('.' in input_data):
        input_data.remove('.')
    for i in seperators:
        while(i in input_data):
            input_data.remove(i)
    doctor = ["",0]
    value = 0
    indexer = 0
    #extracted the line from which has name or previous line
    for line in input_data:
        flag = 0
        for tag in data_forms_mapping['referred']:
            if(tag in line):
                doctor[0] = line
                doctor[1] = indexer
                flag = 1
                break
        if(flag):
            break
        curr_value = max(fuzz.ratio(line, tags) for tags in data_forms_mapping['referred'])
        if(curr_value > value):
            value = curr_value
            doctor[0] = line
            doctor[1] = indexer
        indexer+=1
    #print doctor
    for tag in data_forms_mapping['referred']:
        doctor[0]=doctor[0].replace(tag , "")    
    doctor[0] = doctor[0].strip()        
    for i in seperators:
        doctor[0]=doctor[0].replace(i, "")    
    if(doctor[0] == "" or len(doctor[0]) == 1 ):
        doctor[0] = input_data[doctor[1]+1]
    if(doctor[0].count(" ")>=3):
        return ""   
    return doctor[0]
    

def get_age(input_data):
    input_data = input_data.split("\n")
    age_ends = ["months" , "yrs" , "yr" , "days"]
    counter = 0
    age = ""
    for line in input_data:
        if('age' in line):
            break        
        counter+=1
    
    for i in range(counter+1,len(input_data)):
        age = num(input_data[i])
        
        if(age!=""):
            break      
    return age     

def get_date(input_data):
    #coz there are mutliple dates
    date_arr = re.findall(r"[0-9][0-9][\/|\-][0-9][0-9][\/|\-][1-9][0-9]+" , input_data)
    
    return ' '.join(date_arr)
    
def get_sex(input_data):
    input_data = input_data.split("\n")
    gender = ""
    indexer = 0
    #extracted the line from which has name or previous line
    flag=0
    for line in input_data:
        if "sex" in line or "gender" in line:
            flag=1	
            break
        indexer+=1
    if flag==0:
    	return gender
    if "sex" in input_data[indexer] :
        gender = input_data[indexer].replace("sex","")
    elif "gender" in input_data[indexer] :
        gender = input_data[indexer].replace("gender","")
    for i in seperators:
        gender=gender.replace(i, "")
    gender = gender.strip()
    if len(gender)==0:
        gender = input_data[indexer+1]
    return gender 

def get_sino(input_data):
    input_data = input_data.split("\n")	
    sino = ""
    indexer = 0
    flag=0
    for line in input_data:
        if "file no" in line:
            flag=1
            break
        indexer+=1
    if flag==0:
        return sino
    sino = input_data[indexer+1]    
    for i in seperators:
        sino=sino.replace(i, "")    
    return sino.strip()

def get_labno(input_data):
    input_data = input_data.split("\n")		
    labno = ""
    indexer = 0
    flag=0
    for line in input_data:
        if "lab no" in line:
            flag=1
            break
        indexer+=1
    if flag==0:
        return labno
    labno = input_data[indexer+1]    
    for i in seperators:
        labno=labno.replace(i, "")       
    return labno.strip()


def create_ccd(worddict):
    print("in ccd=",worddict)
    composition=ET.Element("composition")
    if 'date' in worddict:
        ET.SubElement(composition,"date", value=worddict["date"])
    else:
        ET.SubElement(composition,"date", value="")

    ET.SubElement(composition,"title", value="Continuity of Care Document")
    ET.SubElement(composition,"status", value="preliminary")
    subject=ET.SubElement(composition,"subject")

    if 'name' in worddict:
	    ET.SubElement(subject,"display", value=worddict["name"])
    else:
        ET.SubElement(subject,"display", value="e")

    author=ET.SubElement(composition,"author")    
    if 'doctor' in worddict:
	    ET.SubElement(author,"display", value=worddict["doctor"])
    else:
        ET.SubElement(author,"display", value="e")
    
    attester=ET.SubElement(composition,"attester")
    ET.SubElement(attester,"mode",value="legal")
    party=ET.SubElement(attester,"party")
    if 'doctor' in worddict:
	    ET.SubElement(party,"display", value=worddict["doctor"])
    else:
        ET.SubElement(party,"display", value="")
    
    section=ET.SubElement(composition,"section")
    ET.SubElement(section,"title",value="report")
    tree=ET.ElementTree(composition)
    #name=worddict["name"]
    #name+=".xml"
    name="output.xml"
    filepath="/home/chinu/datadigitizer-project/outputdocs/"
    filepath=os.path.join(filepath,name)
    tree.write(filepath)
    xmlstr = ElementTree.tostring(composition, encoding='utf8', method='xml')
    dom=xmd.parseString(xmlstr)
    pretty_xml=dom.toprettyxml()
    print("xml created successfuly")
    return pretty_xml

def get_aadhar(input_data):
    input_data = input_data.split("\n")
    aadhar = ["",0]
    value = 0
    indexer = 0
    #print input_data
    #extracted the line from which has name or previous line
    for line in input_data:
        flag = 0
        for tag in data_forms_mapping['aadhar']:
            if(tag in line):
                aadhar[0] = line
                aadhar[1] = indexer
                flag = 1
        if(flag):
            break
        curr_value = max(fuzz.ratio(line, tags) for tags in data_forms_mapping['aadhar'])
        if(curr_value > value):
            value = curr_value
            aadhar[0] = line
            aadhar[1] = indexer
        indexer+=1
    #print name
    for tag in data_forms_mapping['aadhar']:
        aadhar[0]=aadhar[0].replace(tag , "")    
    aadhar[0] = aadhar[0].strip()        
    for i in seperators:
        aadhar[0]=aadhar[0].replace(i, "")    
    if(aadhar[0] == "" or len(aadhar[0])<= 3):
        aadhar[0] = input_data[aadhar[1]+1]    
    return aadhar[0]
     

def ocr_data_parser(filename):
    """
    This will generate the keys in data_required_and_their_forms_mapping dictionary
    :param file_name:
    return key:value pairs
    """
    file_handle = open(filename+".txt" , "r")
    #file_handle1 = open( filename+"p.txt", "r")
    input_data = file_handle.read()
    pre_processed_data = preprocessor(input_data)
    
    #file_handle1.write(pre_processed_data)
    
    name = get_name(pre_processed_data)
    print(name)

    doctor = get_doctor(pre_processed_data)
    print(doctor)

    age = get_age(pre_processed_data)
    print(age)

    
    date = get_date(pre_processed_data)
    print(date)
    
    sex = get_sex(pre_processed_data)
    print(sex)

    sino = get_sino(pre_processed_data)
    print(sino)

    labno = get_labno(pre_processed_data)
    print(labno)

    aadhar = get_aadhar(pre_processed_data)
    print(aadhar)
    
    # we have not implemented history
    #history = get_history(pre_processed_data)
    
    print("#########")
    worddict = {'name':name ,'aadhar':aadhar ,'doctor':doctor , 'age':age , 'sex':sex, 'sino':sino , 'labno': labno ,'date':date}
    print(worddict)
    fhir={}
    fhir['patient']=worddict
    fhir['report']={}
    fhir['report']['location'] = os.path.join(settings.BASE_DIR,"output.txt")
    tree=create_ccd(worddict)
    parser_out={}
    parser_out['jsonout']=fhir
    parser_out['tree']=tree
    print(parser_out)
    return parser_out
#ocr_data_parser(r"adhaar")    
#file_names = ['27_handwritten', 'sdd', 'omega', 'dorm', 'medical', '28_handwritten']
#for i in file_names: