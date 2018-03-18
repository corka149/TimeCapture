import sys
from qtpy.QtWidgets import QMainWindow, QApplication
from UiQt.mainwindow import Ui_MainWindow
from datedialog import DateDialog
from datetime import date


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Time Capture")

        self.datedialog = DateDialog()
        
        self.ui.action_AddDay.triggered.connect(self.add_new_day)
        self.ui.action_Exit.triggered.connect(self.close)

    def add_new_day(self):
        self.datedialog.exec_()
        # now = date.today()
        # list_len = self.ui.list_days.count()
        # items = [self.ui.list_days.item(i).text() for i in range(list_len)]
        # if not str(now) in items:
        #     self.ui.list_days.addItem(str(now))


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()

sys.exit(app.exec_())

