import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget, QApplication, QMainWindow

from ui.permission_tab import PermissionTab
from ui.remote_tab import RemoteTab
from ui.operations_tab import OperationsTab
from ui import TEST_TOOL_ICO_PATH
from ui.other_functions_tab import OtherFunctionsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试小工具")
        self.setWindowIcon(QIcon(TEST_TOOL_ICO_PATH))
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.operation_tab = OperationsTab()
        self.permission_tab = PermissionTab()
        self.remote_tab = RemoteTab()
        self.other_functions_tab = OtherFunctionsTab()

        self.tabs.addTab(self.operation_tab, "应用操作")
        self.tabs.addTab(self.permission_tab, "应用权限")
        self.tabs.addTab(self.remote_tab, "模拟遥控")
        self.tabs.addTab(self.other_functions_tab, "其他")
        self.resize(410, 470)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
