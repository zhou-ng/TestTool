import subprocess
from PyQt6.QtWidgets import QGridLayout, QWidget, QPushButton, QGroupBox, QStatusBar, QSizePolicy, QVBoxLayout, \
    QSpacerItem


class RemoteTab(QWidget):
    def __init__(self):
        super().__init__()
        self.remote_groupbox = QGroupBox()
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(30)  # 行间距

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
        v_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.status_bar = QStatusBar()  # 添加状态栏
        self.status_bar.setStyleSheet("background-color: #eeeeee;")
        remote_tab_vl = QVBoxLayout()
        remote_tab_vl.addItem(v_spacer)
        remote_tab_vl.addLayout(grid_layout)
        remote_tab_vl.addItem(v_spacer)
        remote_tab_vl.addWidget(self.status_bar)
        self.setLayout(remote_tab_vl)

    def send_input_event(self, event_code):
        subprocess.run(f"adb shell input keyevent {event_code}")
        button_names = {
            19: "上",
            21: "左",
            23: "确认",
            22: "右",
            20: "下",
            3: "Home",
            4: "返回"
        }
        get_button_name = button_names.get(event_code, "未知按钮")
        self.status_bar.showMessage(f"点击了 [{get_button_name}] 按钮")
