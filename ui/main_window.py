import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget, QApplication

from permission_tab import PermissionTab
from remote_tab import RemoteTab
from operations_tab import OperationsTab
from ui import TEST_TOOL_ICO_PATH


class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试小工具")
        self.setWindowIcon(QIcon(TEST_TOOL_ICO_PATH))
        self.app_operation_tab = OperationsTab()
        self.permission_tab = PermissionTab()
        self.remote_tab = RemoteTab()

        self.addTab(self.app_operation_tab, "应用操作")
        self.addTab(self.permission_tab, "应用权限")
        self.addTab(self.remote_tab, "模拟遥控")
        self.resize(400, 400)  # 初始化窗口大小 （宽，高）


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
