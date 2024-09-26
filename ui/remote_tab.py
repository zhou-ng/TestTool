import subprocess
from PyQt6.QtWidgets import QGridLayout, QWidget, QPushButton, QGroupBox


class RemoteTab(QWidget):
    def __init__(self):
        super().__init__()
        self.remote_groupbox = QGroupBox()
        grid_layout = QGridLayout()

        # 按钮配置
        button_configs = [
            # 按钮名称, 行,列,key_event
            ("上", 0, 1, 19),
            ("左", 1, 0, 21),
            ("确认", 1, 1, 23),
            ("右", 1, 2, 22),
            ("下", 2, 1, 20),
            ("Home", 3, 0, 3),
            ("返回", 3, 2, 4)
        ]
        # 创建按钮
        for text, row, col, key_event in button_configs:
            button = QPushButton(text)
            button.setFixedSize(100, 35)
            button.clicked.connect(lambda _, ke=key_event: self.send_input_event(ke))
            grid_layout.addWidget(button, row, col)

        self.remote_groupbox.setLayout(grid_layout)
        self.setLayout(grid_layout)

    @staticmethod
    def send_input_event(event_code):
        subprocess.run(f"adb shell input keyevent {event_code}")
