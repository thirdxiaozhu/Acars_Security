from PyQt5 import QtWidgets


class TestTransDialog(QtWidgets.QDialog):
    def closeEvent(self, event):
        pass
        self.entity.forceStopDevices()
