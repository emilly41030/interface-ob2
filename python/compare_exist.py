# -*- coding: utf-8 -*-
import os
from os import walk


img_path = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/JPEGImages'
label_path = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/Annotations'


for (dirpath, dirnames, filenames) in walk(label_path):
    for file in filenames:
        f = file.split('.')[0]        
        img_F = os.listdir(img_path)
        img_format = img_F[0].split('.')[-1]
        f = f+"."+img_format
        if f in img_F:
            pass
        else:
            print("!!!!!!"+file)
            os.remove(file)