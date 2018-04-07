import sys
from qtpy.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QTimeEdit, QTableWidgetItem, QCheckBox, \
    QDoubleSpinBox, QTableWidget
from UiQt.mainwindow import Ui_MainWindow
from datedialog import DateDialog
from time_capture_service import TimeCaptureService
from datetime import time, date, datetime, timedelta
from bindings import WorkingEntryKey as wek, BookingKey as bk
from time_capture_assets import Assets
from errors import NoOrderProvidedError
from collections import defaultdict


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
        self.ui.pushButton_save.clicked.connect(self.save_entity_table)
        self.ui.pushButton_addBookRow.clicked.connect(self.add_booking_row)
        self.ui.pushButton_saveBookRow.clicked.connect(self.save_booking_table)
        self.ui.pushButton_deleteEntityRow.clicked.connect(self.delete_entry_row)
        self.ui.pushButton_deleteBookingRow.clicked.connect(self.delete_booking_row)
        self.ui.pushButton_copyTime.clicked.connect(self.copy_entries_to_bookings)

    def __transform_entity_table__(self) -> list:
        row = self.ui.table_times.rowCount()
        data = list()

        for i in range(row):
            row = dict()

            hr = self.ui.table_times.cellWidget(i, E_START_TIME_COL).time().hour()
            min = self.ui.table_times.cellWidget(i, E_START_TIME_COL).time().minute()
            row[wek.START_TIME] = time(hr, min)
            hr = self.ui.table_times.cellWidget(i, E_END_TIME_COL).time().hour()
            min = self.ui.table_times.cellWidget(i, E_END_TIME_COL).time().minute()
            row[wek.END_TIME] = time(hr, min)

            if self.ui.table_times.item(i, E_ORDER_COL) is not None:
                row[wek.ORDER] = self.ui.table_times.item(i, E_ORDER_COL).text()
            else:
                row[wek.ORDER] = ""
            if self.ui.table_times.item(i, E_COMMENT_COL) is not None:
                row[wek.COMMENT] = self.ui.table_times.item(i, E_COMMENT_COL).text()
            else:
                row[wek.COMMENT] = ""
            data.append(row)
        return data

    def __convert_entities_to_bookings__(self):
        """
        Converts the entities to a bookings and add them to the booking table.
        :return:
        """
        entities = self.__transform_entity_table__()
        bookings = list()
        d = defaultdict(float)
        for e in entities:
            d[e[wek.ORDER]] += subtract_times(e[wek.END_TIME], e[wek.START_TIME]).seconds / 60 / 60
        for order, hours in d.items():
            d = dict()
            d[bk.ORDER] = order
            d[bk.HOURS] = hours
            d[bk.BOOKED] = False
            d[bk.LOGGED] = False
            d[bk.COMMENT] = ""
            bookings.append(d)
        return bookings

    def __transform_booking_table__(self) -> list:
        row = self.ui.table_bookings.rowCount()
        data = list()

        for i in range(row):
            row = dict()
            table: QTableWidget = self.ui.table_bookings
            row[bk.BOOKED] = table.cellWidget(i, B_BOOKED).isChecked()
            row[bk.LOGGED] = table.cellWidget(i, B_LOGGED).isChecked()
            row[bk.HOURS] = table.cellWidget(i, B_HOURS).value()

            if table.item(i, B_ORDER) is not None:
                row[bk.ORDER] = table.item(i, B_ORDER).text()
            else:
                raise NoOrderProvidedError("An order is required!")
            if table.item(i, B_COMMENT) is not None:
                row[bk.COMMENT] = table.item(i, B_COMMENT).text()
            else:
                row[bk.COMMENT] = ""
            data.append(row)
        return data

    def __clean_and_load_entries__(self, working_date: str):
        row = 0
        entries = self.time_capture_service.load_working_entries(working_date)

        clean_table(self.ui.table_times)

        for e in entries:
            self.ui.table_times.insertRow(row)
            qte = QTimeEdit(self.ui.table_times)
            qte.setTime(e[wek.START_TIME])
            self.ui.table_times.setCellWidget(row, E_START_TIME_COL, qte)

            qte = QTimeEdit(self.ui.table_times)
            qte.setTime(e[wek.END_TIME])
            self.ui.table_times.setCellWidget(row, E_END_TIME_COL, qte)

            self.ui.table_times.setItem(row, E_ORDER_COL, QTableWidgetItem(e[wek.ORDER]))
            self.ui.table_times.setItem(row, E_COMMENT_COL, QTableWidgetItem(e[wek.COMMENT]))
            row += 1
            self.ui.table_times.resizeRowsToContents()

    def __clean_and_load_bookings__(self, working_date: str=None):
        row = 0
        t: QTableWidget = self.ui.table_bookings
        clean_table(t)
        bookings = list()
        if working_date is not None:
            bookings = self.time_capture_service.load_bookings(working_date)
        else:
            bookings = self.__convert_entities_to_bookings__()
        for b in bookings:
            t.insertRow(row)

            qcb = QCheckBox(self.ui.table_bookings)
            qcb.setChecked(b[bk.BOOKED])
            t.setCellWidget(row, B_BOOKED, qcb)

            qcb = QCheckBox(self.ui.table_bookings)
            qcb.setChecked(b[bk.LOGGED])
            t.setCellWidget(row, B_LOGGED, qcb)

            qdsb = QDoubleSpinBox(self.ui.table_bookings)
            qdsb.setValue(b[bk.HOURS])
            t.setCellWidget(row, B_HOURS, qdsb)

            t.setItem(row, B_ORDER, QTableWidgetItem(b[bk.ORDER]))
            t.setItem(row, B_COMMENT, QTableWidgetItem(b[bk.COMMENT]))
            t.resizeRowsToContents()
            row += 1

    def save_entity_table(self):
        self.time_capture_service.update_working_entries(self.__transform_entity_table__())

    def save_booking_table(self):
        self.time_capture_service.update_bookings(self.__transform_booking_table__())

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
        self.__clean_and_load_entries__(item.text())
        self.__clean_and_load_bookings__(item.text())

    def copy_entries_to_bookings(self):
        if self.time_capture_service.selected_day is not None:
            self.__clean_and_load_bookings__()

    def add_entry_row(self):
        row = self.ui.table_times.rowCount()
        self.ui.table_times.insertRow(row)
        self.ui.table_times.setCellWidget(row, E_START_TIME_COL, QTimeEdit(self.ui.table_times))
        self.ui.table_times.setCellWidget(row, E_END_TIME_COL, QTimeEdit(self.ui.table_times))
        self.ui.table_times.resizeRowsToContents()

    def delete_entry_row(self):
        c_row = self.ui.table_times.currentRow()
        self.ui.table_times.removeRow(c_row)

    def add_booking_row(self):
        row = self.ui.table_bookings.rowCount()
        self.ui.table_bookings.insertRow(row)
        qcb = QCheckBox(self.ui.table_bookings)
        self.ui.table_bookings.setCellWidget(row, B_BOOKED, qcb)
        qcb = QCheckBox(self.ui.table_bookings)
        self.ui.table_bookings.setCellWidget(row, B_LOGGED, qcb)
        self.ui.table_bookings.setCellWidget(row, B_HOURS, QDoubleSpinBox(self.ui.table_bookings))
        self.ui.table_times.resizeRowsToContents()

    def delete_booking_row(self):
        c_row = self.ui.table_bookings.currentRow()
        self.ui.table_bookings.removeRow(c_row)


def clean_table(table):
    for i in reversed(range(table.rowCount())):
        table.removeRow(i)


def subtract_times(minuend: time, subtrahend: time) -> timedelta:
    return datetime.combine(date.today(), minuend) - datetime.combine(date.today(), subtrahend)


app = QApplication(sys.argv)
app.setWindowIcon(Assets.load_icon())
window = MainWindow()
tray_icon = Assets.load_tray_icon(window)
window.showMaximized()

sys.exit(app.exec_())

