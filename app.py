# pythonspot.com
# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, request, redirect, session, abort, url_for, g, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import os
from os import listdir
import configure as config
import threading
import subprocess
import time
import signal
import sys
import shutil
import function
from shutil import copyfile
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import json
# App config.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class TaskData(db.Model):
    __tablename__ = 'TaskData'
    Id = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(64))
    TaskName = db.Column(db.String(64))
    Dataset = db.Column(db.Integer)
    RunTime = db.Column(db.String(64))
    MaxBatch = db.Column(db.Integer)
    BatchSize = db.Column(db.Integer)
    Subdivisions = db.Column(db.Integer)
    LearningRate = db.Column(db.Integer)
    PID = db.Column(db.Integer)
    
    def __init__(self, UserName, TaskName, Dataset, RunTime, MaxBatch, BatchSize, Subdivisions, LearningRate, PID):      
        self.UserName = UserName
        self.TaskName = TaskName
        self.Dataset = Dataset
        self.RunTime = RunTime
        self.MaxBatch = MaxBatch
        self.BatchSize = BatchSize
        self.Subdivisions = Subdivisions
        self.LearningRate = LearningRate
        self.PID = PID
    
app.config.from_object(config)
classes = []   #類別資訊
classNamePath = config.CLASSPATH  #類別名稱
# cfg_set -> 設定訓練類別數量、訓練及測試圖片檔名列表路徑、類別名稱路徑、儲存 .wieght 路徑
cfg_set=config.CFG_DATA
# cfg_yolo -> 設定參數 class 有變動 filter classes
cfg_yolo=config.CFG_YOLO
# app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
datasetPath = 'dataset/'
backupPath = 'scripts/backup'
recordPath = "static/record.txt"
resultDir = 'static/Result'

@app.route('/process', methods=['POST'])
def pid_process():
    train_task=0
    if len(config.LIST_PID) != 0:
        for num in config.LIST_PID:
            exist_task = function.check_pid(num)
            if exist_task:
                train_task+=1
            return jsonify({'task': train_task})
    return jsonify({'error':'No training task'})

@app.route('/')
def home():
    return render_template('home.html')



@app.route('/dataset', methods=['GET', 'POST'])
def ImportDataset():
    if request.method == 'POST':       
        OriginImgPath = request.form.get('train_imagePath') #/home/kelly/data/Dataset/Mura/LCD4/JPEGImages
        if str(OriginImgPath)=="":
            return "Image path error"
        OriginLabelPath = request.form.get('train_labelPath') #/home/kelly/data/Dataset/Mura/LCD4/Annotataions
        if str(OriginLabelPath)=="":
            return "Label path error"
        datasetName = request.form.get('dataset_name')
        if str(datasetName)=="":
            return "Dataset name error"
        config.DATASET_NAME=datasetName
        firName = OriginImgPath.split('/')[-3]    # firName = Mura
        secName = OriginImgPath.split('/')[-2]    # secName = LCD4
        #os.path.dirname(os.path.dirname(datasetPath))  擷取 JPEGImages 上上層 /home/kelly/data/Dataset/Mura
        function.create_dir(datasetPath+datasetName)        
        if os.path.isdir(datasetPath+datasetName+'/'+firName):
            shutil.rmtree(datasetPath+datasetName+'/'+firName, ignore_errors=True)

        ####    寫 class 類別名稱   ####
        class_temp = request.form['classes'] # 讀進來是 unicode
        classNamePath = 'data/voc_'+datasetName+'.names'
        config.CLASSPATH = classNamePath
        
        try:
            function.file_remove(classNamePath)
            del classes[:]
            with open(classNamePath,'w+') as f:
                f.write(str(class_temp))
            function.add_class(classes, classNamePath)
        except:          
            return ".names 寫檔錯誤!!!"        
        print("classes = "+str(classes))
       
        # 將資料集路徑的捷徑建立到 dataset/
        newPath = datasetPath+datasetName+'/'+firName
        ImagesPath = os.getcwd()+'/'+newPath + "/"+ secName +'/JPEGImages'
        LabelPath = os.getcwd()+'/'+newPath + "/"+ secName +'/Annotations'
        function.create_dir(os.getcwd()+'/'+newPath)
        function.create_dir(os.getcwd()+'/'+newPath + "/"+ secName)
        cmd_1 = " ln -sf "+OriginImgPath+" "+ImagesPath
        cmd_2 = " ln -sf "+OriginLabelPath+" "+LabelPath
        if not function.check_dir_notzero(OriginImgPath):
            return "Error: "+str(OriginImgPath)
        if not function.check_dir_notzero(OriginLabelPath):
            return "Error: "+str(OriginLabelPath)
       
        print(cmd_1)
        print(cmd_2)
        subprocess.Popen(['ln','-sf',OriginImgPath,ImagesPath])
        subprocess.Popen(['ln','-sf',OriginLabelPath,LabelPath])
        function.file_remove(newPath+"/"+secName+"/ImageSets/Main/train.txt")
        function.file_remove(newPath+"/"+secName+"/ImageSets/Main/val.txt")

        # 將 JPEGImages 的圖片寫入 /ImageSets/Main/train.txt、val.txt
        function.create_listName(ImagesPath)
        print("Creat_listName finish")
        
        # voc_label_Mura.py  創建 訓練、驗證完整的路徑檔案 scripts/xxx_train.txt、xxx_val.txt，
        #                    產生 label 資料夾      
        function.voc_label(ImagesPath, datasetName, classes)
        #  寫 .data 檔
        cfg_set = datasetPath+datasetName+"/voc_"+datasetName+".data"
        with open(cfg_set, 'w') as f:
            f.write("classes= "+str(len(classes))+'\n')
            f.write("train  = "+newPath+"/"+secName+'/full_train.txt\n')
            f.write("valid  = "+newPath+"/"+secName+'/full_val.txt\n')
            f.write("names = data/voc_"+datasetName+".names\n")

        backupFileList = []
        backupFileList.append('darknet53.conv.74')
        backupFileList = function.make_tree(backupPath, backupFileList)
        datasetList = function.find_dataset(datasetPath)
        return render_template('train.html', dirList=datasetList, backup=backupFileList)
    return render_template("dataset.html")

@app.route('/train')
def train():
    backupFileList = []
    backupFileList.append('darknet53.conv.74')
    backupFileList = function.make_tree(backupPath, backupFileList)
    datasetList = function.find_dataset(datasetPath)
    if len(datasetList)==0:
        return render_template('train.html',error="No found any dataset")
    if os.path.isfile('static/train_log_loss.txt'):
        os.remove('static/train_log_loss.txt')
    if os.path.isfile('static/test.txt'):
        os.remove('static/test.txt')
    return render_template('train.html', dirList=datasetList, pid_size=len(config.LIST_PID), backup=backupFileList)

@app.route('/train_model_post/',methods=['POST','GET']) 
def train_model_post(): #获取POST数据 
    config.TEST_DATASET=request.form.get('dirname')
    time2 = config.TEST_DATASET.split('___')[-1]
    task = TaskData.query.filter_by(RunTime=time2).first()
    status=''
    try:
        os.kill(task.PID, 0)
    except OSError:
        status = "Close"
    else:
        status = "Training"
    data = [{
        'TaskName':task.TaskName,
        'Dataset':task.Dataset,
        'RunTime':task.RunTime,
        'MaxBatch':task.MaxBatch,
        'BatchSize':task.BatchSize,
        'Subdivisions':task.Subdivisions,
        'LearningRate':task.LearningRate,
        'status':status
    }]
    return jsonify(data)

@app.route('/test_post/',methods=['POST','GET']) 
def test_post(): #获取POST数据 
    dataset=request.form.get('dirname')
    print('dataset = '+str(dataset))
    childtree = []
    data={}
    dirfiles = listdir(backupPath+"/"+str(dataset))
    for f in dirfiles:
        if 'weight' in f:   
            childtree.append(f)
    data['weight']=childtree
    config.TEST_DATASET=dataset 
    print(data)
    return jsonify(data)

@app.route('/index')
def index():    
    return render_template('index.html')

def write_log(datasetName, current, paras, classes, config, datasetPath, backupPath):
    function.add_class('data/voc_'+datasetName+'.names', classes)    
    classes_size=str(len(classes))
    os.mkdir("scripts/"+datasetName+"___"+current)
    function.file_remove("static/test.txt")
    # 寫 yolov3_voc.cfg 檔案
    function.read_reversed(classes_size, paras)
    #  寫 .data 檔
    cfg_set = "scripts/"+datasetName+"___"+current+"/voc_"+datasetName+".data"
    copyfile(datasetPath+datasetName+"/voc_"+datasetName+".data", cfg_set)
    config.CFG_DATA=cfg_set
    backupDir = backupPath+"/"+datasetName+"___"+current
    with open(cfg_set, 'a+') as f:
        f.write("backup = "+backupDir)
    function.create_dir(backupPath+"/"+datasetName+"___"+current)
    logPath='scripts/'+datasetName+"___"+current+'/log'
    function.create_dir(logPath)
    logfile = open(logPath+'/logfile.log', 'w+')
    cfg_set = os.getcwd()+'/scripts/'+datasetName+"___"+current+'/voc_'+datasetName+".data"
    cfg_yolo = os.getcwd()+"/scripts/"+datasetName+"___"+current+"/yolov3_"+datasetName+".cfg"
    time.sleep(1)
    print("./darknet detector train "+cfg_set+" "+cfg_yolo+ " "+paras[6])
    p = subprocess.Popen(['./darknet', 'detector', 'train', cfg_set,cfg_yolo , paras[6]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    config.PID = p.pid
    task = TaskData(UserName='ad',TaskName=paras[7],Dataset=paras[0], RunTime=current, MaxBatch=paras[1], BatchSize=paras[3], Subdivisions=paras[4], LearningRate=paras[2], PID=p.pid)
    db.session.add(task)
    db.session.commit()
    config.LIST_PID.append(p.pid)
    print("======== Add pid  "+ str(config.PID)+" ========")
    print(config.LIST_PID)
    for line in p.stdout:
        sys.stdout.write(line)
        logfile.write(line)
    print ('write_log finish')
    print(str(config.PID) + "   "+str(config.LIST_PID))
    if config.PID in config.LIST_PID:
        config.LIST_PID.remove(config.PID)
        print("======== Del pid  "+ str(config.PID)+" ========")
        print(config.LIST_PID)
    with open("static/test.txt", "w+") as f:
        f.write("")


@app.route('/training', methods=['GET', 'POST'])
def training():
    paras = []    
    function.file_remove("static/test.txt")
    if not os.path.isfile('darknet53.conv.74'):
        subprocess.Popen(['wget','https://pjreddie.com/media/files/darknet53.conv.74'])
    
    if request.method == 'POST':
        current = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        config.EPOCH = request.form.get('max_batches')
        datasetName = request.form.get('comp1_select')
        config.DATASET_NAME=datasetName          # Mura_LCD4
        paras.append(datasetName)                #[0]
        paras.append(request.form.get('max_batches'))
        paras.append(request.form.get('learning_rate'))
        paras.append(request.form.get('batch'))   #[3]
        paras.append(request.form.get('subdivisions'))
        paras.append(current)
        paras.append(request.form.get('comp2_select'))  #[6]
        paras.append(request.form.get('task_name'))
        
       
        Thread1=threading.Thread(target=write_log, args=(datasetName, current, paras, classes, config, datasetPath, backupPath))
        Thread1.start()       
        Thread2=threading.Thread(target=function.extract_log, args=(datasetName, current, config))
        Thread2.start()
        time.sleep(1)
        filepath = datasetName+"___"+current
    # filepath = "Mura_LCD4___20181206_112804"
    return render_template("training.html", pid=config.PID, paras=paras, filepath=filepath)
    
@app.route("/option", methods=['GET', 'POST'])
def option():
    backupFileList = []
    backupFileList.append('darknet53.conv.74')
    backupFileList = function.make_tree(backupPath, backupFileList)
    datasetList = function.find_dataset(datasetPath)
    if len(datasetList)==0:
        return render_template('train.html',error="No found any dataset")

    if request.method == 'POST':
        backupFileList = []
        backupFileList = function.make_tree(backupPath, backupFileList)
        datasetList = function.find_dataset(datasetPath)
        backupFileList.append('darknet53.conv.74')
        if len(datasetList)==0:
            return render_template('train.html',error="No found any dataset")     
        if request.form["btn"] == "Test":
            return render_template('test.html')
        if request.form["btn"] == "Close":
            if (function.check_pid(config.PID)):
                function.close_pid(config.PID)
                print("======== Del pid"+ str(config.PID)+" ========")
                config.LIST_PID.remove(config.PID)
                print("LIST_PID = "+str(config.LIST_PID))
                        
    return render_template("train.html", pid=config.PID, dirList=datasetList,  backup=backupFileList)
    

@app.route("/view_training", methods=['GET', 'POST'])
def view_training():
    backupDir=[]
    error=None
    backupfiles = listdir(backupPath)
    for f in backupfiles:
        backupDir.append(f)
    if len(backupDir)==0:
        error = "Cannot find any backup"
        return render_template('view_training.html',error=error)
    config.TEST_DATASET = backupDir[0]

    if request.method == "POST":
        if 'delBtn' in request.form:
            del_dir = request.form.getlist('comp0_select')
            
            for dirname in del_dir:     # 存放 weight
                print(del_dir)
                shutil.rmtree(backupPath+'/'+dirname, ignore_errors=True)
                # 存放 log .data .cfg
                if not dirname=='backup':
                    shutil.rmtree('scripts/'+dirname, ignore_errors=True)
                # 存放 log .data .cfg            
                shutil.rmtree('static/task/'+dirname, ignore_errors=True)
                backupDir.remove(dirname)
                time = dirname.split("___")[-1]
                print(time)
                del_task = TaskData.query.filter_by(RunTime=time).first()
                db.session.delete(del_task)
                db.session.commit()

                
        elif 'cancelBtn' in request.form:
            config.TEST_DATASET = request.form.get('comp0_select')

    return render_template('view_training.html',size_d=2,tree=backupDir, error=error, dataset=config.TEST_DATASET)

@app.route("/showimg", methods=['GET', 'POST'])
def showimg():
    image_names = os.listdir('static/Result')
    return render_template("showimg.html", image_names=image_names)

@app.route("/test", methods=['GET', 'POST'])
def test():  
    imgPath = "data"
    backupDir = []
    imglist=[]
    error=None
    size_d = 0
    backupfiles = listdir(backupPath)
    for f in backupfiles:
        backupDir.append(f)
    imgfiles = listdir(imgPath)
    for f in imgfiles:
        if os.path.splitext(f)[-1] in [".png", ".jpg"]:
            imglist.append(f)
    if len(backupDir) > 5:
        size_d = 5
    elif len(backupDir)==0:
        error = " Cannot find any backup"        
        return render_template('test.html',error=error)
    else:
        size_d=len(backupDir)
    name = backupDir[0].split("___")
    # config.DATASET_NAME=backupDir[0]
    config.DATASET_NAME=name[0]
    config.TIME=name[-1]
    childtree = []
    dirfiles = listdir(backupPath+"/"+str(config.DATASET_NAME)+"___"+str(config.TIME))
    
    for f in dirfiles:
        if 'weight' in f:
            childtree.append(f)
    if request.method == "POST":
        if 'del_btn' in request.form:
            print("!!!!   del   !!!!!")
            backupfiles = os.listdir(backupPath)
            for dirname in backupfiles:     # 存放 weight
                print(dirname)
                shutil.rmtree(backupPath+'/'+dirname, ignore_errors=True)
            file = os.listdir('scripts')  # 存放 log .data .cfg
            for dirname in file:
                if not dirname=='backup':
                    shutil.rmtree('scripts/'+dirname, ignore_errors=True)      
            file = os.listdir('static/task')  # 存放 log .data .cfg
            for dirname in file:
                shutil.rmtree('static/task/'+dirname, ignore_errors=True)
            
            error = " Cannot find any backup"
            TaskData.query.delete()
            db.session.commit()
            return render_template('test.html',error=error)
        
        elif request.form['form_1'] == 'test_start':            
            function.file_remove('predictions.jpg')
            function.create_dir(resultDir)
            if config.TEST_DATASET=="":
                config.TEST_DATASET = backupDir[0]          
            dataset = config.TEST_DATASET
            name = config.TEST_DATASET.split("___")          
            wei_file = request.form.get('comp1_select')
            img = request.form.get('comp2_select')
            print("./darknet detector test scripts/"+dataset+"/voc_"+name[0]+".data scripts/"+dataset+"/yolov3_"+name[0]+".cfg scripts/backup/"+dataset+"/"+str(wei_file)+ ' data/'+str(img))
            p = subprocess.Popen(["./darknet", "detector","test","scripts/"+dataset+"/voc_"+name[0]+".data", "scripts/"+dataset+"/yolov3_"+name[0]+".cfg","scripts/backup/"+dataset+"/"+str(wei_file), 'data/'+str(img)])
            p.wait()
            img_name = str(wei_file)+'-'+dataset+'.jpg'
            shutil.move('predictions.jpg', resultDir+"/"+img_name)            
            return render_template("test.html",size_d=size_d, dataset=config.TEST_DATASET,tree=backupDir, childtree=childtree, imglist=imglist, error=error, result=img_name)
       
            config.TEST_DATASET=dataset

    return render_template('test.html',size_d=size_d, dataset=config.TEST_DATASET,tree=backupDir, childtree=childtree, imglist=imglist, error=error, result="")


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    function.create_dir(backupPath)
    function.create_dir(datasetPath)
    function.create_dir("static")
    function.create_dir(resultDir)
    if not os.path.isfile("darknet"):
        subprocess.Popen(["make","-j16"])
    function.file_remove("test.txt")
    function.read_record(recordPath, config)
    # manager.run()
    db.create_all()
    
    app.run(debug=True,host='0.0.0.0', port=6060, threaded=True)
