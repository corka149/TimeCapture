import sys
from qtpy.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QTimeEdit, QTableWidgetItem, QCheckBox
from UiQt.mainwindow import Ui_MainWindow
from datedialog import DateDialog
from time_capture_service import TimeCaptureService
from datetime import time
from bindings import WorkingEntryKey
from time_capture_assets import Assets


# Working entry
E_START_TIME_COL = 0
E_END_TIME_COL = 1
E_ORDER_COL = 2
E_COMMENT_COL = 3

# Booking
B_ORDER = 0
B_HOURS = 1
B_BOOKED = 2
B_LOGGED = 3
B_COMMENT = 4


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
        self.ui.pushButton_addRow.clicked.connect(self.add_entry_row)
        self.ui.pushButton_save.clicked.connect(self.save_table)
        self.ui.pushButton_addBookRow.clicked.connect(self.add_booking_row)

    def __transform_table__(self):
        row = self.ui.table_times.rowCount()
        data = list()

        for i in range(row):
            row = dict()

            hr = self.ui.table_times.cellWidget(i, E_START_TIME_COL).time().hour()
            min = self.ui.table_times.cellWidget(i, E_START_TIME_COL).time().minute()
            row[WorkingEntryKey.START_TIME] = time(hr, min)
            hr = self.ui.table_times.cellWidget(i, E_END_TIME_COL).time().hour()
            min = self.ui.table_times.cellWidget(i, E_END_TIME_COL).time().minute()
            row[WorkingEntryKey.END_TIME] = time(hr, min)

            if self.ui.table_times.item(i, E_ORDER_COL) is not None:
                row[WorkingEntryKey.ORDER] = self.ui.table_times.item(i, E_ORDER_COL).text()
            else:
                row[WorkingEntryKey.ORDER] = ""
            if self.ui.table_times.item(i, E_COMMENT_COL) is not None:
                row[WorkingEntryKey.COMMENT] = self.ui.table_times.item(i, E_COMMENT_COL).text()
            else:
                row[WorkingEntryKey.COMMENT] = ""
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
        row = 0
        self.ui.tabWidget_Details.setEnabled(True)
        self.time_capture_service.selected_day = item.text()
        entries = self.time_capture_service.load_working_entries(item.text())

        for i in reversed(range(self.ui.table_times.rowCount())):
            self.ui.table_times.removeRow(i)

        if entries is not None:
            for e in entries:
                self.ui.table_times.insertRow(row)
                qte = QTimeEdit(self.ui.table_times)
                qte.setTime(e[WorkingEntryKey.START_TIME])
                self.ui.table_times.setCellWidget(row, E_START_TIME_COL, qte)

                qte = QTimeEdit(self.ui.table_times)
                qte.setTime(e[WorkingEntryKey.END_TIME])
                self.ui.table_times.setCellWidget(row, E_END_TIME_COL, qte)

                self.ui.table_times.setItem(row, E_ORDER_COL, QTableWidgetItem(e[WorkingEntryKey.ORDER]))
                self.ui.table_times.setItem(row, E_COMMENT_COL, QTableWidgetItem(e[WorkingEntryKey.COMMENT]))
                row += 1
            self.ui.table_times.resizeRowsToContents()

    def add_entry_row(self):
        row = self.ui.table_times.rowCount()
        self.ui.table_times.insertRow(row)
        self.ui.table_times.setCellWidget(row, E_START_TIME_COL, QTimeEdit(self.ui.table_times))
        self.ui.table_times.setCellWidget(row, E_END_TIME_COL, QTimeEdit(self.ui.table_times))
        self.ui.table_times.resizeRowsToContents()

    def add_booking_row(self):
        row = self.ui.table_bookings.rowCount()
        self.ui.table_bookings.insertRow(row)
        self.ui.table_bookings.setCellWidget(row, B_BOOKED, QCheckBox(self.ui.table_bookings))
        self.ui.table_bookings.setCellWidget(row, B_LOGGED, QCheckBox(self.ui.table_bookings))
        self.ui.table_times.resizeRowsToContents()


app = QApplication(sys.argv)
app.setWindowIcon(Assets.load_icon())
window = MainWindow()
tray_icon = Assets.load_tray_icon(window)
window.showMaximized()

sys.exit(app.exec_())

