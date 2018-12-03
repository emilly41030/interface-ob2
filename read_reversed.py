import os
from shutil import copyfile
import sys

datasetName = sys.argv[2]
max_batches = sys.argv[3]
learning_rate = sys.argv[4]
batch = sys.argv[5]
subdivisions = sys.argv[6]
current = sys.argv[7]

cfg_yolo = 'scripts/'+datasetName+"___"+current+'/yolov3_'+datasetName+'.cfg'
classes = sys.argv[1]

replace_count=[]
count=0
is_train=0
temp = 'scripts/'+datasetName+"___"+current+'/cfg_temp.cfg'
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
                if not is_train == 0:                          
                    fw.write('batch='+batch+'\n')
                else:
                    fw.write(lines)
            elif "subdivisions" in lines:
                if not is_train == 0:
                    fw.write('subdivisions='+subdivisions+'\n')
                else:
                    fw.write(lines)
                is_train+=1
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