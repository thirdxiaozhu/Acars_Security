import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import Ui_EntryUI

def main():
    print(QStyleFactory.keys())
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_EntryUI.Ui_MainWindow()
    ui.setupUi(mainWindow)
    #event = Event(mainWindow)
    QApplication.setStyle("Breeze")
    mainWindow.show()
    app.exec_()
    #event.closeWindow()

if __name__ == "__main__":
    main()