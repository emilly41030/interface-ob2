import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import sys

classes=[]
for i in range(3, len(sys.argv)):
    classes.append(sys.argv[i])
source_folder=sys.argv[1]
folder_name = source_folder.split('/')
sets=[(folder_name[-2], 'train'), (folder_name[-2], 'val')]

# source_folder='/home/kelly/data/Dataset/Mura/LCD4/JPEGImages'
def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(ID, image_id):    
    in_file = open(os.path.dirname(source_folder)+'/Annotations/%s.xml'%(image_id))
    out_file = open(os.path.dirname(source_folder)+'/labels/%s.txt'%(image_id), 'w')
    # in_file = open('Mura/LCD%s/Annotations/%s.xml'%(ID, image_id))
    # out_file = open('Mura/LCD%s/labels/%s.txt'%(ID, image_id), 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

for ID, image_set in sets:
    if not os.path.exists(os.path.dirname(source_folder)+'/labels/'):
        os.makedirs(os.path.dirname(source_folder)+'/labels/')
    image_ids = open(os.path.dirname(source_folder)+'/ImageSets/Main/%s.txt'%(image_set)).read().strip().split()
    list_file = open(os.getcwd()+'/dataset/%s/%s_%s.txt'%(sys.argv[2], ID, image_set), 'w')
    for image_id in image_ids:
        list_file.write(os.path.dirname(source_folder)+'/JPEGImages/%s.jpg\n'%(image_id))
        convert_annotation(ID, image_id)
    list_file.close()
print("voc_finish!!!!!")

