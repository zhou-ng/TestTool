import subprocess

from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QHBoxLayout, QPushButton, QTextEdit, \
    QSizePolicy, QSpacerItem, QGridLayout

from ui import AAPT_PATH


class PermissionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.is_show_widget = False
        self.compare_permission_gb = QGroupBox("权限对比")
        compare_permission_gl = QGridLayout()
        first_package_label = QLabel("第一个应用 :")
        second_package_label = QLabel("第二个应用 :")
        self.input_first_package_le = QLineEdit()  # 第一个安装包输入框
        self.input_first_package_le.setAcceptDrops(True)  # 允许拖放
        self.input_first_package_le.dragEnterEvent = self.input_first_drag_enter
        self.input_first_package_le.dropEvent = self.input_first_drop
        self.input_second_package_le = QLineEdit()  # 第二个安装包输入框
        self.input_second_package_le.setAcceptDrops(True)  # 允许拖放
        self.input_second_package_le.dragEnterEvent = self.input_second_drag_enter
        self.input_second_package_le.dropEvent = self.input_second_drop
        confirm_compare_permission_pb = QPushButton("确定")
        confirm_compare_permission_pb.clicked.connect(self.click_confirm_compare_permission)
        h_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        qh = QHBoxLayout()
        qh.addItem(h_spacer)
        qh.addWidget(confirm_compare_permission_pb)
        compare_permission_gl.addWidget(first_package_label, 0, 0)
        compare_permission_gl.addWidget(self.input_first_package_le, 0, 1)
        compare_permission_gl.addWidget(second_package_label, 1, 0)
        compare_permission_gl.addWidget(self.input_second_package_le, 1, 1)
        compare_permission_gl.addLayout(qh, 2, 0, 1, 2)
        self.compare_permission_gb.setLayout(compare_permission_gl)

        self.first_package_output = QTextEdit()
        self.first_package_output.hide()
        self.first_package_output.setAcceptDrops(False)
        self.second_package_output = QTextEdit()
        self.second_package_output.hide()
        self.second_package_output.setAcceptDrops(False)
        compare_permission_output = QHBoxLayout()
        compare_permission_output.addWidget(self.first_package_output)
        compare_permission_output.addWidget(self.second_package_output)

        self.danger_permission_output = QTextEdit()  # 危险权限输出弹窗
        self.danger_permission_output.hide()
        v_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.pack_up_btn = QPushButton("收起")
        self.pack_up_btn.clicked.connect(self.click_pack_up)
        self.pack_up_btn.hide()
        self.app_permission_groupbox = QGroupBox()
        app_permission_vl = QVBoxLayout()
        app_permission_vl.addWidget(self.compare_permission_gb)
        app_permission_vl.addLayout(compare_permission_output)
        app_permission_vl.addItem(v_spacer)
        app_permission_vl.addWidget(self.pack_up_btn)
        self.app_permission_groupbox.setLayout(app_permission_vl)
        self.setLayout(app_permission_vl)

    @staticmethod
    def input_first_drag_enter(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def input_first_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.input_first_package_le.setText(file_path)

    @staticmethod
    def input_second_drag_enter(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def input_second_drop(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.input_second_package_le.setText(file_path)

    # 点击权限对比中的确定
    def click_confirm_compare_permission(self):
        self.first_package_output.show()
        self.second_package_output.show()
        self.pack_up_btn.show()
        self.is_show_widget = True

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
        self.pack_up_btn.hide()
        if self.is_show_widget:
            self.first_package_output.hide()
            self.second_package_output.hide()
        else:
            self.danger_permission_output.hide()
            self.compare_permission_gb.show()

    def highlight_diff_permissions(self, diff_permissions):
        cursor = self.first_package_output.textCursor()
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
    def get_apk_permissions(apk_path):
        command = f"{AAPT_PATH} dump permissions {apk_path}"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        permissions = output.decode("utf-8").splitlines()
        return permissions
