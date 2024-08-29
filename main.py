import re
import subprocess
import sys

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QColor, QTextCursor, QTextCharFormat
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QTabWidget, QSpacerItem, QSizePolicy, QGridLayout, \
    QCheckBox


class InstallThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, apk_path, device):
        super().__init__()
        self.apk_path = apk_path
        self.device = device

    def run(self):
        try:
            apks_path = "install_apks.jar"  # 安装apks的jar包路径
            if self.apk_path.endswith('.apk'):
                command = f"adb -s {self.device} install {self.apk_path}"
            elif self.apk_path.endswith('.apks'):
                adb_window = AdbWindow()
                is_devices = adb_window.get_device_list()
                if len(is_devices) > 1:
                    self.error.emit("当前连接多台设备,无法安装apks")
                    return
                command = f"java -jar {apks_path} install-apks --apks={self.apk_path}"
            elif ".hap" in self.apk_path:
                replace_file_path = self.apk_path.replace('/', '\\')
                command = f"hdc app install {replace_file_path}"
            else:
                self.error.emit("请检查文件格式是否正确")
                return
            result = subprocess.run(command, capture_output=True, text=True, creationflags=0x08000000)
            if result.returncode == 0:
                self.finished.emit(f"{self.apk_path}安装成功")
            else:
                self.error.emit(f"{self.apk_path}安装失败")
        except subprocess.CalledProcessError as e:
            self.error.emit(f"安装{self.apk_path}文件时出现错误: {e.stderr}")


class AdbWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试小工具")
        self.setWindowIcon(QIcon("./favicon.ico"))
        # 在此添加鸿蒙应用的安装包名
        self.hdc_package_options = {
            "com.xingin.xhs_hos": "鸿蒙小红书",
            "com.xunlei.thunder": "鸿蒙迅雷",
            "com.ovital.ovitalMapHm": "鸿蒙奥维互动地图"
        }
        # 在此添加安卓应用的包名
        self.adb_package_options = {
            "com.taobao.taobao": "淘宝",
            "com.ss.android.ugc.aweme": "抖音",
            "com.autonavi.minimap": "高德地图",
        }
        self.init_ui()

    def init_ui(self):
        self.create_operation_layout()
        self.create_console_layout()
        self.create_permission_layout()
        self.create_remote_layout()

        main_tw = QTabWidget()  # 创建一个选项卡窗口部件
        main_widget = QWidget()  # 创建一个QWidget用于容纳选项卡
        app_operation_layout = QVBoxLayout()  # 在main_widget中使用QVBoxLayout作为布局
        app_operation_layout.addWidget(self.operation_groupbox)
        app_operation_layout.addWidget(self.console_groupbox)
        main_widget.setLayout(app_operation_layout)  # 将主布局设置为main_widget的布局
        main_tw.addTab(main_widget, "应用操作")  # 将main_widget作为选项卡添加到tab_widget中，并设置标题为"安装卸载"
        self.setCentralWidget(main_tw)  # 将tab_widget设置为主窗口的中心部件

        main_tw.addTab(self.permission_groupbox, "应用权限")
        main_tw.addTab(self.remote_groupbox, "模拟遥控")

        main_tw.currentChanged.connect(self.tab_changed)
        self.resize(200, 400)  # 初始化窗口大小 （宽，高）

    # 创建应用操作选项卡中的第一个垂直布局
    def create_operation_layout(self):
        # 设置QComboBox、QLineEdit的统一大小
        size_policy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        device_label = QLabel("设备列表:")
        self.device_combox = QComboBox()  # 设备下拉列表
        self.device_combox.setSizePolicy(size_policy)
        self.device_combox.setToolTip("当前与电脑连接的设备")
        refresh_btn = QPushButton("刷新设备")
        refresh_btn.setToolTip("查看当前的设备连接情况")
        refresh_btn.clicked.connect(self.refresh_device_list)
        self.harmmonyOS_btn = QCheckBox(" 鸿蒙系统")
        self.harmmonyOS_btn.setToolTip("测试鸿蒙应用时,勾选此项")
        self.harmmonyOS_btn.toggled.connect(self.click_harmmonyOS_update_btn)
        device_layout = QHBoxLayout()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combox)
        device_layout.addWidget(refresh_btn)
        device_layout.addWidget(self.harmmonyOS_btn)

        install_label = QLabel("安装应用:")
        self.install_text = QLineEdit()  # 安装应用输入框，接收输入的安装包路径
        self.install_text.setDragEnabled(True)
        self.install_text.setSizePolicy(size_policy)
        # self.install_text.setPlaceholderText("输入或拖拽文件至此")
        self.install_text.setToolTip("输入电脑上完整的安装包路径或者拖拽安装包文件至此窗口，也可点击“浏览”选择安装包文件")
        install_btn = QPushButton("安装")
        install_btn.setToolTip("在指定设备上，安装.apk/.apks/.hap格式的安装包")
        install_btn.clicked.connect(self.click_install_btn)
        view_btn = QPushButton("浏览")
        view_btn.setToolTip("打开文件夹，选择安装包")
        view_btn.clicked.connect(self.click_browse_btn)
        install_layout = QHBoxLayout()
        install_layout.addWidget(install_label)
        install_layout.addWidget(self.install_text)
        install_layout.addWidget(install_btn)
        install_layout.addWidget(view_btn)
        uninstall_label = QLabel("卸载应用:")
        self.app_option_combox = QComboBox()  # app下拉列表
        self.app_option_combox.setSizePolicy(size_policy)
        self.app_option_combox.setToolTip("输入应用包名或者从下拉列表中选择")
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
        uninstall_layout.addWidget(uninstall_label)
        uninstall_layout.addWidget(self.app_option_combox)
        uninstall_layout.addWidget(uninstall_btn)
        uninstall_layout.addWidget(clear_cache_btn)
        self.window_top_btn = QPushButton("窗口置顶")
        self.window_top_btn.setToolTip("让这个窗口永远显示在其他窗口上方")
        self.window_top_btn.setCheckable(True)  # 窗口固定可选中
        self.window_top_btn.clicked.connect(self.click_window_top)
        window_layout = QHBoxLayout()
        self.spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        window_layout.addItem(self.spacer_item)
        window_layout.addWidget(self.window_top_btn)
        self.operation_groupbox = QGroupBox()
        main_layout = QVBoxLayout()
        main_layout.addLayout(device_layout)
        main_layout.addLayout(install_layout)
        main_layout.addLayout(uninstall_layout)
        main_layout.addLayout(window_layout)

        self.operation_groupbox.setLayout(main_layout)

    # 创建应用权限选项卡中的调试输出
    def create_console_layout(self):
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

        self.console_groupbox = console_groupbox

    # 创建应用权限选项卡布局
    def create_permission_layout(self):
        first_permission_label = QLabel("第一个应用:")
        self.first_text = QLineEdit()  # 第一个apk输入框
        self.first_text.setPlaceholderText("输入apk文件路径或拖拽文件至此")
        self.first_text.setAcceptDrops(True)  # 允许拖放
        self.first_text.dragEnterEvent = self.first_text_drag_enter
        self.first_text.dropEvent = self.first_text_drop
        compare_btn = QPushButton("权限对比")
        compare_btn.clicked.connect(self.click_compare_permission)
        first_permission_layout = QHBoxLayout()
        first_permission_layout.addWidget(first_permission_label)
        first_permission_layout.addWidget(self.first_text)
        first_permission_layout.addWidget(compare_btn)
        second_permission_label = QLabel("第二个应用:")
        self.second_text = QLineEdit()  # 第二个apk输入框
        self.second_text.setPlaceholderText("输入apk文件路径或拖拽文件至此")
        self.second_text.setAcceptDrops(True)  # 允许拖放
        self.second_text.dragEnterEvent = self.second_text_drag_enter
        self.second_text.dropEvent = self.second_text_drop
        clear_input_btn = QPushButton("清空")
        clear_input_btn.clicked.connect(self.click_clear_permission)
        self.first_output = QTextEdit()
        self.first_output.setAcceptDrops(False)
        self.second_output = QTextEdit()
        self.second_output.setAcceptDrops(False)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.first_output)
        output_layout.addWidget(self.second_output)
        self.permission_groupbox = QGroupBox()
        permission_layout = QVBoxLayout()
        second_permission_layout = QHBoxLayout()
        second_permission_layout.addWidget(second_permission_label)
        second_permission_layout.addWidget(self.second_text)
        second_permission_layout.addWidget(clear_input_btn)
        permission_layout.addLayout(first_permission_layout)
        permission_layout.addLayout(second_permission_layout)
        permission_layout.addLayout(output_layout)
        self.permission_groupbox.setLayout(permission_layout)

    # 创建模拟遥控选项卡界面
    def create_remote_layout(self):
        grid_layout = QGridLayout()

        up_btn = QPushButton("上")
        up_btn.setFixedSize(100, 35)
        up_btn.clicked.connect(self.click_up_btn)
        grid_layout.addWidget(up_btn, 0, 1)

        left_btn = QPushButton("左")
        left_btn.setFixedSize(100, 35)
        left_btn.clicked.connect(self.click_left_btn)
        grid_layout.addWidget(left_btn, 1, 0)

        ok_btn = QPushButton("确认")
        ok_btn.setFixedSize(100, 35)
        ok_btn.clicked.connect(self.click_ok_btn)
        grid_layout.addWidget(ok_btn, 1, 1)

        right_btn = QPushButton("右")
        right_btn.setFixedSize(100, 35)
        right_btn.clicked.connect(self.click_right_btn)
        grid_layout.addWidget(right_btn, 1, 2)

        down_btn = QPushButton("下")
        down_btn.setFixedSize(100, 35)
        down_btn.clicked.connect(self.click_down_btn)
        grid_layout.addWidget(down_btn, 2, 1)

        home_btn = QPushButton("Home")
        home_btn.setFixedSize(100, 35)
        home_btn.clicked.connect(self.click_home_btn)
        grid_layout.addWidget(home_btn, 3, 0)

        back_btn = QPushButton("返回")
        back_btn.setFixedSize(100, 35)
        back_btn.clicked.connect(self.click_back_btn)
        grid_layout.addWidget(back_btn, 3, 2)

        self.remote_groupbox = QGroupBox()
        self.remote_groupbox.setLayout(grid_layout)

    # 刷新设备列表
    def refresh_device_list(self):
        self.device_combox.clear()
        devices = self.get_device_list()
        self.device_combox.addItems(devices)

    # 获取连接的安卓手机设备
    def get_device_list(self):
        devices = []
        try:
            if self.harmmonyOS_btn.isChecked():
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
            if self.harmmonyOS_btn.isChecked():
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
        self.install_thread = InstallThread(apk_path, device)
        self.install_thread.finished.connect(self.handle_install_finished)
        self.install_thread.error.connect(self.handle_install_error)
        self.install_thread.start()

    def handle_install_finished(self, message):
        self.display_output(message)

    def handle_install_error(self, error):
        self.display_output(error)

    #  获取app下拉列表中的应用名
    def get_package_name(self):
        selected_option = self.app_option_combox.currentText()
        package_name = ""
        device = self.device_combox
        app_options = self.hdc_package_options if self.harmmonyOS_btn.isChecked() else self.adb_package_options
        if not device:
            self.display_output("请选择设备")
            return
        if not selected_option:
            self.display_output("请输入应用包名,或者从下拉列表中选择")
            return package_name
        for key, value in app_options.items():
            if value == selected_option:
                package_name = key
                break
        return package_name

    # 卸载应用
    def click_uninstall_btn(self):
        try:
            # 拼接adb -s 设备名 uninstall 包名命令
            if self.harmmonyOS_btn.isChecked():
                command = subprocess.run(["hdc", "uninstall", self.get_package_name()],
                                         capture_output=True, text=True, shell=True)
            else:
                command = subprocess.run(
                    ["adb", "-s", self.device_combox.currentText(), "uninstall", self.get_package_name()],
                    capture_output=True, text=True, shell=True)
            if command.returncode == 0:
                self.display_output(self.get_package_name() + "应用卸载成功")
            else:
                self.display_output("卸载失败，请检查输入框中的包名是否正确以及设备上是否存在该应用")
        except subprocess.CalledProcessError as e:
            self.display_output(f"卸载 {self.get_package_name()} 应用时出错：{e.output.decode('utf-8')}")

    # 清除应用缓存
    def click_clear_btn(self):
        try:
            if self.harmmonyOS_btn.isChecked():
                command = subprocess.run(
                    ["hdc", "shell", "bm", "clean", "-n", self.get_package_name(), "-d"],
                    capture_output=True, text=True, shell=True)
            else:
                command = subprocess.run(
                    ["adb", "-s", self.device_combox.currentText(), "shell", "pm", "clear", self.get_package_name()],
                    capture_output=True, text=True, shell=True)
            if command.returncode == 0:
                self.display_output(self.get_package_name() + "已清除数据")
            else:
                self.display_output("清除应用缓存失败，请检查输入框中的包名是否正确以及设备上是否存在该应用")
        except subprocess.CalledProcessError as e:
            self.display_output(f"清除 {self.get_package_name()} 缓存时出错：{e.stderr}")

    # 拖动物体进入QLineEdit区域时被调用
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 拖动物体释放到QLineEdit区域时被调用
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.install_text.setText(file_path)

    @staticmethod
    def first_text_drag_enter(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def first_text_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.first_text.setText(file_path)

    @staticmethod
    def second_text_drag_enter(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def second_text_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.second_text.setText(file_path)

    # 切换tab时，改变窗口大小
    def tab_changed(self, index):
        if index == 0:  # 切换到 Tab 应用操作
            self.resize(200, 400)
        elif index == 1:  # 切换到 Tab 应用权限
            self.resize(800, 500)
        elif index == 2:  # 切换到Tab 模拟遥控
            self.resize(200, 150)

    #  控制台输出
    def display_output(self, message):
        self.console.append(message)

    def clear_console_output(self):
        self.console.clear()

    # 当勾选鸿蒙设备时更新卸载应用下拉框的状态
    def click_harmmonyOS_update_btn(self, checked):
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
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()

    # 清空权限显示
    def click_clear_permission(self):
        self.first_text.clear()
        self.first_output.clear()
        self.second_text.clear()
        self.second_output.clear()

    @staticmethod
    def get_apk_permissions(apk_path):
        aapt_path = r"android-sdk\build-tools\aapt"  # aapt 路径
        command = f"{aapt_path} dump permissions {apk_path}"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        permissions = output.decode("utf-8").splitlines()
        return permissions

    # 点击权限对比
    def click_compare_permission(self):
        permissions1 = self.get_apk_permissions(self.first_text.text())
        permissions2 = self.get_apk_permissions(self.second_text.text())
        self.first_output.clear()
        self.second_output.clear()
        cursor = self.first_output.textCursor()
        cursor.insertText("第一个APK的权限：\n")
        for permission in permissions1:
            cursor.insertText(permission + "\n")
        cursor = self.second_output.textCursor()
        cursor.insertText("第二个APK的权限：\n")
        for permission in permissions2:
            cursor.insertText(permission + "\n")

        diff_permissions = list(set(permissions1) - set(permissions2))
        self.highlight_diff_permissions(diff_permissions)

    def highlight_diff_permissions(self, diff_permissions):
        cursor = self.first_output.textCursor()
        tc_format = QTextCharFormat()
        tc_format.setBackground(QColor("yellow"))
        cursor.beginEditBlock()  # 开始编辑块
        cursor.movePosition(QTextCursor.MoveOperation.Start)  # 将光标移动到文本开始位置
        while not cursor.atEnd():
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)  # 选择当前行
            line_text = cursor.selectedText()

            if any(permission in line_text for permission in diff_permissions):
                cursor.mergeCharFormat(tc_format)  # 合并字符格式，即应用高亮格式
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)  # 移动到下一行

        cursor.endEditBlock()  # 结束编辑块

    @staticmethod
    def click_up_btn():
        subprocess.run("adb shell input keyevent 19", creationflags=0x08000000)

    @staticmethod
    def click_left_btn():
        subprocess.run("adb shell input keyevent 21", creationflags=0x08000000)

    @staticmethod
    def click_ok_btn():
        subprocess.run("adb shell input keyevent 23", creationflags=0x08000000)

    @staticmethod
    def click_right_btn():
        subprocess.run("adb shell input keyevent 22", creationflags=0x08000000)

    @staticmethod
    def click_down_btn():
        subprocess.run("adb shell input keyevent 20", creationflags=0x08000000)

    @staticmethod
    def click_home_btn():
        subprocess.run("adb shell input keyevent 3", creationflags=0x08000000)

    @staticmethod
    def click_back_btn():
        subprocess.run("adb shell input keyevent 4", creationflags=0x08000000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdbWindow()
    window.show()
    sys.exit(app.exec())
