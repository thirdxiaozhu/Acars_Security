from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import os
import sys


class Window(QMainWindow):
    def __init__(self, parent=None):

        a = [1,2,3,4,5,6,7,8]
        print(a[2:4])


        super(Window, self).__init__(parent)
        self.qwebengine = QWebEngineView()
        url = os.getcwd() + os.path.sep + "src/main/assets/map.html"    # 要绝对路径，不然无法加载
        print(url)
        self.qwebengine.load(QUrl.fromLocalFile(url))
        #self.qwebengine.load(QUrl('https://www.baidu.com'))
        self.setCentralWidget(self.qwebengine)

# 创建应用
app = QApplication(sys.argv + ["--no-sandbox"])
# 创建主窗口
window = Window()
# 显示窗口
window.show()
# 运行应用，并监听事件
app.exec_()
