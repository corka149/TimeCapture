import sys
from qtpy.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QTimeEdit
from UiQt.mainwindow import Ui_MainWindow
from datedialog import DateDialog
from time_capture_service import TimeCaptureService
from datetime import time


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
        self.ui.pushButton_addRow.clicked.connect(self.add_row)
        self.ui.pushButton_save.clicked.connect(self.save_table)

    def __transform_table__(self):
        row = self.ui.table_times.rowCount()
        data = list()

        for i in range(row):
            row = dict()

            hr = self.ui.table_times.cellWidget(i, 0).time().hour()
            min = self.ui.table_times.cellWidget(i, 0).time().minute()
            row["start_time"] = time(hr, min)
            hr = self.ui.table_times.cellWidget(i, 1).time().hour()
            min = self.ui.table_times.cellWidget(i, 1).time().minute()
            row["end_time"] = time(hr, min)

            row["order"] = self.ui.table_times.item(i, 2).text()
            row["comment"] = self.ui.table_times.item(i, 3).text()
            data.append(row)

        return data

    def save_table(self):
        self.time_capture_service.updates_working_entries(self.__transform_table__())

    def add_new_day(self):
        self.datedialog.exec_()
        working_day = self.datedialog.get_working_date()
        list_len = self.ui.list_days.count()
        items = [self.ui.list_days.item(i).text() for i in range(list_len)]
        if not str(working_day) in items:
            self.ui.list_days.addItem(str(working_day))
            self.time_capture_service.add_new_working_day(working_day)

    def activate_details(self, item: QListWidgetItem):
        self.ui.tabWidget_Details.setEnabled(True)
        self.time_capture_service.selected_day = item.text()

    def add_row(self):
        row = self.ui.table_times.rowCount()
        self.ui.table_times.insertRow(row)
        self.ui.table_times.setCellWidget(row, 0, QTimeEdit(self.ui.table_times))
        self.ui.table_times.setCellWidget(row, 1, QTimeEdit(self.ui.table_times))
        self.ui.table_times.resizeRowsToContents()


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()

sys.exit(app.exec_())

