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
avg_loss=[]
iou = []

class TaskData(db.Model):
    __tablename__ = 'TaskData'
    Id = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(64))
    TaskName = db.Column(db.String(64))
    Dataset = db.Column(db.String(64))
    RunTime = db.Column(db.String(64))
    MaxBatch = db.Column(db.Integer)
    BatchSize = db.Column(db.Integer)
    Subdivisions = db.Column(db.Integer)
    LearningRate = db.Column(db.Integer)
    PreModel = db.Column(db.String(64))
    PID = db.Column(db.Integer)    
    Status = db.Column(db.String(64))    
    Description = db.Column(db.String(64))

    def __init__(self, UserName, TaskName, Dataset, RunTime, MaxBatch, BatchSize, Subdivisions, LearningRate, PreModel, PID, Status, Description):      
        self.UserName = UserName
        self.TaskName = TaskName
        self.Dataset = Dataset
        self.RunTime = RunTime
        self.MaxBatch = MaxBatch
        self.BatchSize = BatchSize
        self.Subdivisions = Subdivisions
        self.LearningRate = LearningRate
        self.PreModel = PreModel
        self.PID = PID
        self.Status=Status      
        self.Description = Description

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
imgPath = "data"



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
    time2 = config.TEST_DATASET
    task = TaskData.query.filter_by(RunTime=time2).first()
    if task is None:
        return ""
    data = [{
        'TaskName':task.TaskName,
        'Dataset':task.Dataset,
        'RunTime':task.RunTime,
        'MaxBatch':task.MaxBatch,
        'BatchSize':task.BatchSize,
        'Subdivisions':task.Subdivisions,
        'LearningRate':task.LearningRate,
        'status':task.Status
    }]
    return jsonify(data)

@app.route('/test_post/',methods=['POST','GET']) 
def test_post(): #获取POST数据 
    dataset=request.form.get('dirname')
    # print('dataset = '+str(dataset))
    childtree = []
    data={}
    dirfiles = listdir(backupPath+"/"+str(dataset))
    for f in dirfiles:
        if 'weight' in f:   
            childtree.append(f)
    data['weight']=childtree
    config.TEST_DATASET=dataset 
    # print(data)
    return jsonify(data)

@app.route('/trainTask_post/',methods=['POST','GET']) 
def trainTask_post(): #获取POST数据 
    task = TaskData.query.filter_by(Status="Training").first()   
    if task is not None:
        return "1"
    return "0"

@app.route('/index')
def index():    
    return render_template('index.html')

def write_log(datasetName, current, paras, classes, config, datasetPath, backupPath):
    function.add_class('data/voc_'+datasetName+'.names', classes)    
    classes_size=str(len(classes))
    os.mkdir("scripts/"+current)
    function.file_remove("static/test.txt")
    # 寫 yolov3_voc.cfg 檔案
    function.read_reversed(classes_size, paras)
    #  寫 .data 檔
    cfg_set = "scripts/"+current+"/voc_"+datasetName+".data"
    copyfile(datasetPath+datasetName+"/voc_"+datasetName+".data", cfg_set)
    config.CFG_DATA=cfg_set
    backupDir = backupPath+"/"+current
    with open(cfg_set, 'a+') as f:
        f.write("backup = "+backupDir)
    function.create_dir(backupPath+"/"+current)
    logPath='scripts/'+current+'/log'
    function.create_dir(logPath)
    logfile = open(logPath+'/logfile.log', 'w+')
    cfg_set = os.getcwd()+'/scripts/'+current+'/voc_'+datasetName+".data"
    cfg_yolo = os.getcwd()+"/scripts/"+current+"/yolov3_"+datasetName+".cfg"
    time.sleep(1)
    print("./darknet detector train "+cfg_set+" "+cfg_yolo+ " "+paras[6])
    p = subprocess.Popen(['./darknet', 'detector', 'train', cfg_set,cfg_yolo , paras[6]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    config.PID = p.pid
    task = TaskData(UserName='ad',TaskName=paras[7],Dataset=paras[0], RunTime=current, MaxBatch=paras[1], BatchSize=paras[3], Subdivisions=paras[4], LearningRate=paras[2], PreModel=paras[8], PID=p.pid, Status="Training", Description="")
    db.session.add(task)
    db.session.commit()  
    
    result_dir = 'static/task/'+current
    function.create_dir(result_dir)
    max_batches = paras[1]
    next_skip = False
    
    with open(result_dir + '/IOU.json', 'w+') as outfile2:
        with open(result_dir + '/AvgLoss.json', 'w+') as outfile:
            for line in p.stdout:
                sys.stdout.write(line)
                logfile.write(line)
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
                #print(avg_loss)
            data = {"avg_loss":avg_loss}
            json.dump(data, outfile)
            data = {"IOU":iou}
            json.dump(data, outfile2)

        if 'CUDA Error' in line:           
            task.Status = "Error"
            task.Description = line
            db.session.commit()          
        elif 'Cannot load image' in line:            
            task.Status = "Error"
            task.Description = line
            db.session.commit()          
        elif " "+max_batches+' images' in line:
            task.Status = "Success"
            db.session.commit()
            
    del avg_loss[:]
    del iou[:]
    print ('write_log finish')
   
    if not task.Status=="Abort":
        if not task.Status == "Success":
            task.Status = "Error"
            task.Description = "Exception occurs (Maybe max batch set too small or Pre-train model error)"
            db.session.commit()

    with open("static/test.txt", "w+") as f:
        f.write("")

@app.route('/close_task', methods=['GET', 'POST'])
def close_task():
    pid=request.form.get('pid')   
    if pid is not None:
        function.close_pid(pid)
        task3 = TaskData.query.filter_by(PID=pid).first()
        task3.Status = "Abort"
        db.session.commit()
    return "0"

@app.route('/training', methods=['GET', 'POST'])
def training():
    paras=[]
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
        paras.append(request.form.get('comp2_select'))
        Thread1=threading.Thread(target=write_log, args=(datasetName, current, paras, classes, config, datasetPath, backupPath))
        Thread1.start()      
        time.sleep(1)
    return render_template("training.html", pid=config.PID, paras=paras, filepath=current)
    
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
                # print("======== Del pid"+ str(config.PID)+" ========")
                task3 = TaskData.query.filter_by(PID=config.PID).first()
                task3.Status = "Abort"
                db.session.commit()
                        
    return render_template("train.html", pid=config.PID, dirList=datasetList,  backup=backupFileList)
    
@app.route("/view_training_test_post", methods=['GET', 'POST'])
def view_training_test_post():
    config.TEST_DATASET=request.form.get('dirname')
    print(config.TEST_DATASET)
    return "0"

@app.route("/view_training_del_post", methods=['GET', 'POST'])
def view_training_del_post():
    del_dir = request.get_json()
    for dirname in del_dir:     # 存放 weight
        # print(del_dir)
        shutil.rmtree(backupPath+'/'+dirname, ignore_errors=True)
        # 存放 log .data .cfg
        if not dirname=='backup':
            shutil.rmtree('scripts/'+dirname, ignore_errors=True)
        # 存放 log .data .cfg            
        shutil.rmtree('static/task/'+dirname, ignore_errors=True)
        time = dirname
        # print(time)
        del_task = TaskData.query.filter_by(RunTime=time).first()
        db.session.delete(del_task)
        db.session.commit()
    return "0"


@app.route("/view_training", methods=['GET', 'POST'])
def view_training():
    backupDir_data=[]
    error=None
    backupfiles = listdir(backupPath)
    for f in backupfiles:
        task = TaskData.query.filter_by(RunTime=str(f)).first()
        if task is not None:
            backupDir_data.append(task)
    if len(backupDir_data)==0:
        error = "Cannot find any backup"
        return render_template('view_training.html',error=error)
    # config.TEST_DATASET = backupDir_data[0]

    return render_template('view_training.html',size_d=2,tree=backupDir_data, error=error, dataset=config.TEST_DATASET)

@app.route("/showimg_del_post", methods=['GET', 'POST'])
def showimg_del_post():
    print("!!!")
    shutil.rmtree(resultDir, ignore_errors=True)
    function.create_dir(resultDir)
    error=None
    error = " Cannot find any backup"        
    return render_template('test.html',error=error)
    # return "0"

@app.route("/showimg", methods=['GET', 'POST'])
def showimg():
    image_names = os.listdir(resultDir)
    # if request.method == "POST":
    #     shutil.rmtree(resultDir, ignore_errors=True)
    #     del image_names
    #     image_names=[]
    # function.create_dir(resultDir)
    return render_template("showimg.html", image_names=image_names)

@app.route("/test_start_post/", methods=['GET', 'POST'])
def test_start_post():
    print("!!!!!!!!!!!!")
    dirname = request.form.get('model')
    wei_file = request.form.get('weight')
    img = request.form.get('img')
    function.file_remove('predictions.jpg')
    function.create_dir(resultDir)
        
    task = TaskData.query.filter_by(RunTime=dirname).first()
    name = task.Dataset
    print("./darknet detector test scripts/"+dirname+"/voc_"+name+".data scripts/"+dirname+"/yolov3_"+name+".cfg scripts/backup/"+dirname+"/"+str(wei_file)+ ' data/'+str(img))
    p = subprocess.Popen(["./darknet", "detector","test","scripts/"+dirname+"/voc_"+name+".data", "scripts/"+dirname+"/yolov3_"+name+".cfg","scripts/backup/"+dirname+"/"+str(wei_file), 'data/'+str(img)])
    p.wait()
    img_name = str(wei_file)+'-'+str(img).split('.')[0]+'.jpg'
    shutil.move('predictions.jpg', resultDir+"/"+img_name)
    return jsonify(img_name)

@app.route("/training_status_post/", methods=['GET', 'POST'])
def training_status_post():
    task = TaskData.query.filter_by(PID=config.PID).first()
    #print(avg_loss)
    data = [{      
        'status':task.Status,
        'Description':task.Description,
        "avg_loss":avg_loss
    }]
    return jsonify(data)

@app.route("/test", methods=['GET', 'POST'])
def test():
    ###   匯入 backup file ###
    function.create_dir(resultDir)
    backupDir = []
    size_d = 0
    backupfiles = listdir(backupPath)
    for f in backupfiles:
        backupDir.append(f)    

    if len(backupDir) > 5:
        size_d = 5
    elif len(backupDir)==0:
        error=None
        error = " Cannot find any backup"        
        return render_template('test.html',error=error)
    else:
        size_d=len(backupDir)

    ###   匯入 backup file 的 weights ###   
    dirfiles=[]
    childtree = []
    # config.DATASET_NAME=backupDir[0]
    if config.TEST_DATASET =="" or config.TEST_DATASET is None:
        config.DATASET_NAME=backupDir[0]
        config.TIME=backupDir[0]
        dirfiles = listdir(backupPath+"/"+str(config.TIME))
    else:
        dirfiles = listdir(backupPath+"/"+config.TEST_DATASET)
    for f in dirfiles:
        if 'weight' in f:
            childtree.append(f)

    ###   匯入 images ###
    imglist=[]
    imgfiles = listdir(imgPath)
    for f in imgfiles:
        if os.path.splitext(f)[-1] in [".png", ".jpg"]:
            imglist.append(f)

    return render_template('test.html',size_d=size_d, dataset=config.TEST_DATASET,tree=backupDir, childtree=childtree, imglist=imglist, result="")

@app.route("/del_all_post/", methods=['GET', 'POST'])
def del_all_post():
    backupfiles = os.listdir(backupPath)
    for dirname in backupfiles:     # 存放 weight
        # print(dirname)
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
