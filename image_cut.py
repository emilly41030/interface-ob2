# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from os import walk


scale = 0.3
img_path = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/JPEGImages'
label_path = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/labels'
# out_path = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/scale_jpg'
out_path = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/draw_jpg'
out_path2 = '/home/kelly/Desktop/interface-ob2/dataset/Mura_LCD4/Mura/LCD4/label_jpg'
if not os.path.isdir(out_path):
    os.mkdir(out_path)
if not os.path.isdir(out_path2):
    os.mkdir(out_path2)



def scale_and_draw():
    for (dirpath, dirnames, filenames) in walk(img_path):
        for file in range(len(filenames)):
            positive_count = 0
            arix_list = []

            f_name = filenames[file][:-4]
            print(f_name)
            im = Image.open(img_path+"/"+f_name+".jpg")
            w, h= im.size
            #####   圖片縮小 scale 倍 #####
            im = im.resize((int(w*scale), int(h*scale)),Image.ANTIALIAS)
            rgb_im = im.convert('RGB')
            rgb_im.save(out_path+"/"+f_name+".jpg")
            #############################

            temp = rgb_im.copy()
            # temp = im.copy()
            draw = ImageDraw.Draw(temp)
            # draw = ImageDraw.Draw(im)
            # temp.show()

            with open(label_path+"/"+f_name+".txt") as f:
                lines = f.read().splitlines()

            for i in range(len(lines)):
                arix_list.append(str(lines[i]).split(' '))

            # width, height = im.size
            width, height = rgb_im.size
            dw = 1./(width)
            dh = 1./(height)

            for i in range(len(arix_list)):#每個瑕疵
                x = float(arix_list[i][1])/dw
                w = float(arix_list[i][3])/dw
                y = float(arix_list[i][2])/dh
                h = float(arix_list[i][4])/dh
                xmin = (2*(x+1) - w)/2
                xmax = (2*(x+1) + w)/2
                ymin = (2*(y+1) - h)/2
                ymax = (2*(y+1) + h)/2
            

                draw.line([(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax),(xmin,ymin)], width=4, fill="#ff0000")
                # temp.show()
                temp.save(out_path2+"/"+f_name+".jpg")

            del draw

def draw():
    for (dirpath, dirnames, filenames) in walk(img_path):
            for file in range(len(filenames)):
                positive_count = 0
                arix_list = []

                f_name = filenames[file][:-4]
                print(f_name)
                im = Image.open(img_path+"/"+f_name+".jpg")
                
                temp = im.copy()
                draw = ImageDraw.Draw(temp)
                # draw = ImageDraw.Draw(im)
                # temp.show()

                with open(label_path+"/"+f_name+".txt") as f:
                    lines = f.read().splitlines()

                for i in range(len(lines)):
                    arix_list.append(str(lines[i]).split(' '))

                width, height = im.size
      
                dw = 1./(width)
                dh = 1./(height)

                count = 0
                for i in range(len(arix_list)):#每個瑕疵
                    x = float(arix_list[i][1])/dw
                    w = float(arix_list[i][3])/dw
                    y = float(arix_list[i][2])/dh
                    h = float(arix_list[i][4])/dh
                    xmin = (2*(x+1) - w)/2
                    xmax = (2*(x+1) + w)/2
                    ymin = (2*(y+1) - h)/2
                    ymax = (2*(y+1) + h)/2
                

                    draw.line([(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax),(xmin,ymin)], width=4, fill="#ff0000")
                    # temp.show()
                    temp.save(out_path+"/"+f_name+".jpg")

                del draw
draw()