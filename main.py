# main program run
# setting file load and save

# main.py
from PySide2.QtWidgets import QApplication
from qt_material import apply_stylesheet
import sys
from app.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    extra = {'font_size': '20px'}
    apply_stylesheet(app, theme='light_blue.xml', extra=extra)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


# from UI.ui_Template import Ui_DED_Monitoring
# # from frontend.ui_cam_setting import Ui_Cam_set
# from UI.ui_save_path import Ui_Dialog as save_UI_Dialog
# from qt_material import apply_stylesheet
# from PySide2 import QtCore, QtGui, QtWidgets
# from PySide2 import QtCore, QtGui, QtWidgets
# from PySide2.QtCore import *
# from PySide2.QtGui import *
# from PySide2.QtGui import QImage
# from PySide2.QtWidgets import *
# from UI.ui_camera_setting import Ui_Cam_set
# # from Sensors.CNC import CNC_Communication, CNC_DB, CNC_Collector
# from Sensors.Camera import Camera_communication, Camera_DB, Camera_Collector
# from Sensors.IPG import IPG_Communication, IPG_DB, IPG_Collector
# from Sensors.pyrometer import Pyrometer_Communication, Pyrometer_DB, Pyrometer_Collector
# import configparser
# import subprocess

# from pyqtgraph import PlotWidget, plot
# import pyqtgraph as pg

# import sys, os
# import time
# from datetime import datetime, timedelta
# import cv2
# import numpy as np
# import pandas as pd
# import random

# from threading import Thread, Timer

# my_font = QFont("Times New Roman", 15)
# my_font2 = QFont("Times New Roman", 12)

# if __name__ =='__main__':    
#     print(os.path.abspath(__file__))
#     extra ={
#         'font_size': '20px'
#     }
#     app = QApplication(sys.argv) 
#     myWindow = Mainwindow()
#     apply_stylesheet(app, theme='light_blue.xml', extra=extra)


#     myWindow.show()
#     sys.exit(app.exec_())
    