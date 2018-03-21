import sys
from qtpy.QtWidgets import QMainWindow, QApplication, QListWidgetItem
from UiQt.mainwindow import Ui_MainWindow
from datedialog import DateDialog
from time_capture_service import TimeCaptureService


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_capture_service = TimeCaptureService()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Time Capture")

        self.datedialog = DateDialog(self)
        self.ui.tabWidget_Details.setEnabled(False)

        self.__connect__()
        self.__setup__list__()

    def __setup__list__(self):
        for k in self.time_capture_service.working_dates:
            self.ui.list_days.addItem(str(k))

    def __connect__(self):
        self.ui.action_AddDay.triggered.connect(self.add_new_day)
        self.ui.action_Exit.triggered.connect(self.close)
        self.ui.list_days.itemClicked.connect(self.activate_details)

    def add_new_day(self):
        self.datedialog.exec_()
        working_day = self.datedialog.get_working_date()
        list_len = self.ui.list_days.count()
        items = [self.ui.list_days.item(i).text() for i in range(list_len)]
        if not str(working_day) in items:
            self.ui.list_days.addItem(str(working_day))

    def activate_details(self, item: QListWidgetItem):
        self.ui.tabWidget_Details.setEnabled(True)
        self.time_capture_service.selected_day = item.text()


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()

sys.exit(app.exec_())

