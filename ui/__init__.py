import os
# 获取当前文件的绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_TOOL_ICO_PATH = os.path.join(CURRENT_DIR, "..", "res", "test_tool.ico")
INSTALL_APKS_PATH = os.path.join(CURRENT_DIR, "..", "libs", "install_apks.jar")
AAPT_PATH = os.path.join(CURRENT_DIR, "..", "libs", "aapt.exe")

