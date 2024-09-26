import re
import subprocess

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSizePolicy, QLabel, QPushButton, QCheckBox, QHBoxLayout, \
    QComboBox, QLineEdit, QTextEdit, QFileDialog, QSpacerItem

from ui import INSTALL_APKS_PATH


class InstallApp(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, apk_path, device):
        super().__init__()
        self.apk_path = apk_path
        self.device = device

    def run(self):
        try:
            if self.apk_path.endswith('.apk'):
                command = f"adb -s {self.device} install {self.apk_path}"
            elif self.apk_path.endswith('.apks'):
                operations_tab = OperationsTab()
                is_devices = operations_tab.get_device_list()
                if len(is_devices) > 1:
                    self.error.emit("当前连接多台设备,无法安装apks")
                    return
                command = f"java -jar {INSTALL_APKS_PATH} install-apks --apks={self.apk_path}"
            elif ".hap" in self.apk_path:
                replace_file_path = self.apk_path.replace('/', '\\')
                command = f"hdc app install {replace_file_path}"
            else:
                self.error.emit("请检查文件格式是否正确")
                return
            self.status.emit(f"正在安装 {self.apk_path} ......")
            result = subprocess.run(command, capture_output=True, text=True, creationflags=0x08000000)
            if result.returncode == 0:
                self.finished.emit(f"{self.apk_path} 安装成功")
            else:
                self.error.emit(f"{self.apk_path} 安装失败")
        except subprocess.CalledProcessError as e:
            self.error.emit(f"安装 {self.apk_path} 文件时出现错误: {e.stderr}")


class OperationsTab(QWidget):
    def __init__(self):
        super().__init__()
        # 在此添加预设的鸿蒙应用的安装包名
        self.hdc_package_options = {
            "com.xingin.xhs_hos": "鸿蒙小红书",
            "com.xunlei.thunder": "鸿蒙迅雷",
            "com.ovital.ovitalMapHm": "鸿蒙奥维互动地图"
        }
        # 在此添加预设的安卓应用的包名
        self.adb_package_options = {
            "com.taobao.taobao": "淘宝",
            "com.ss.android.ugc.aweme": "抖音",
            "com.autonavi.minimap": "高德地图",
            "com.think.earth": "Earth Maps",
        }
        # 设置QComboBox、QLineEdit的统一大小
        size_policy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        device_label = QLabel("设备列表:")
        self.device_combox = QComboBox()  # 设备下拉列表
        self.device_combox.setSizePolicy(size_policy)
        self.device_combox.setToolTip("当前与电脑连接的设备")
        refresh_btn = QPushButton("刷新设备")
        refresh_btn.setToolTip("查看当前的设备连接情况")
        refresh_btn.clicked.connect(self.refresh_device_list)
        self.harmonyOS_btn = QCheckBox(" 鸿蒙系统")
        self.harmonyOS_btn.setToolTip("测试鸿蒙应用时,勾选此项")
        self.harmonyOS_btn.toggled.connect(self.click_harmonyOS_update_btn)
        device_layout = QHBoxLayout()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combox)
        device_layout.addWidget(refresh_btn)
        device_layout.addWidget(self.harmonyOS_btn)

        install_uninstall_clear_gb = QGroupBox("应用安装/卸载/清除数据")
        install_uninstall_clear_layout = QVBoxLayout()
        self.install_text = QLineEdit()  # 安装应用输入框，接收输入的安装包路径
        self.install_text.setDragEnabled(True)
        self.install_text.setSizePolicy(size_policy)
        self.install_text.setToolTip("输入电脑上完整的安装包路径或者拖拽安装包文件至此窗口，也可点击“浏览”选择安装包文件")
        self.install_text.dragEnterEvent = self.handle_install_text_dragEnterEvent
        self.install_text.dropEvent = self.handle_install_text_dropEvent
        install_btn = QPushButton("安装")
        install_btn.setToolTip("在指定设备上，安装.apk/.apks/.hap格式的安装包")
        install_btn.clicked.connect(self.click_install_btn)
        view_btn = QPushButton("浏览")
        view_btn.setToolTip("打开文件夹，选择安装包")
        view_btn.clicked.connect(self.click_browse_btn)
        install_layout = QHBoxLayout()
        install_layout.addWidget(self.install_text)
        install_layout.addWidget(install_btn)
        install_layout.addWidget(view_btn)
        self.app_option_combox = QComboBox()  # app下拉列表
        self.app_option_combox.setSizePolicy(size_policy)
        self.app_option_combox.setToolTip("输入应用包名或者从预设的下拉列表中选择应用")
        self.app_option_combox.addItems(self.adb_package_options.values())
        self.app_option_combox.setEditable(True)  # 设置为可编辑
        self.app_option_combox.setCurrentText("")  # 设置默认选项
        uninstall_btn = QPushButton("卸载")
        uninstall_btn.setToolTip("卸载指定的应用")
        uninstall_btn.clicked.connect(self.click_uninstall_btn)
        clear_cache_btn = QPushButton("清除数据")
        clear_cache_btn.setToolTip("清除指定应用的应用数据")
        clear_cache_btn.clicked.connect(self.click_clear_btn)
        uninstall_layout = QHBoxLayout()
        uninstall_layout.addWidget(self.app_option_combox)
        uninstall_layout.addWidget(uninstall_btn)
        uninstall_layout.addWidget(clear_cache_btn)
        install_uninstall_clear_layout.addLayout(install_layout)
        install_uninstall_clear_layout.addLayout(uninstall_layout)
        install_uninstall_clear_gb.setLayout(install_uninstall_clear_layout)

        # self.window_top_btn = QPushButton("窗口置顶")
        # self.window_top_btn.setToolTip("让这个窗口显示在其他窗口上方")
        # self.window_top_btn.setCheckable(True)  # 窗口固定可选中
        # self.window_top_btn.clicked.connect(self.click_window_top)
        # window_layout = QHBoxLayout()
        # self.spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # window_layout.addItem(self.spacer_item)
        # window_layout.addWidget(self.window_top_btn)
        self.console = QTextEdit()
        self.console.setReadOnly(True)  # 只读，不能编辑
        console_groupbox = QGroupBox("调试输出")
        console_layout = QVBoxLayout()
        console_layout.addWidget(self.console)

        clear_button = QPushButton("清空")
        clear_button.setToolTip("清空[调试输出]中的信息")
        clear_button.clicked.connect(self.clear_console_output)
        console_layout.addWidget(clear_button)
        console_groupbox.setLayout(console_layout)

        operations_tab = QVBoxLayout()
        operations_tab.addLayout(device_layout)
        operations_tab.addWidget(install_uninstall_clear_gb)
        # operations_tab.addLayout(window_layout)
        operations_tab.addWidget(console_groupbox)
        self.operation_groupbox = QGroupBox()
        self.operation_groupbox.setLayout(operations_tab)
        self.setLayout(operations_tab)

    # 刷新设备列表
    def refresh_device_list(self):
        self.device_combox.clear()
        devices = self.get_device_list()
        self.device_combox.addItems(devices)

    # 获取连接的安卓手机设备
    def get_device_list(self):
        devices = []
        try:
            if self.harmonyOS_btn.isChecked():
                hdc_output = subprocess.check_output(["hdc", "list", "targets"], creationflags=0x08000000).decode(
                    "utf-8")
                lines = hdc_output.strip().split("\n")
                device_output = "当前连接的设备及连接状态：\n"
                for line in lines:
                    device = line.strip()
                    device_output += f"{device}\n"
                    devices.append(device)
                self.display_output(device_output)
            else:
                adb_output = subprocess.check_output(["adb", "devices"], creationflags=0x08000000).decode("utf-8")
                filtered_output = re.sub(r"List of devices attached\n", "", adb_output)
                lines = filtered_output.strip().split("\n")
                device_output = "当前连接的设备及连接状态：\n"
                for line in lines[1:]:
                    device = line.split("\t")[0]
                    status = line.split("\t")[1]
                    device_output += f"{device}\t{status}\n"
                    devices.append(device)
                self.display_output(device_output)
        except subprocess.CalledProcessError:
            if self.harmonyOS_btn.isChecked():
                self.display_output("无法获取设备列表，请确保HDC已正确安装和配置。")
            else:
                self.display_output("无法获取设备列表，请确保ADB已正确安装和配置。")
        return devices

    def click_browse_btn(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择apk/apks/hap文件", "", "install files (*.apk *.apks *.hap)")
        if file_path:
            self.install_text.setText(file_path)

    def click_install_btn(self):
        apk_path = self.install_text.text()
        device = self.device_combox.currentText()
        if not device:
            self.display_output("请选择要安装到的设备")
            return
        if not apk_path:
            self.display_output("请选择要安装的apk/apks文件")
            return
        self.install_thread = InstallApp(apk_path, device)
        self.install_thread.finished.connect(self.handle_install_finished)
        self.install_thread.error.connect(self.handle_install_error)
        self.install_thread.status.connect(self.handle_install_status)
        self.install_thread.start()

    def handle_install_finished(self, message):
        self.display_output(message)

    def handle_install_error(self, error):
        self.display_output(error)

    def handle_install_status(self, status):
        self.display_output(status)

    #  获取app下拉列表中的应用名
    def get_package_name(self):
        selected_option = self.app_option_combox.currentText()
        app_options = self.hdc_package_options if self.harmonyOS_btn.isChecked() else self.adb_package_options
        if not self.device_combox.currentText():
            self.display_output("请选择设备")
            return
        if not selected_option:
            self.display_output("请输入应用包名,或者从下拉列表中选择")
            return selected_option
        for key, value in app_options.items():
            if value == selected_option:
                selected_option = key
                break
        return selected_option

    # 卸载应用
    def click_uninstall_btn(self):
        package_name = self.get_package_name()
        if package_name is None:
            return
        try:
            if self.harmonyOS_btn.isChecked():
                command = ["hdc", "uninstall", package_name]
            else:
                command = ["adb", "-s", self.device_combox.currentText(), "uninstall", package_name]
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.display_output(f"{package_name} 应用卸载成功")
            else:
                self.display_output("卸载失败，请检查输入框中的包名是否正确以及设备上是否存在该应用")
        except subprocess.CalledProcessError as e:
            self.display_output(f"卸载 {package_name} 应用时出错：{e.output.decode('utf-8')}")

    # 清除应用缓存
    def click_clear_btn(self):
        package_name = self.get_package_name()
        if package_name is None:
            return
        try:
            if self.harmonyOS_btn.isChecked():
                command = subprocess.run(
                    ["hdc", "shell", "bm", "clean", "-n", package_name, "-d"],
                    capture_output=True, text=True, shell=True)
            else:
                command = subprocess.run(
                    ["adb", "-s", self.device_combox.currentText(), "shell", "pm", "clear", package_name],
                    capture_output=True, text=True, shell=True)
            if command.returncode == 0:
                self.display_output(package_name + "已清除缓存")
            else:
                self.display_output("清除应用缓存失败，请检查输入框中的包名是否正确以及设备上是否存在该应用")
        except subprocess.CalledProcessError as e:
            self.display_output(f"清除 {package_name} 缓存时出错：{e.stderr}")

    @staticmethod
    def handle_install_text_dragEnterEvent(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 拖动物体释放到QLineEdit区域时被调用
    def handle_install_text_dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.install_text.setText(file_path)

    # 当勾选鸿蒙设备时更新卸载应用下拉框的状态
    def click_harmonyOS_update_btn(self, checked):
        if checked:
            self.app_option_combox.clear()
            self.app_option_combox.addItems(self.hdc_package_options.values())
        else:
            self.app_option_combox.clear()
            self.app_option_combox.addItems(self.adb_package_options.values())
        self.app_option_combox.setCurrentText("")

    # 窗口置顶
    # def click_window_top(self):
    #     if self.window_top_btn.isChecked():
    #         self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    #     else:
    #         self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
    #     self.show()

    # 控制台输出
    def display_output(self, message):
        self.console.append(message)

    # 清空控制台输出
    def clear_console_output(self):
        self.console.clear()
