import datetime
import os
import re
import subprocess
import time

from PyQt6.QtCore import QTimer, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QFrame, QStatusBar, QGroupBox, QFileDialog, QLabel, QTableView, QHeaderView, QComboBox


class OtherFunctionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.recording_proc = None
        self.recording_file_name = None
        self.log_file_name = None
        self.log_proc = None

        h_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # 水平弹簧
        v_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)  # 垂直弹簧
        v_spacer_10 = QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)  # 垂直间距10像素的弹簧

        select_path_btn = QPushButton("保存路径")
        select_path_btn.setToolTip("选择截图/录屏/日志文件保存路径")
        self.output_path_le = QLineEdit()
        self.output_path_le.setReadOnly(True)
        other_functions_tab_vl = QVBoxLayout()
        file_path_hl = QHBoxLayout()
        file_path_hl.addWidget(select_path_btn)
        file_path_hl.addWidget(self.output_path_le)

        h_line = QFrame()  # 水平线
        h_line.setFrameShape(QFrame.Shape.HLine)

        screenshot_btn = QPushButton("手机截图")
        screenshot_btn.setToolTip("手机截图并保存到电脑指定的文件夹下,手机相册不会保存截图")
        self.start_recording_btn = QPushButton("手机录屏")
        self.start_recording_btn.setToolTip("进行录屏,最长录制3分钟,3分钟时自动保存")
        self.end_recording_btn = QPushButton("结束录屏")
        self.end_recording_btn.setToolTip("结束录屏并保存录屏文件至电脑,手机相册会生成录屏文件")
        self.end_recording_btn.hide()
        self.recording_time_label = QLabel("00:00")
        self.recording_time_label.hide()
        self.recording_time_label.setStyleSheet("font-weight: bold;")  # 加粗
        screenshot_recording_hl = QHBoxLayout()
        screenshot_recording_hl.addWidget(screenshot_btn)
        screenshot_recording_hl.addWidget(self.start_recording_btn)
        screenshot_recording_hl.addWidget(self.end_recording_btn)
        screenshot_recording_hl.addItem(h_spacer)
        screenshot_recording_hl.addWidget(self.recording_time_label)

        self.status_bar = QStatusBar()  # 状态栏
        self.status_bar.setStyleSheet("background-color: #eeeeee;")  # 状态栏背景色

        log_gb = QGroupBox("日志")
        self.log_start_btn = QPushButton("开始")
        self.log_start_btn.setToolTip("进行日志记录")
        self.log_end_btn = QPushButton("结束")
        self.log_end_btn.setToolTip("结束日志记录并保存到电脑指定文件夹下")
        self.log_end_btn.hide()
        first_hl = QHBoxLayout()
        first_hl.addWidget(self.log_start_btn)
        first_hl.addWidget(self.log_end_btn)
        first_hl.addItem(h_spacer)

        self.select_log_file_btn = QPushButton("选择日志文件")
        self.select_log_file_btn.setToolTip("选择日志文件(.txt格式)")
        self.input_log_file_le = QLineEdit()
        self.input_log_file_le.setReadOnly(True)
        self.analyse_log_btn = QPushButton("分析")
        self.analyse_log_btn.setToolTip("分析日志文件中的异常关键字")

        self.log_table_view = QTableView()
        self.log_table_view.setVisible(False)
        self.log_table_model = QStandardItemModel()
        self.log_table_view.setModel(self.log_table_model)
        # 创建 QSortFilterProxyModel
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.log_table_model)
        self.filter_proxy_model.setFilterKeyColumn(0)  # 设置过滤的列为"类型"列
        self.log_table_view.setModel(self.filter_proxy_model)

        self.log_filter_label = QLabel("选择过滤异常类型 :")
        self.log_filter_label.setVisible(False)
        self.log_filter_label.setStyleSheet("font-weight: bold;")
        # 添加过滤输入框
        self.log_filter_cb = QComboBox()
        self.log_filter_cb.addItems(["All", "Fatal", "ANR", "Error", "Exception"])
        self.log_filter_cb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.log_filter_cb.setVisible(False)
        log_filter_hl = QHBoxLayout()
        log_filter_hl.addWidget(self.log_filter_label)
        log_filter_hl.addWidget(self.log_filter_cb)

        second_hl = QHBoxLayout()
        second_hl.addWidget(self.select_log_file_btn)
        second_hl.addWidget(self.input_log_file_le)
        second_hl.addWidget(self.analyse_log_btn)

        log_vl = QVBoxLayout()
        log_vl.addLayout(first_hl)
        log_vl.addLayout(second_hl)
        log_vl.addLayout(log_filter_hl)
        log_vl.addWidget(self.log_table_view, stretch=1)
        log_vl.addItem(v_spacer)
        log_gb.setLayout(log_vl)

        other_functions_tab_vl.addLayout(file_path_hl)
        other_functions_tab_vl.addItem(v_spacer_10)
        other_functions_tab_vl.addWidget(h_line)
        other_functions_tab_vl.addItem(v_spacer_10)
        other_functions_tab_vl.addLayout(screenshot_recording_hl)
        other_functions_tab_vl.addItem(v_spacer_10)
        other_functions_tab_vl.addWidget(log_gb, stretch=1)
        other_functions_tab_vl.addItem(v_spacer)
        other_functions_tab_vl.addWidget(self.status_bar)
        self.setLayout(other_functions_tab_vl)

        # 计时器
        self.recording_timer = QTimer()
        self.recording_timer.setInterval(1000)  # 1秒更新一次
        self.recording_timer.timeout.connect(self.update_timer)
        self.recording_duration = 0

        # 按钮事件
        select_path_btn.clicked.connect(self.select_file_path)
        screenshot_btn.clicked.connect(self.take_screenshot)
        self.start_recording_btn.clicked.connect(self.start_recording)
        self.end_recording_btn.clicked.connect(self.end_recording)
        self.log_start_btn.clicked.connect(self.start_logging)
        self.log_end_btn.clicked.connect(self.end_logging)
        self.log_filter_cb.currentTextChanged.connect(self.set_log_filter)
        self.select_log_file_btn.clicked.connect(self.select_log_file)
        self.analyse_log_btn.clicked.connect(self.analyse_log)

    # 选择保存的文件夹
    def select_file_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if folder_path:
            self.output_path_le.setText(folder_path)
            self.status_bar.showMessage(f"已选择保存路径:{folder_path}")

    # 截图
    def take_screenshot(self):
        save_folder = self.check_save_file_path()
        if not save_folder:
            return
        screenshot_file_name = os.path.join(save_folder, f"screen_{datetime.datetime.now().strftime('%Y%m%d%H%S')}.png")
        subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=open(screenshot_file_name, "wb"))
        self.status_bar.showMessage(f"截图已保存至: {screenshot_file_name}")

    # 开始录制
    def start_recording(self):
        save_folder = self.check_save_file_path()
        if not save_folder:
            return
        self.start_recording_btn.hide()
        self.end_recording_btn.show()
        self.recording_timer.start()
        self.recording_time_label.show()

        self.recording_file_name = os.path.join(save_folder,
                                                f"video_{datetime.datetime.now().strftime('%Y%m%d%H%S')}.mp4")
        self.recording_proc = subprocess.Popen(["adb", "shell", "screenrecord", "/sdcard/" +
                                                os.path.basename(self.recording_file_name)])
        self.status_bar.showMessage("正在录屏中......")

    # 结束录制
    def end_recording(self):
        self.recording_timer.stop()
        self.end_recording_btn.hide()
        self.start_recording_btn.show()
        self.recording_proc.terminate()
        self.recording_proc.wait()
        time.sleep(0.5)  # 结束进程后不能马上拉取文件会导致视频无法播放
        subprocess.run(["adb", "pull", "/sdcard/" +
                        os.path.basename(self.recording_file_name), self.recording_file_name])
        self.recording_time_label.setText("00:00")
        self.recording_time_label.hide()
        self.recording_duration = 0
        self.status_bar.showMessage(f"录屏已保存至: {self.recording_file_name}")

    # 开始记录日志
    def start_logging(self):
        save_folder = self.check_save_file_path()
        if not save_folder:
            return
        self.log_start_btn.hide()
        self.log_end_btn.show()
        self.log_file_name = os.path.join(save_folder, f"log_{datetime.datetime.now().strftime('%Y%m%d%H%S')}.txt")
        subprocess.run(["adb", "logcat", "-c"])
        self.log_proc = subprocess.Popen(["adb", "logcat", "-v", "time"], stdout=open(self.log_file_name, "wb"))
        self.status_bar.showMessage("正在记录日志......")

    # 结束记录日志
    def end_logging(self):
        self.log_end_btn.hide()
        self.log_start_btn.show()
        self.log_proc.terminate()
        self.log_proc.wait()
        self.status_bar.showMessage(f"日志已保存至: {self.log_file_name}")

    # 更新时间
    def update_timer(self):
        self.recording_duration += 1
        minutes = self.recording_duration // 60
        seconds = self.recording_duration % 60
        self.recording_time_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.recording_duration >= 180:  # 如果录屏时间达到 3 分钟,自动停止录屏
            self.end_recording()

    # 选择日志文件
    def select_log_file(self):
        log_file_path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", "", "日志文件 (*.txt)")
        if log_file_path:
            self.input_log_file_le.setText(log_file_path)

    # 检查是否选择保存路径
    def check_save_file_path(self):
        save_path = self.output_path_le.text()
        if not save_path:
            self.status_bar.showMessage("请先选择保存路径")
            return False
        return save_path

    def set_log_filter(self, filter_text):
        if filter_text == "All":
            self.filter_proxy_model.setFilterRegularExpression("")
        else:
            self.filter_proxy_model.setFilterRegularExpression(rf"(?i){filter_text}")
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    # 分析日志
    def analyse_log(self):
        log_file_path = self.input_log_file_le.text()
        if not log_file_path:
            self.status_bar.showMessage("请先选择日志文件")
            return

        self.log_table_model.clear()  # 清除之前的结果
        self.log_table_model.setHorizontalHeaderLabels(["类型", "行号", "异常信息"])  # 设置表头
        table_header = self.log_table_view.horizontalHeader()
        table_header.setStretchLastSection(True)  # 最后一列占满剩余宽度
        table_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 其余列自适应宽度
        table_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                log_lines = log_file.readlines()
                exceptions = []  # 用于存储异常信息
                # 正则表达式匹配异常行
                exception_pattern = re.compile(r'(?i)(exception|error|fatal|anr in)', re.MULTILINE)

                for line_number, line in enumerate(log_lines, start=1):
                    if exception_pattern.search(line):
                        if exception_pattern.search(line):
                            exception_type = None
                            if 'fatal' in line.lower():
                                exception_type = 'Fatal'
                            elif 'anr in' in line.lower():
                                exception_type = 'ANR'
                            elif 'error' in line.lower():
                                exception_type = 'Error'
                            elif 'exception' in line.lower():
                                exception_type = 'Exception'
                            exception_message = re.search(r'\(.*?\):\s*(.*)', line.strip()).group(1)
                            exceptions.append((exception_type, line_number, exception_message))  # 记录行号和信息

                # 将异常信息填充到日志表
                for exception_type, line_number, exception_message in exceptions:
                    row = [
                        QStandardItem(exception_type or 'Unknown'),  # 异常类型
                        QStandardItem(str(line_number)),  # 行号
                        QStandardItem(exception_message)  # 异常信息
                    ]
                    self.log_table_model.appendRow(row)

            if exceptions:
                self.log_filter_cb.setVisible(True)
                self.log_table_view.setVisible(True)
                self.log_filter_label.setVisible(True)
                self.status_bar.showMessage(f"共找到 {len(exceptions)} 个异常信息")
            else:
                self.log_filter_cb.setVisible(False)
                self.log_table_view.setVisible(False)
                self.log_filter_label.setVisible(False)
                self.status_bar.showMessage("未找到异常信息")

            # 设置过滤模型
            self.filter_proxy_model.setSourceModel(self.log_table_model)
            self.filter_proxy_model.setFilterKeyColumn(0)

        except Exception as e:
            self.status_bar.showMessage(f"分析日志时出错: {str(e)}")

    def __del__(self):
        self.recording_timer.stop()
        self.recording_timer.deleteLater()
