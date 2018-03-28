from qtpy import QtCore, QtGui


class Assets:

    @staticmethod
    def load_icon() -> QtGui.QIcon:
        app_icon = QtGui.QIcon()
        app_icon.addFile("assets/icons/16x16.jpeg", QtCore.QSize(16, 16))
        app_icon.addFile("assets/icons/24x24.jpeg", QtCore.QSize(24, 24))
        app_icon.addFile("assets/icons/32x32.jpeg", QtCore.QSize(32, 32))
        app_icon.addFile("assets/icons/48x48.jpeg", QtCore.QSize(48, 48))
        app_icon.addFile("assets/icons/64x64.jpeg", QtCore.QSize(64, 64))
        app_icon.addFile("assets/icons/128x128.png", QtCore.QSize(128, 128))
        return app_icon