# import the necessary packages
from PIL import Image, ImageEnhance
import pytesseract
import argparse
import cv2
import os
import numpy as np
import enchant
from nltk.metrics import edit_distance
from django.conf import settings
#from parsersih import parser
from newparser import ocr_data_parser

def maximizeContrast(imgGrayscale):
    height, width = imgGrayscale.shape

    imgTopHat = np.zeros((height, width, 1), np.uint8)
    imgBlackHat = np.zeros((height, width, 1), np.uint8)

    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    imgTopHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_TOPHAT, structuringElement)
    imgBlackHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_BLACKHAT, structuringElement)

    imgGrayscalePlusTopHat = cv2.add(imgGrayscale, imgTopHat)
    imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

    return imgGrayscalePlusTopHatMinusBlackHat


# end function

class SpellingReplacer(object):
    def __init__(self, dict_name='en_GB', max_dist=2):
        self.spell_dict = enchant.Dict(dict_name)
        self.max_dist = 2

    def replace(self, word):
        fpath=os.path.join(settings.MEDIA_ROOT,'documents')
        fpath=os.path.join(fpath,'medical_dictionary.txt')
        fobj = open(fpath)
        text = fobj.read().strip().split()
        s = word
        if s in text:
            return word
        else:
            if self.spell_dict.check(word):
                return word
            suggestions = self.spell_dict.suggest(word)

            if suggestions and edit_distance(word, suggestions[0]) <= self.max_dist:
                return suggestions[0]
            else:
                return word

        fobj.close()


def spell_check(word_list):
    checked_list = []
    for item in word_list:
        replacer = SpellingReplacer()
        r = replacer.replace(item)
        checked_list.append(r)
    return checked_list

def ocr_image_reader(image):


    # construct the argument parse and parse the arguments
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-i", "--image", required=True, help="path to input image to be OCR'd")
    #ap.add_argument("-p", "--preprocess", type=str, default="thresh", help="type of preprocessing to be done")
    #args = vars(ap.parse_args())

    # load the example image and convert it to grayscale
    image = cv2.imread(image)
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # pil_im = Image.fromarray(image)
    # imag=ImageEnhance.Contrast(pil_im)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray=maximizeContrast(gray)
    #gray=cv2.bitwise_not(gray)

    # check to see if we should apply thresholding to preprocess the
    # image
    #if args["preprocess"] == "thresh":

    # gray=cv2.GaussianBlur(gray,(3,3),1)
    gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # gray = cv2.adaptiveThreshold(gray.astype(np.uint8),255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,9,41)
    # kernel=np.ones((2,2),np.uint8)
    # closing=cv2.morphologyEx(gray,cv2.MORPH_CLOSE,kernel)
    # closing = cv2.medianBlur(gray,3)
    # closing = cv2.medianBlur(gray,3)
    # gray=closing
    # print("fd")

    # kernel=np.ones((3,3),np.uint8)
    # opening=cv2.morphologyEx(gray,cv2.MORPH_OPEN,kernel)
    # out=gray
    # out=cv2.dilate(gray,kernel,iterations=3)
    # closing=cv2.morphologyEx(opening,cv2.MORPH_CLOSE,kernel)
    # gray=image_smoothening(gray)
    #	gray=cv2.bitwise_or(gray,closing)
    # gray=cv2.GaussianBlur(gray,(3,3),1)
    # gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # out=gray
    # gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # gray=cv2.GaussianBlur(gray,(5,5),0)

    # make a check to see if median blurring should be done to remove
    # noise
    #elif args["preprocess"] == "blur":
    #gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temporary file so we can
    # apply OCR to it
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    # cv2.imshow("closing",closing)


    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    # text = pytesseract.image_to_string(Image.open(filename))
    # os.remove(filename)
    # print(text)

    # show the output images

    #cv2.imshow("Image", image)
    #cv2.imshow("Output", gray)
    #cv2.waitKey(0)

    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    text = pytesseract.image_to_string(Image.open(filename), config='-c preserve_interword_spaces=1')
    print(text)
    #f=open("output.txt","w")
    #f.write(text)
    #f.close()
    os.remove(filename)
    """
        word_list = []
        for line in text.split('\n'):
            for word in line.split():
                word_list.append(word)
                sr = sr + "".join(spell_check(word.split())) + " "
            sr = sr + "\n"
                #print(word_list)
        #print(spell_check(word_list))
    """

    #print(sr)
    #parser_out=parser()
    #path="/home/chinu/datadigitizer-project/outputdocs/"
    #name=parser_out['jsonout']['patient']['name'].strip()
    #name+=".txt"
    #path=os.path.join(path,name)
    f = open("output.txt", "w+")
    f.write(text)
    f.close()
    parser_out=ocr_data_parser("output")
    #cv2.destroyAllWindows()
    #return text
    ocr_out={}
    ocr_out['OCR']=text
    ocr_out['FHIR']=parser_out['jsonout']
    ocr_out['CCD']=parser_out['tree']
    return ocr_out
