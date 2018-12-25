# -*- coding: utf-8 -*-
import os
from os import listdir
import subprocess
import signal
import time
from shutil import copyfile
import sys
import json

############## voc_label ##############
import xml.etree.ElementTree as ET
import pickle
import os

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

def convert_annotation(ID, image_id, source_folder, classes):    
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

def voc_label(source_folder, datasetName, classes):
    folder_name = source_folder.split('/')
    sets=[(folder_name[-2], 'train'), (folder_name[-2], 'val')]
   
    for ID, image_set in sets:
        if not os.path.exists(os.path.dirname(source_folder)+'/labels/'):
            os.makedirs(os.path.dirname(source_folder)+'/labels/')
        image_ids = open(os.path.dirname(source_folder)+'/ImageSets/Main/%s.txt'%(image_set)).read().strip().split()
        for image_id in image_ids:
            convert_annotation(ID, image_id, source_folder, classes)
       
    print("voc_finish!!!!!")
#######################################

def create_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
def check_dir_notzero(path):
    if os.path.isdir(path):
        f = os.listdir(path)
        if len(f) == 0:
            return False
        else: 
            return True
    else:
        return False

def find_backupFileList(backupPath):
    backupFileList=[]
    backupFileList.append('darknet53.conv.74')
    for ( dirpath, dirnames, filenames) in os.walk(backupPath):
        for path in dirpath:
            for dirname in dirnames:
                for file in filenames:
                    print(path+"/"+dirname+'/'+file)
                    if '.backup' in file:
                        backupFileList.append(file)
    return backupFileList

def read_record(recordPath, config):
    if os.path.isfile(recordPath):
        with open(recordPath, "r") as f:
            for lines in f.readlines():
                if "dataset" in lines:
                    config.DATASET_NAME = lines.split(':')[-1].strip()
                    print(config.DATASET_NAME)
                elif "cfg_setdata" in lines:
                    config.CFG_DATA = lines.split(":")[-1].strip()
                elif "cfg_yolo" in lines:
                    config.CFG_YOLO = lines.split(":")[-1].strip()
                elif "classNamePath" in lines:
                    config.CLASSPATH = lines.split(":")[-1].strip()

def close_pid(pid):
    os.kill(int(pid), signal.SIGKILL)

def get_pid(name):
    return subprocess.check_output(["pidof",name])

def make_tree(path, list_f):
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                make_tree(fn, list_f)
            else:                
                if '.backup' in fn:
                    list_f.append(fn)
    return list_f

def check_pid(pid): 
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def file_remove(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        print("remove "+file_path)
    else:
        print("File doesnot exist: "+file_path)

def add_class(classes, classNamePath):
    try:
        class_str = ""
        del classes[:]    
        with open(classNamePath, 'r') as f:
                for line in f:
                    if not line=="":
                        line = line.strip() #濾除空白、換行之類的特出符號
                        classes.append(line)                        
                        class_str = class_str+line+","
        if "" in classes:
            classes.remove("")
        print("add_class = "+str(classes))
       
        return class_str[:-1]
    except:
        return "class import error"

def find_dataset(datasetPath):
    datasetList=[]
    files = os.listdir(datasetPath)  
    for f in files:
        fullpath = os.path.join(datasetPath, f)   
        if os.path.isdir(fullpath):
            datasetList.append(f)
    if 'backup' in datasetList:
        datasetList.remove('backup')
    return datasetList

def create_listName(source_folder):
    # source_folder='/home/kelly/data/Dataset/Mura/LCD4/JPEGImages'#地址是所有图片的保存地点
    # dest='/home/kelly/data/Dataset/Mura/LCD4/ImageSets/Main/train.txt' #保存train.txt的地址
    # dest2='/home/kelly/data/Dataset/Mura/LCD4/ImageSets/Main/val.txt'  #保存val.txt的地址
    
    if not os.path.isdir(os.path.dirname(source_folder)+"/ImageSets"):
        os.mkdir(os.path.dirname(source_folder)+"/ImageSets")
    if not os.path.isdir(os.path.dirname(source_folder)+"/ImageSets/Main"):
        os.mkdir(os.path.dirname(source_folder)+"/ImageSets/Main")
    
    dest = os.path.dirname(source_folder)+"/ImageSets/Main/train.txt"
    dest2 = os.path.dirname(source_folder)+"/ImageSets/Main/val.txt"
    dest3 = os.path.dirname(source_folder)+"/full_train.txt"
    dest4 = os.path.dirname(source_folder)+"/full_val.txt"
    if os.path.isfile(dest):
        os.remove(dest)
    if os.path.isfile(dest2):
        os.remove(dest2)
    file_list=os.listdir(source_folder)       #赋值图片所在文件夹的文件列表
    train_file=open(dest,'a')                 #打开文件
    val_file=open(dest2,'a')                  #打开文件
    fully_train_file=open(dest3,'a')                 #打开文件
    fully_val_file=open(dest4,'a')                  #打开文件
    for num, file_obj in enumerate(file_list):                #访问文件列表中的每一个文件
        file_path=os.path.join(source_folder,file_obj) 
        #file_path保存每一个文件的完整路径
        file_name,file_extend=os.path.splitext(file_obj)
        #file_name 保存文件的名字，file_extend保存文件扩展名
        # file_num=int(file_name) 
        #把每一个文件命str转换为 数字 int型 每一文件名字都是由四位数字组成的  如 0201 代表 201     高位补零  
        if(num<len(file_list)*0.8):                     #保留900个文件用于训练
            #print file_num
            train_file.write(file_name+'\n')  #用于训练前900个的图片路径保存在train.txt里面，结尾加回车换行
            fully_train_file.write(file_path+'\n')
        else :
            val_file.write(file_name+'\n')    #其余的文件保存在val.txt里面
            fully_val_file.write(file_path+'\n')
    train_file.close()#关闭文件
    val_file.close()
    fully_train_file.close()
    fully_val_file.close()



def write_file(log_path, result_dir):
    avg_loss=[]
    iou = []
    with open(result_dir + '/IOU.json', 'w+') as outfile2:
        with open(result_dir + '/AvgLoss.json', 'w+') as outfile:
            with open(log_path, 'r') as f:
                    next_skip = False
                    for line in f:
                        if next_skip:
                            next_skip = False
                            continue
                        # 去除多gpu的同步log
                        if 'Syncing' in line:
                            continue
                        # 去除除零错误的log
                        if 'nan' in line:
                            continue
                        if 'Saving weights to' in line:
                            next_skip = True
                            continue
                        if "images" in line:                           
                            avg_loss.append(float(line.split(' ')[2]))
                        elif "IOU" in line:
                            iou.append(float(line.split(' ')[4].split(',')[0]))
            data = {"avg_loss":avg_loss}
            json.dump(data, outfile)
            data = {"IOU":iou}
            json.dump(data, outfile2)




def read_reversed(classes, paras, datasetName):
    max_batches = paras[1]
    learning_rate = paras[2]
    batch = paras[3]
    subdivisions = paras[4]
    current = paras[5]
    cfg_yolo = 'static/task/'+current+'/yolov3_'+datasetName+'.cfg'   
    replace_count=[]
    count=0
    temp = 'static/task/'+current+'/cfg_temp.cfg'
    copyfile('cfg/yolov3-voc.cfg', cfg_yolo)
    with open(cfg_yolo, 'r') as fr:    
        with open(temp, 'w+') as fw:
            for lines in fr:
                count+=1
                if "#" in lines:
                    fw.write(lines)                   
                elif "classes" in lines:
                    fw.write("classes="+classes+"\n")
                elif "max_batches" in lines:
                    fw.write('max_batches='+max_batches+'\n')                   
                elif "learning_rate" in lines:
                    fw.write('learning_rate='+learning_rate+'\n')                   
                elif "batch=" in lines:
                    fw.write('batch='+batch+'\n')                  
                elif "subdivisions" in lines:
                    fw.write('subdivisions='+subdivisions+'\n')
                else:
                    fw.write(lines)

    yolo_t = False
    # for line in reversed(cfg_yolo.readlines()):   #python2
    for line in reversed(list(open(cfg_yolo))):
        if 'yolo' in line.rstrip():
            yolo_t = True
        if 'filters' in line.rstrip() and yolo_t is True:
            replace_count.append(count)
            yolo_t=False
        count-=1


    with open(temp, 'r') as fr:
        with open(cfg_yolo, 'w+') as fw:
            for lines in fr:
                if count+1 in replace_count:                
                    filter_num = 3*(int(classes)+5)
                    fw.write("filters="+str(filter_num)+'\n')
                else:
                    fw.write(lines)
                count+=1
    os.remove(temp)