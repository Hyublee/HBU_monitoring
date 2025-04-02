
from PySide2.QtWidgets import QWidget, QLabel

class Ui_DED_Monitoring(object):
    def setupUi(self, DED_Monitoring):
        DED_Monitoring.setObjectName("DED_Monitoring")
        DED_Monitoring.resize(800, 600)

        self.centralwidget = QWidget(DED_Monitoring)
        self.centralwidget.setObjectName("centralwidget")

        self.label_camera_status = QLabel("🔴 Camera", self.centralwidget)
        self.label_camera_status.move(20, 20)

        self.label_pyro_status = QLabel("🔴 Pyrometer", self.centralwidget)
        self.label_pyro_status.move(20, 50)

        self.label_cnc_status = QLabel("🔴 CNC", self.centralwidget)
        self.label_cnc_status.move(20, 80)

        self.label_ipg_status = QLabel("🔴 IPG Laser", self.centralwidget)
        self.label_ipg_status.move(20, 110)

        DED_Monitoring.setCentralWidget(self.centralwidget)
