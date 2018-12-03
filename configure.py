#encoding: utf-8
import os

# __file__ refers to the file settings.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC_TXT = os.path.join(APP_ROOT, '') #设置一个专门的类似全局变量的东西
SECRET_KEY = '7d441f27d441f27567d441f2b6176a'
PID = 66666
EPOCH = 1200000
LIST_PID=[]
LOG_LIST=[]
TEST_IMG=''
DATASET_NAME=""
CFG_DATA=""
CFG_YOLO=""
CLASSPATH=""
TEST_DATASET=""
TIME=""