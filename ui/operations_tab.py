import datetime
import re
import subprocess

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSizePolicy, QLabel, QPushButton, QCheckBox, QHBoxLayout, \
    QComboBox, QLineEdit, QTextEdit, QFileDialog

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
        self.device_combox = QComboBox()  # 设备下拉列表
        self.device_combox.setSizePolicy(size_policy)
        self.device_combox.setToolTip("选择要操作的设备")
        refresh_btn = QPushButton("刷新设备")
        refresh_btn.setToolTip("查看当前设备的连接情况")
        refresh_btn.clicked.connect(self.refresh_device_list)
        self.harmonyOS_btn = QCheckBox(" 鸿蒙系统")
        self.harmonyOS_btn.setToolTip("测试鸿蒙应用时,勾选此项")
        self.harmonyOS_btn.toggled.connect(self.click_harmonyOS_update_btn)
        device_usb_layout = QHBoxLayout()
        device_usb_layout.addWidget(self.device_combox)
        device_usb_layout.addWidget(refresh_btn)
        device_usb_layout.addWidget(self.harmonyOS_btn)

        self.input_ip_address_le = QLineEdit()
        regex = QRegularExpression(r"[0-9.]+")  # 只允许输入数字和小数点
        validator = QRegularExpressionValidator(regex, self.input_ip_address_le)
        self.input_ip_address_le.setValidator(validator)  # 设置验证器
        self.input_ip_address_le.setPlaceholderText(" 输入手机的IP地址")
        self.input_ip_address_le.setSizePolicy(size_policy)
        connect_device_btn = QPushButton("无线连接")
        connect_device_btn.clicked.connect(self.connect_device_withIP)
        disconnect_device_btn = QPushButton("断开连接")
        disconnect_device_btn.clicked.connect(self.disconnect_device_withIP)
        get_ip_address_btn = QPushButton("?")
        get_ip_address_btn.setFixedSize(20, 20)
        get_ip_address_btn.setToolTip("获取当前连接设备的IP地址")
        get_ip_address_btn.clicked.connect(self.get_device_ip_address)
        device_ip_layout = QHBoxLayout()
        device_ip_layout.addWidget(self.input_ip_address_le)
        device_ip_layout.addWidget(get_ip_address_btn)
        device_ip_layout.addWidget(connect_device_btn)
        device_ip_layout.addWidget(disconnect_device_btn)

        device_gb = QGroupBox("设备连接")
        device_layout = QVBoxLayout()
        device_layout.addLayout(device_usb_layout)
        device_layout.addLayout(device_ip_layout)
        device_gb.setLayout(device_layout)

        install_uninstall_clear_gb = QGroupBox("应用安装/卸载/清除数据")
        install_uninstall_clear_layout = QVBoxLayout()
        self.input_install_path_le = QLineEdit()  # 安装应用输入框，接收输入的安装包路径
        self.input_install_path_le.setDragEnabled(True)
        self.input_install_path_le.setSizePolicy(size_policy)
        self.input_install_path_le.setToolTip("输入电脑上完整的安装包路径或者拖拽安装包文件至此窗口，也可点击“浏览”选择安装包文件")
        self.input_install_path_le.dragEnterEvent = self.handle_install_text_dragEnterEvent
        self.input_install_path_le.dropEvent = self.handle_install_text_dropEvent
        install_btn = QPushButton("安装")
        install_btn.setToolTip("在指定设备上，安装.apk/.apks/.hap格式的安装包")
        install_btn.clicked.connect(self.click_install_btn)
        view_btn = QPushButton("浏览")
        view_btn.setToolTip("打开文件夹，选择安装包")
        view_btn.clicked.connect(self.click_browse_btn)
        install_layout = QHBoxLayout()
        install_layout.addWidget(self.input_install_path_le)
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

        self.window_top_btn = QPushButton("窗口置顶")
        self.window_top_btn.setToolTip("让这个窗口显示在其他窗口上方")
        self.window_top_btn.setCheckable(True)  # 窗口固定可选中
        self.window_top_btn.clicked.connect(self.click_window_top)
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
        operations_tab.addWidget(self.window_top_btn)
        operations_tab.addWidget(device_gb)
        operations_tab.addWidget(install_uninstall_clear_gb)
        operations_tab.addWidget(console_groupbox)
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
            self.input_install_path_le.setText(file_path)

    def click_install_btn(self):
        apk_path = self.input_install_path_le.text()
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
            self.display_output(f"卸载 {package_name} 应用时出错：{e.stderr}")

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
            self.display_output(f"{package_name}清除缓存报错：{e.stderr}")

    @staticmethod
    def handle_install_text_dragEnterEvent(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 拖动物体释放到QLineEdit区域时被调用
    def handle_install_text_dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.input_install_path_le.setText(file_path)

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
    def click_window_top(self):
        if self.window_top_btn.isChecked():
            self.window().setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.window().setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.window().show()

    # 控制台输出
    def display_output(self, message):
        timestamp = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
        output = f"[{timestamp}] {message}"
        self.console.append(output)

    # 清空控制台输出
    def clear_console_output(self):
        self.console.clear()

    # 获取手机的IP地址
    def get_device_ip_address(self):
        device = self.device_combox.currentText()
        if not device:
            self.display_output("没有USB连接的设备,请先使用USB连接")
            return
        try:
            command = subprocess.check_output(["adb", "-s", device, "shell", "ip", "addr", "show", "wlan0"])
            output = command.decode("utf-8")
            # 使用正则表达式提取IP地址
            format_output = r"inet\s+(\d+\.\d+\.\d+\.\d+)\/\d+"
            match = re.search(format_output, output)
            if match:
                ip_address = match.group(1)
                self.input_ip_address_le.setText(ip_address)
                self.display_output(f"当前设备 IP 地址: {ip_address}")
            else:
                self.display_output("无法获取设备IP地址")
        except subprocess.CalledProcessError as e:
            self.display_output(f"获取IP地址失败.报错:{e.stderr}")

    # 无线连接
    def connect_device_withIP(self):
        ip_address = self.input_ip_address_le.text().strip()
        if not ip_address:
            self.display_output("请先输入地址")
            return
        try:
            # 检查当前电脑是否已经监听5555 端口号
            output = subprocess.run(["netstat", "-an"], capture_output=True, text=True, check=True)
            is_port_listening = ":5555" in output.stdout
            # 未监听则先监听5555 端口号
            if not is_port_listening:
                subprocess.run(["adb", "tcpip", "5555"], capture_output=True, text=True, check=True)
            subprocess.run(["adb", "connect", f"{ip_address}:5555"], capture_output=True, text=True, check=True)
            self.display_output("无线连接成功")
            self.refresh_device_list()
        except subprocess.CalledProcessError as e:
            self.display_output(f"无线连接失败.报错:{e.stderr}")

    # 断开无线连接
    def disconnect_device_withIP(self):
        ip_address = self.input_ip_address_le.text().strip()
        if not ip_address:
            self.display_output("请先输入要断开连接设备的IP地址")
            return
        try:
            subprocess.run(["adb", "disconnect", ip_address], capture_output=True, text=True, check=True)
            self.display_output(f"{ip_address}已断开无线连接")
            self.refresh_device_list()
        except subprocess.CalledProcessError as e:
            self.display_output(f"断开连接失败.报错:{e.stderr}")
