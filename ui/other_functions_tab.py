import datetime
import os
import subprocess
import time

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QFrame, QStatusBar, QGroupBox, QFileDialog, QLabel


class OtherFunctionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.recording_porc = None
        h_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # 水平弹簧
        v_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)  # 垂直弹簧
        v_spacer_25 = QSpacerItem(0, 25, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)  # 垂直间距25像素的弹簧
        v_spacer_10 = QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)  # 垂直间距10像素的弹簧

        select_path_btn = QPushButton("选择路径")
        self.output_path_le = QLineEdit()
        self.output_path_le.setReadOnly(True)
        other_functions_tab_vl = QVBoxLayout()
        file_path_hl = QHBoxLayout()
        file_path_hl.addWidget(select_path_btn)
        file_path_hl.addWidget(self.output_path_le)

        h_line = QFrame()  # 水平线
        h_line.setFrameShape(QFrame.Shape.HLine)

        screenshot_btn = QPushButton("手机截图")
        self.start_recording_btn = QPushButton("手机录屏")
        self.end_recording_btn = QPushButton("结束录屏")
        self.end_recording_btn.hide()
        screenshot_recording_hl = QHBoxLayout()
        screenshot_recording_hl.addWidget(screenshot_btn)
        screenshot_recording_hl.addWidget(self.start_recording_btn)
        screenshot_recording_hl.addWidget(self.end_recording_btn)
        screenshot_recording_hl.addItem(h_spacer)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #eeeeee;")

        log_gb = QGroupBox("日志")
        self.log_start_btn = QPushButton("开始")
        self.log_end_btn = QPushButton("结束")
        self.log_end_btn.hide()
        log_hl = QHBoxLayout()
        log_hl.addWidget(self.log_start_btn)
        log_hl.addWidget(self.log_end_btn)
        log_hl.addItem(h_spacer)
        log_gb.setLayout(log_hl)

        self.recording_time_label = QLabel("00:00")
        self.recording_time_label.setStyleSheet("font-weight: bold;")  # 加粗
        timer_hl = QHBoxLayout()
        timer_hl.addItem(h_spacer)
        timer_hl.addWidget(self.recording_time_label)

        other_functions_tab_vl.addLayout(file_path_hl)
        other_functions_tab_vl.addItem(v_spacer_10)
        other_functions_tab_vl.addWidget(h_line)
        other_functions_tab_vl.addItem(v_spacer_25)
        other_functions_tab_vl.addLayout(screenshot_recording_hl)
        other_functions_tab_vl.addItem(v_spacer_25)
        other_functions_tab_vl.addWidget(log_gb)
        other_functions_tab_vl.addItem(v_spacer)
        other_functions_tab_vl.addLayout(timer_hl)
        other_functions_tab_vl.addWidget(self.status_bar)
        self.setLayout(other_functions_tab_vl)

        self.recording_timer = QTimer()
        self.recording_timer.setInterval(1000)  # 1秒更新一次
        self.recording_timer.timeout.connect(self.update_time)
        self.recording_duration = 0
        self.recording_file_name = None

        select_path_btn.clicked.connect(self.select_file_path)
        screenshot_btn.clicked.connect(self.take_screenshot)
        self.start_recording_btn.clicked.connect(self.start_recording)
        self.end_recording_btn.clicked.connect(self.end_recording)

    def select_file_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if folder_path:
            self.output_path_le.setText(folder_path)
            self.status_bar.showMessage(f"已选择保存路径:{folder_path}")

    def take_screenshot(self):
        save_folder = self.output_path_le.text()
        if not save_folder:
            self.status_bar.showMessage("请先选择保存路径")
            return
        screenshot_path = os.path.join(save_folder, f"{datetime.datetime.now().strftime('%Y%m%d%H%S')}.png")
        subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=open(screenshot_path, "wb"))
        self.status_bar.showMessage(f"截图已保存至: {screenshot_path}")

    def start_recording(self):
        save_folder = self.output_path_le.text()
        if not save_folder:
            self.status_bar.showMessage("请先选择保存路径")
            return
        self.start_recording_btn.hide()
        self.end_recording_btn.show()
        self.recording_timer.start()

        date = datetime.datetime.now().strftime('%Y%m%d')
        file_name = f"{date}_1.mp4"
        file_path = os.path.join(save_folder, file_name)

        # 检查文件是否存在,如果存在则递增数字
        i = 1
        while os.path.exists(file_path):
            i += 1
            file_name = f"{date}_{i}.mp4"
            file_path = os.path.join(save_folder, file_name)
        self.recording_file_name = file_path

        self.recording_porc = subprocess.Popen(["adb", "shell", "screenrecord", "/sdcard/" + os.path.basename(file_path)])
        self.status_bar.showMessage("正在录屏中......")

    def end_recording(self):
        self.recording_timer.stop()
        self.end_recording_btn.hide()
        self.start_recording_btn.show()
        self.recording_porc.terminate()
        time.sleep(0.5)  # 结束进程后不能马上拉取文件会导致文件不完整,使用self.proc.wait()也不能解决
        subprocess.run(["adb", "pull", "/sdcard/" + os.path.basename(self.recording_file_name), self.recording_file_name])
        # 删除手机中的录屏文件
        subprocess.run(["adb", "shell", "rm", "/sdcard/" + os.path.basename(self.recording_file_name)])
        self.recording_time_label.setText("00:00")
        self.recording_duration = 0
        self.status_bar.showMessage(f"录屏已保存至: {self.recording_file_name}")

    def update_time(self):
        self.recording_duration += 1
        minutes = self.recording_duration // 60
        seconds = self.recording_duration % 60
        self.recording_time_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.recording_duration >= 180:  # 如果录屏时间达到 3 分钟,自动停止录屏
            self.end_recording()

    def __del__(self):
        self.recording_timer.stop()
        self.recording_timer.deleteLater()
