from qtpy import QtCore, QtWidgets, QtGui


class Assets:

    @staticmethod
    def load_icon() -> QtGui.QIcon:
        """
        Loads the time capture icons.

        :return app_icon
        """
        app_icon = QtGui.QIcon()
        app_icon.addFile("assets/icons/16x16.jpeg", QtCore.QSize(16, 16))
        app_icon.addFile("assets/icons/24x24.jpeg", QtCore.QSize(24, 24))
        app_icon.addFile("assets/icons/32x32.jpeg", QtCore.QSize(32, 32))
        app_icon.addFile("assets/icons/48x48.jpeg", QtCore.QSize(48, 48))
        app_icon.addFile("assets/icons/64x64.jpeg", QtCore.QSize(64, 64))
        app_icon.addFile("assets/icons/128x128.png", QtCore.QSize(128, 128))
        return app_icon

    @staticmethod
    def load_tray_icon(parent=None) -> QtWidgets.QSystemTrayIcon:
        """
        Load the system tray icon of time capture.

        :param parent:
        :return tray_icon:
        """
        tray_icon = QtWidgets.QSystemTrayIcon(Assets.load_icon(), parent)
        return tray_icon
