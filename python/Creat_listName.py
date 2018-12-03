#coding=UTF-8
#这个小脚本是用来打开图片文件所在文件夹，把前900个用于训练的图片的名称保存在tain.txt，后103个用于验证的图片保存在val.txt
import os
from os import listdir, getcwd
from os.path import join
import sys

if __name__ == '__main__':    
    # source_folder='/home/kelly/data/Dataset/Mura/LCD4/JPEGImages'#地址是所有图片的保存地点
    # dest='/home/kelly/data/Dataset/Mura/LCD4/ImageSets/Main/train.txt' #保存train.txt的地址
    # dest2='/home/kelly/data/Dataset/Mura/LCD4/ImageSets/Main/val.txt'  #保存val.txt的地址
    source_folder=sys.argv[1]
    if not os.path.isdir(os.path.dirname(source_folder)+"/ImageSets"):
        os.mkdir(os.path.dirname(source_folder)+"/ImageSets")
    if not os.path.isdir(os.path.dirname(source_folder)+"/ImageSets/Main"):
        os.mkdir(os.path.dirname(source_folder)+"/ImageSets/Main")
    dest = os.path.dirname(source_folder)+"/ImageSets/Main/train.txt"
    dest2 = os.path.dirname(source_folder)+"/ImageSets/Main/val.txt"
     
    if os.path.isfile(dest):
        os.remove(dest)
    if os.path.isfile(dest2):
        os.remove(dest2)
    file_list=os.listdir(source_folder)       #赋值图片所在文件夹的文件列表
    train_file=open(dest,'a')                 #打开文件
    val_file=open(dest2,'a')                  #打开文件
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
        else :
            val_file.write(file_name+'\n')    #其余的文件保存在val.txt里面
    train_file.close()#关闭文件
    val_file.close()
