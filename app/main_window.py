# app/main_window.py
from PySide2.QtWidgets import QMainWindow
from ui.ui_template import Ui_DED_Monitoring
from app.datacollector.collector import DataCollector

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DED_Monitoring()
        self.ui.setupUi(self)

        self.data_collector = DataCollector(self)

        # setup_connections(self)
        # setup_timers(self)


class Mainwindow(QMainWindow):                                          # Front pannel 동작, 버튼 및 그래프 등의 정의 클래스
    def __init__(self):
        super().__init__()
        # QMainWindow.__init__(self)
        self.ui = Ui_DED_Monitoring()                                       # Pyqtdesigner로 생성된 UI와 연결
        self.ui.setupUi(self)

        self.DC = DataCollector(self)                                       # 데이터 수집 클래스 선언

        self.btn_action()                                               # page, save, connect, exit 버튼 동작 시 연결함수 정의                                  
        self.graphs_init()                                              # 그래프 초기 설정
        self.is_running = False
        self.camera_active = False

        self.current_time = QTimer(self)                                # 현재 시간 타이머 정의
        self.current_time.timeout.connect(self.update_current_time)     # 타이머 동작 함수 연결
        self.current_time.start(1000)                                   # 타이머 동작 주기 1 s

        self.graph_update = QTimer(self)                                # 시계열 그래프 업데이트 타이머 정의
        self.graph_update.timeout.connect(self.update_gui)              # 타이머 동작 함수 연결

        self.img_update = QTimer(self)
        self.img_update.timeout.connect(self.draw_img)

        time.sleep(0.5)
        self.DC.start_threads()
        QTimer.singleShot(1000, self.DC.update_ui_sensor_status)
        self.graph_update.start(100)
        self.img_update.start(10)

    def btn_action(self):
        """버튼 동작 시 연결되는 함수 정의"""
        # self.ui.checkbox_cam_active.clicked.connect(self.basler_connect)

        self.ui.Save_btn.clicked.connect(self.save_cliecked)
        self.ui.setting_btn.clicked.connect(self.open_cam_ui)
        self.ui.Exit_btn.clicked.connect(self.exit)
        self.ui.Exit_btn.clicked.connect(QCoreApplication.instance().quit)

    def graphs_init(self):
        """그래프 설정"""
        self.set_serial_style(self.ui.meltpool_area, 'Melt Pool Area', 'Area(㎟)', 'Time', -20, 300)
        self.set_serial_style(self.ui.meltpool_temp, 'Melt Pool Temperature', 'Temperature(°C)', 'Time', 670, 2350, True)
        self.set_serial_style(self.ui.laserpower, 'Laser Power', 'Power(W)', 'Time', -20, 1100, True)

        self.line_data1 = self.ui.meltpool_temp.plot([], [], pen=pg.mkPen(width=1.5, color='r'), name='Melt Pool temperature')
        self.line_data2 = self.ui.meltpool_area.plot([], [], pen=pg.mkPen(width=1.5, color='b'), name='Melt Pool Area')
        self.line_data3 = self.ui.laserpower.plot([], [], pen=pg.mkPen(width=1.5, color='orange'), name='Out Power') 
        self.line_data4 = self.ui.meltpool_temp.plot([], [], pen=pg.mkPen(width=1.5, color='green', style=QtCore.Qt.DotLine), name='1-color temperature') 
        self.line_data5 = self.ui.laserpower.plot([], [], pen=pg.mkPen(width=1.5, color='orange', style=QtCore.Qt.DotLine), name='Set Power') 
        
    def update_ui_sensor_status(self):
        status = self.data_collector.sensor_status

        self.ui.label_camera_status.setText("🟢 Camera" if status['camera'] else "🔴 Camera")
        self.ui.label_pyro_status.setText("🟢 Pyrometer" if status['pyro'] else "🔴 Pyrometer")
        self.ui.label_cnc_status.setText("🟢 CNC" if status['cnc'] else "🔴 CNC")
        self.ui.label_ipg_status.setText("🟢 IPG Laser" if status['ipg'] else "🔴 IPG Laser")

    def connect_clicked(self, checked):
        """CONNECT 버튼 동작시 데이터 수집, 시각화 등의 기능을 시작"""
        if checked:                    
            self.is_running = True
            self.DC.start_threads()
            QTimer.singleShot(1000, self.DC.update_ui_sensor_status)
            self.graph_update.start(100)        # time serise 10 Hz
            self.img_update.start()           # camera image 30 fps
            self.set_ir_parms()

        else:
            self.is_running = False      
            if self.ui.btn_Save.isChecked():
                self.ui.btn_Save.toggle() 
                self.save_cliecked(False)      
            self.DC.stop_threads()
            self.graph_update.stop()
            self.img_update.stop()
            self.DC.ir_collector.stop()
            
    def save_cliecked(self, checked):
        """SAVE 버튼 클릭시 실행 함수 정의"""
        if checked:
            self.open_save_ui()
            self.is_saving = True
            save_thread = Thread(target=self.save, daemon=True)
            save_thread.start()
            # Thread(target=self.DC.save_img).start()

        else:
            self.is_saving = False
            # 모든 쓰레드 종요 및 진행 중인 작업 종료 -> save 버튼 다시 활성 시 모든 기능 동작 할 수 있도록.
            save_thread.join()

    def update_current_time(self):
        """현재 시간 업데이트"""
        self.ui.current_time.setDateTime(QDateTime.currentDateTime())

    def update_gui(self):
        """데이터 시각화 및 업데이트, QTimer()를 통해 동작"""
        try:
            self.ui.cur_x_val.setText(f"{self.DC.data_storage['curpos_x']:.2f}")
            self.ui.cur_y_val.setText(f"{self.DC.data_storage['curpos_y']:.2f}")
            self.ui.cur_z_val.setText(f"{self.DC.data_storage['curpos_z']:.2f}")
            self.ui.cur_a_val.setText(f"{self.DC.data_storage['curpos_a']:.2f}")
            self.ui.cur_c_val.setText(f"{self.DC.data_storage['curpos_c']:.2f}")
            self.ui.mac_x_val.setText(f"{self.DC.data_storage['macpos_x']:.2f}")
            self.ui.mac_y_val.setText(f"{self.DC.data_storage['macpos_y']:.2f}")
            self.ui.mac_z_val.setText(f"{self.DC.data_storage['macpos_z']:.2f}")
            self.ui.mac_a_val.setText(f"{self.DC.data_storage['macpos_a']:.2f}")
            self.ui.mac_c_val.setText(f"{self.DC.data_storage['macpos_c']:.2f}")
            self.ui.rem_x_val.setText(f"{self.DC.data_storage['rempos_x']:.2f}")
            self.ui.rem_y_val.setText(f"{self.DC.data_storage['rempos_y']:.2f}")
            self.ui.rem_z_val.setText(f"{self.DC.data_storage['rempos_z']:.2f}")
            self.ui.rem_a_val.setText(f"{self.DC.data_storage['rempos_a']:.2f}")
            self.ui.rem_c_val.setText(f"{self.DC.data_storage['rempos_c']:.2f}")

            self.ui.feed_val.setText(f"{self.DC.data_storage['feed_rate']:.2f}")
            self.ui.override_val.setText(f"{self.DC.data_storage['feed_override']:.1f}")
            self.ui.rapid_override_val.setText(f"{self.DC.data_storage['rapid_override']:.1f}")
            self.ui.operating_time.setText(f"{int(self.DC.data_storage['oper_time'] // 3600)}:{int((self.DC.data_storage['oper_time'] % 3600) // 60)}:{int(self.DC.data_storage['oper_time'] % 60)}")
            self.ui.total_operating_time.setText(f"{int(self.DC.data_storage['total_oper_time'] // 3600)}:{int((self.DC.data_storage['total_oper_time'] % 3600) // 60)}:{int(self.DC.data_storage['total_oper_time'] % 60)}")

        except Exception as e:
            print(f"!!!!!!!!Error in update_gui:{e}")

        self.draw_graph()

    def draw_graph(self):
        """시계열 및 이미지 그래프 업데이트"""
        try:
            self.line_data1.setData(self.DC.data_storage['_t'], self.DC.data_storage['mpt'])
            self.line_data2.setData(self.DC.data_storage['_t'], self.DC.data_storage['melt_pool_area'])
            self.line_data3.setData(self.DC.data_storage['_t'], self.DC.data_storage['outpower'])
            self.line_data4.setData(self.DC.data_storage['_t'], self.DC.data_storage['1ct'])
            self.line_data5.setData(self.DC.data_storage['_t'], self.DC.data_storage['setpower'])

        except Exception as e:
            print(f"!!!!!!!!draw_graph() graph Error: {e}")

    def draw_img(self):
        # if self.DC.cam.active:
            # if self.camera_active != self.DC.cam.active:
            #     self.ui.checkbox_cam_active.setChecked(True)
            # self.ui.label_cam_state.setText("Camera ON")
        try:
            img = self.DC.data_storage['image'][-1]
            img = QImage(img, 1920, 1200, QImage.Format.Format_Grayscale8)
            img = img.scaled(540, 340, Qt.KeepAspectRatio)
            self.ui.img_label.setPixmap(QPixmap.fromImage(img))
        except Exception as e:
            self.ui.img_label.setText("Error in image update")
            print(f"!!!!!!!!draw_img() image Error:{e}")
            # self.DC.cam.active = False
        # else: 
        #     if self.camera_active != self.DC.cam.active:
        #         self.ui.checkbox_cam_active.setChecked(False)
        #     self.ui.label_cam_state.setText("Camera OFF")
        # self.camera_active = self.DC.cam.active

    def set_serial_style(self, obj, title, labelx, labely, vmin, vmax, legend=False):
        """시계열 그래프 디자인"""
        obj.setBackground('#e6e6e6')
        obj.setLabel('top', title, color='black')
        obj.setLabel('left', labelx, color='black')
        obj.setLabel('bottom', labely, color='black',units='s')
        obj.setLabel('right', ' ', color='black')
        # obj.showAxis('right')
        obj.setYRange(vmin, vmax, padding=0)
        obj.showGrid(y=True)
        if legend == True:
            obj.addLegend(brush=(255,255,255,255), pen=pg.mkPen(color=(0,0,0)), size=(50,15), offset=(5,5), labelTextColor=(0,0,0))
        obj.getAxis('top').label.setFont(my_font)
        obj.getAxis('bottom').label.setFont(my_font2)
        obj.getAxis('left').label.setFont(my_font2)
        obj.getAxis('top').setStyle(showValues=False)
        obj.getAxis('right').setStyle(showValues=False)

    def save(self):
        """ DataCollector의 Data_storge의 데이터를 불러와 필요한 데이터를 .csv로 저장 """
        folder_generator = True
        start_time = datetime.now()
        file_name = str(start_time.strftime("%Y%m%d%H%M%S"))

        if folder_generator and self.folder_path:                 # 폴더 및 공정 로그 파일 생성
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            file_name = os.path.join(self.folder_path, f"{file_name}.csv")
            folder_generator = False

        while self.is_saving:
            loop_start_time = time.perf_counter()
            current_time = datetime.now()
            time_difference = current_time - start_time
            
            if time_difference >= timedelta(hours=1):
                file_name = os.path.join(self.folder_path, f"{str(current_time.strftime('%Y%m%d%H%M%S'))}.csv")
                start_time = current_time

            data_to_save = {key: value[-1] if isinstance(value, list) else value for key, value in self.DC.data_storage.items()}
            _df = pd.DataFrame([data_to_save])
            _df_save = _df[['time', 'curpos_x','curpos_y','curpos_z','curpos_a','curpos_c','mpt','melt_pool_area', 'outpower']]
            
            if os.path.exists(file_name):
                _df_save.to_csv(file_name, header=None, index=False, mode='a')
            else:
                _df_save.to_csv(file_name, header=True, index=False, mode='w')

            sleep_time = max(0, (1/30)-(time.perf_counter()-loop_start_time))
            time.sleep(sleep_time)
            
    def open_cam_ui(self, 
                    cam_config_path='./Monitoring/Sensors/ini_files/Camera.ini', 
                    CNC_config_path='./Monitoring/Sensors/ini_files/HXApi.ini', 
                    IPG_config_path='./Monitoring/Sensors/ini_files/IPG.ini',
                    Pyro_config_path='./Monitoring/Sensors/ini_files/Pyrometer,ini'):
        cam_config = configparser.ConfigParser()
        cnc_config = configparser.ConfigParser()
        ipg_config = configparser.ConfigParser()
        pyro_config = configparser.ConfigParser()
        cam_config.read(cam_config_path)
        cnc_config.read(CNC_config_path)
        ipg_config.read(IPG_config_path)
        pyro_config.read(Pyro_config_path)
        dialog = QDialog(self)
        ui = Ui_Cam_set()
        ui.setupUi(dialog)

        ui.exposure_time.setValue(int(cam_config['parameters']['exposure']))
        ui.gain.setValue(float(cam_config['parameters']['gain']))
        ui.gamma.setValue(float(cam_config['parameters']['gamma']))
        ui.black_level.setValue(float(cam_config['parameters']['black_level']))
        ui.digital_shift.setValue(int(cam_config['parameters']['digital_shift']))

        ui.image_width.setValue(int(cam_config['parameters']['width']))
        ui.image_height.setValue(float(cam_config['parameters']['height']))
        ui.pixel_size.setValue(float(cam_config['parameters']['pixel_size']))
        ui.threshold.setValue(float(cam_config['parameters']['threshold']))
        ui.fps.setValue(int(cam_config['parameters']['fps']))

        ui.laser_ip.setText(str(ipg_config['adress']['ip']))
        ui.laser_port.setValue(int(ipg_config['adress']['port']))

        ui.cnc_ip.setText(str(cnc_config['adress']['ip']))
        ui.cnc_port.setValue(int(cnc_config['adress']['port']))

        # ui.pyro_com.setValue(str(pyro_config['adress']['port']))
        # ui.pyro_baudrate.setValue(str(pyro_config['adress']['baudrate']))
        # ui.pyro_parity.setValue(str(pyro_config['adress']['parity']))
        # ui.pyro_stopbit.setValue(int(pyro_config['adress']['stopbits']))
        # ui.pyro_bytesize.setValue(int(pyro_config['adress']['bytesize']))
        # ui.pyro_timeout.setValue(int(pyro_config['adress']['timeout']))

        if dialog.exec_() == QDialog.Accepted:
            pass
        #     cam_config['parameters']['exposure'] = str(ui.exposure_time.value())
        #     cam_config['parameters']['gain'] = str(ui.gain.value())
        #     cam_config['parameters']['gamma'] = str(ui.gamma.value())
        #     cam_config['parameters']['black_level'] = str(ui.black_level.value())
        #     cam_config['parameters']['digital_shift'] = str(ui.digital_shift.value())

        #     cam_config['parameters']['width'] = str(ui.image_width.value())
        #     cam_config['parameters']['height'] = str(ui.image_height.value())
        #     cam_config['parameters']['pixel_size'] = str(ui.pixel_size.value())
        #     cam_config['parameters']['threshold'] = str(ui.threshold.value())
        #     cam_config['parameters']['fps'] = str(ui.fps.value())
        #     with open(cam_config_path, 'w') as configfile:
        #         cam_config.write(configfile)
        # self.DC.cam.change_camera_setting()

    def open_save_ui(self, config_path="./Monitoring/Sensors/ini_files/Main.ini"):
        config = configparser.ConfigParser()
        config.read(config_path)
        dialog = QDialog(self)
        ui = save_UI_Dialog()
        ui.setupUi(dialog)
        ui.lineEdit.setText(str(config['save_path']['path']))

        if dialog.exec_() == QDialog.Accepted:
            self.folder_path = "Monitoring/DB/" + ui.lineEdit.text()
            config['save_path']['path'] = ui.lineEdit.text()
            with open('./Monitoring/Sensors/ini_files/main.ini', 'w') as configfile:
                config.write(configfile)
            print(f"Save Path: {self.folder_path}")
        else:
            print("Dialog canceled")

    def basler_connect(self, checked):
        if checked:
            self.DC.cam.create_camera()
            time.sleep(1)
            if not self.DC.cam.active:
                self.ui.checkbox_cam_active.setChecked(False)
        else:
            self.DC.cam.active=False
            print("Camera stop")

    def exit(self):
        """EXIT 버튼 클릭시 실행중인 모든 기능 정지"""
        self.is_running = False
        self.is_saving = False
        self.DC.cnc_thread.join()
        # self.DC.cam_collector.running=False
        # self.DC.cnc_collector.running-False