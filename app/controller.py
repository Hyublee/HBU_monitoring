from PySide2.QtCore import QTimer, QDateTime

def setup_connections(window):
    ui = window.ui

    ui.Save_btn.clicked.connect(lambda: save_clicked(window))
    ui.Exit_btn.clicked.connect(lambda: exit_clicked(window))

def setup_timers(window):
    window.current_time_timer = QTimer()
    window.current_time_timer.timeout.connect(lambda: update_time(window))
    window.current_time_timer.start(1000)

def update_time(window):
    now = QDateTime.currentDateTime()
    window.ui.current_time.setDateTime(now)

def save_clicked(window):
    print("Save clicked")  # 실제 기능 연결은 collector에 위임

def exit_clicked(window):
    window.close()
