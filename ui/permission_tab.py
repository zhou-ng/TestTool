import subprocess

from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QHBoxLayout, QPushButton, QTextEdit, \
    QSizePolicy, QSpacerItem, QGridLayout

from ui import AAPT_PATH


class PermissionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.show_permission_widget = False
        h_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        v_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.input_package_le = QLineEdit()  # 查看应用权限下的输入框
        self.input_package_le.setAcceptDrops(True)
        self.input_package_le.dragEnterEvent = self.input_drag_enter
        self.input_package_le.dropEvent = self.input_package_drop
        self.input_package_le.setToolTip("输入apk文件路径或拖拽文件至此")
        view_btn = QPushButton("查看")
        first_hl = QHBoxLayout()
        first_hl.addWidget(self.input_package_le)
        first_hl.addWidget(view_btn)
        show_permission_vl = QVBoxLayout()
        show_permission_vl.addLayout(first_hl)
        self.show_permission_gb = QGroupBox("查看应用权限")
        self.show_permission_gb.setLayout(show_permission_vl)

        self.compare_permission_gb = QGroupBox("权限对比")
        compare_permission_gl = QGridLayout()
        first_package_label = QLabel("第一个应用 :")
        self.input_first_package_le = QLineEdit()  # 第一个安装包输入框
        self.input_first_package_le.setAcceptDrops(True)  # 允许拖放
        self.input_first_package_le.dragEnterEvent = self.input_drag_enter
        self.input_first_package_le.dropEvent = self.input_first_drop
        second_package_label = QLabel("第二个应用 :")
        self.input_second_package_le = QLineEdit()  # 第二个安装包输入框
        self.input_second_package_le.setAcceptDrops(True)  # 允许拖放
        self.input_second_package_le.dragEnterEvent = self.input_drag_enter
        self.input_second_package_le.dropEvent = self.input_second_drop

        compare_permission_btn = QPushButton("确定")
        qh = QHBoxLayout()
        qh.addItem(h_spacer)
        qh.addWidget(compare_permission_btn)

        self.first_package_output = QTextEdit()
        self.first_package_output.setVisible(False)
        self.first_package_output.setAcceptDrops(False)
        self.second_package_output = QTextEdit()
        self.second_package_output.setVisible(False)
        self.second_package_output.setAcceptDrops(False)
        output_qh = QHBoxLayout()
        output_qh.addWidget(self.first_package_output)
        output_qh.addWidget(self.second_package_output)

        compare_permission_gl.addWidget(first_package_label, 0, 0)
        compare_permission_gl.addWidget(self.input_first_package_le, 0, 1)
        compare_permission_gl.addWidget(second_package_label, 1, 0)
        compare_permission_gl.addWidget(self.input_second_package_le, 1, 1)
        compare_permission_gl.addLayout(qh, 2, 0, 1, 2)
        self.compare_permission_gb.setLayout(compare_permission_gl)

        self.pack_up_btn = QPushButton("收起")
        self.pack_up_btn.setVisible(False)

        app_permission_vl = QVBoxLayout()
        app_permission_vl.addWidget(self.show_permission_gb)  # 查看权限
        app_permission_vl.addWidget(self.compare_permission_gb)
        app_permission_vl.addLayout(output_qh, stretch=1)
        app_permission_vl.addItem(v_spacer)
        app_permission_vl.addWidget(self.pack_up_btn)
        self.setLayout(app_permission_vl)

        # 按钮点击事件
        view_btn.clicked.connect(self.click_view_btn)
        compare_permission_btn.clicked.connect(self.click_compare_permission_btn)
        self.pack_up_btn.clicked.connect(self.click_pack_up)

    @staticmethod
    def input_drag_enter(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def input_package_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.input_package_le.setText(file_path)

    # 点击查看
    def click_view_btn(self):
        self.compare_permission_gb.setVisible(False)
        self.pack_up_btn.setVisible(True)
        self.show_permission_widget = False
        self.first_package_output.setVisible(True)
        self.first_package_output.clear()
        cursor = self.first_package_output.textCursor()
        cursor.insertText("当前包声明的应用权限 :\n")

        package_path = self.input_package_le.text()
        permissions = self.get_apk_permissions(package_path)
        for permission in permissions:
            cursor.insertText(permission + "\n")
        self.first_package_output.moveCursor(QTextCursor.MoveOperation.Start)

    def input_first_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.input_first_package_le.setText(file_path)

    def input_second_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.input_second_package_le.setText(file_path)

    # 点击权限对比中的确定
    def click_compare_permission_btn(self):
        self.first_package_output.setVisible(True)
        self.second_package_output.setVisible(True)
        self.pack_up_btn.setVisible(True)
        self.show_permission_gb.setVisible(False)
        self.show_permission_widget = True

        permissions1 = self.get_apk_permissions(self.input_first_package_le.text())
        permissions2 = self.get_apk_permissions(self.input_second_package_le.text())
        self.first_package_output.clear()
        self.second_package_output.clear()
        cursor = self.first_package_output.textCursor()
        cursor.insertText("第一个APK的权限 ：\n")
        for permission in permissions1:
            cursor.insertText(permission + "\n")
        cursor = self.second_package_output.textCursor()
        cursor.insertText("第二个APK的权限 ：\n")
        for permission in permissions2:
            cursor.insertText(permission + "\n")

        diff_permissions = list(set(permissions1) - set(permissions2))
        self.highlight_diff_permissions(diff_permissions)

    # 点击"收起"
    def click_pack_up(self):
        self.pack_up_btn.setVisible(False)
        if self.show_permission_widget:
            self.first_package_output.setVisible(False)
            self.second_package_output.setVisible(False)
            self.show_permission_gb.setVisible(True)
        else:
            self.compare_permission_gb.setVisible(True)
            self.first_package_output.setVisible(False)

    def highlight_diff_permissions(self, diff_permissions):
        cursor = self.first_package_output.textCursor()
        cursor.beginEditBlock()  # 开始编辑块
        cursor.movePosition(QTextCursor.MoveOperation.Start)  # 将光标移动到文本开始位置
        while not cursor.atEnd():
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)  # 选择当前行
            line_text = cursor.selectedText()
            tc_format = QTextCharFormat()
            tc_format.setBackground(QColor("yellow"))
            if any(permission in line_text for permission in diff_permissions):
                cursor.mergeCharFormat(tc_format)  # 合并字符格式，即应用高亮格式
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)  # 移动到下一行
        cursor.endEditBlock()  # 结束编辑块

    @staticmethod
    def get_apk_permissions(apk_path):
        command = f"{AAPT_PATH} dump permissions {apk_path}"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        permissions = output.decode("utf-8").splitlines()
        return permissions
