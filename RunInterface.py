import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import Ui_MainInterface
import Interface

def main():
    #print(QStyleFactory.keys())
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainInterface.Ui_MainWindow()
    ui.setupUi(mainWindow)
    interface = Interface.Interface(mainWindow)
    QApplication.setStyle("Oxygen")
    mainWindow.show()
    app.exec_()
    interface.closeWindow()

if __name__ == "__main__":
    main()