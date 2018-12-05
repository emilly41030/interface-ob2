#coding=utf-8
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import sys
import json

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Yolov3LogVisualization:

    def __init__(self,log_path,result_dir):

        self.log_path = log_path
        self.result_dir = result_dir

    def extract_log(self):
        avg_loss=[]
        iou = []
        with open(self.result_dir + '/IOU.json', 'w+') as outfile2:
            with open(self.result_dir + '/AvgLoss.json', 'w+') as outfile:
                with open(self.log_path, 'r') as f:
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


if __name__ == '__main__':
    # log_path = '/home/kelly/Desktop/interface-ob2/scripts/Mura_LCD4___20181205_165501/log/logfile.log'
    # result_dir = '/home/kelly/Desktop/interface-ob2/scripts'
    print(sys.argv[1])
    print(sys.argv[2])
    log_path = sys.argv[1]
    result_dir = sys.argv[2]
    logVis = Yolov3LogVisualization(log_path,result_dir)
    logVis.extract_log()

