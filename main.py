import sys
from qtpy import QtWidgets
from UiQt.mainwindow import Ui_MainWindow
from datetime import date


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Time Capture")

        self.ui.action_AddDay.triggered.connect(self.add_new_day)

    def add_new_day(self):
        now = date.today()
        list_len = self.ui.list_days.count()
        items = [self.ui.list_days.item(i).text() for i in range(list_len)]
        if not str(now) in items:
            self.ui.list_days.addItem(str(now))


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.showMaximized()

sys.exit(app.exec_())
