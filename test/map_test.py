import os
import functools
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtWebChannel

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        # self.setFixedSize(800, 500)
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        label = self.label = QtWidgets.QLabel()
        sp = QtWidgets.QSizePolicy()
        sp.setVerticalStretch(0)
        label.setSizePolicy(sp)
        vbox.addWidget(label)
        view = self.view = QtWebEngineWidgets.QWebEngineView()
        #channel = self.channel = QtWebChannel.QWebChannel()

        #channel.registerObject("MainWindow", self)
        #view.page().setWebChannel(channel)

        file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "../src/main/assets/map.html",
        )
        #self.view.setUrl(QtCore.QUrl.fromLocalFile(file))
        view.load(QtCore.QUrl.fromUserInput("https://www.baidu.com"))

        vbox.addWidget(view)

        button = QtWidgets.QPushButton("Go to Paris")
        panToParis = functools.partial(self.panMap, 2.3272, 48.8620)
        button.clicked.connect(panToParis)
        vbox.addWidget(button)

    @QtCore.pyqtSlot(float, float)
    def onMapMove(self, lat, lng):
        self.label.setText("Lng: {:.5f}, Lat: {:.5f}".format(lng, lat))

    def panMap(self, lng, lat):
        page = self.view.page()
        page.runJavaScript("map.panTo(L.latLng({}, {}));".format(lat, lng))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())