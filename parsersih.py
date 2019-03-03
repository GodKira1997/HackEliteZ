import unicodedata
import re
import string
import json
from django.conf import settings
import os
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
import xml.dom.minidom as xmd

ocroutput = "output.txt"
dictionary={
	'name':['name of the patient','name of patient','patient name','patient','name'],
	'referred':['referred by','ref. by'],
	'age':['age'],
	'date':['date of collection','date'],
	'dob':['date of birth','dob'],
	'sex':['sex','gender'],
	'sino':['file no'],
	'labno':['lab no'],
	'history':['history'],
}
table = []
worddict={}

#Function for text preprocessing
def process(text):
	text = text.lower()
	text = re.sub(r':', '',text)
	text = re.sub(r'[^a-z0-9/., ]', '',text)
	return text

#Function for extracting useful keys
def extract(sentence,lineNo):
	for key in dictionary.keys():
		for item in dictionary[key]:
			index=sentence.find(item)
			if index!=-1:
				table.append([str(key),int(lineNo),int(index),int(index)+int(len(item))])
				break

def create_ccd():
	composition=ET.Element("composition")
	ET.SubElement(composition,"date", value=worddict["date"])
	ET.SubElement(composition,"title", value="Continuity of Care Document")
	ET.SubElement(composition,"status", value="preliminary")
	subject=ET.SubElement(composition,"subject")
	ET.SubElement(subject,"display", value=worddict["name"])
	author=ET.SubElement(composition,"author")
	ET.SubElement(author,"display", value=worddict["referred"])
	attester=ET.SubElement(composition,"attester")
	ET.SubElement(attester,"mode",value="legal")
	party=ET.SubElement(attester,"party")
	ET.SubElement(party,"display",value=worddict["referred"])
	section=ET.SubElement(composition,"section")
	ET.SubElement(section,"title",value="report")
	tree=ET.ElementTree(composition)
	name=worddict["name"]
	name+=".xml"
	filepath="/home/chinu/datadigitizer-project/outputdocs/"
	filepath=os.path.join(filepath,name)
	tree.write(filepath)
	xmlstr = ElementTree.tostring(composition, encoding='utf8', method='xml')
	dom=xmd.parseString(xmlstr)
	pretty_xml=dom.toprettyxml()
	print("xml created successfuly")
	return pretty_xml

def parser():
	global table
	#Reading File line by lineto extract keys (PASS - 1)
	with open(ocroutput) as openfile:
		lineNo = 0
		for line in openfile:
			line = process(line)
			extract(line,lineNo)
			lineNo += 1
	openfile.close()

	#Sort the table according to lineNo & index
	table = sorted(table, key = lambda x: (x[1], x[2]))

	#Check DOB
	for i in range(len(table)):
		if table[i][0] == 'dob':
			if table[i - 1][0] == 'date':
				table.remove(table[i - 1])
			else:
				table.remove(table[i + 1])


	#Open the OCR Output again
	openfile = open(ocroutput,'r')
	lines = openfile.read().split('\n')
	for i in range(len(lines)):
		lines[i] = process(lines[i])
	openfile.close()

	#Creating Dictionary using the lookup table (PASS - 2)
	for row in range(len(table)):
		line = lines[table[row][1]]
		key = table[row][0]
		if row < len(table) - 1:
			if table[row][1] == table[row + 1][1]:
				worddict[key] = line[table[row][3]:table[row + 1][2]]
			else:
				worddict[key] = line[table[row][3]:len(line)]
		else:
			worddict[key] = line[table[row][3]:len(line)]

	#worddict['sex']=worddict['sex'].strip()
	#if worddict['sex']:
		#worddict['sex']=worddict['sex'][0] 
	#print(table)
	print(worddict)		

	#Page Segmentation
	seperatorLine1 = table[0][1]
	seperatorLine2 = table[-1][1]
	openfile = open(ocroutput,'r')
	lines = openfile.read().split('\n')
	name = worddict['name'].strip()

	headerfile = open(name + "header",'w+')
	for i in range(seperatorLine1):
		headerfile.write(lines[i] + "\n")
	headerfile.close()

	#Creating report file
	reportfile = open(name + "report",'w+')
	for i in range(seperatorLine2 + 1,len(lines)):
		reportfile.write(lines[i] + "\n")
	reportfile.close()
	openfile.close()

	filename=name+'report'
	fhir={}
	fhir['patient']=worddict
	fhir['report']={}
	fhir['report']['location'] = os.path.join(settings.BASE_DIR,filename) 
	#Creating json
	print(fhir)
	result=json.dumps(fhir,indent=4)
	fhir=json.loads(result)
	#print("result: ",result)
	tree=create_ccd()
	parser_out={}
	parser_out['jsonout']=fhir
	parser_out['tree']=tree
	return parser_out


