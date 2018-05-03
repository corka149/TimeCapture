import sys
from qtpy.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QTimeEdit, QTableWidgetItem, QCheckBox, \
    QDoubleSpinBox, QTableWidget, QShortcut
from qtpy.QtGui import QKeySequence
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

days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

TAB_ENTRY = 0
TAB_BOOKING = 1


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_capture_service = TimeCaptureService()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Time Capture")

        self.datedialog = DateDialog(self)
        self.ui.tabWidget_Details.setEnabled(False)
        self.selected_tab = TAB_ENTRY

        self.__connect__()
        self.__setup__list__()
        self.__set_tool_tips__()

    def __setup__list__(self):
        """
        Load working days and sets tooltips for list items.

        :return:
        """
        for k in self.time_capture_service.working_dates:
            sum = 0
            for booking in self.time_capture_service.load_bookings(str(k)):
                sum += booking[bk.HOURS]

            qlwi = QListWidgetItem(str(k))
            qlwi.setToolTip("Day: {} | Sum: {} hrs".format(days[k.weekday()], sum))
            self.ui.list_days.addItem(qlwi)

    def __connect__(self):
        """
        Connects events to event handlers.

        :return:
        """
        self.ui.action_AddDay.triggered.connect(self.add_new_day)
        self.ui.action_Exit.triggered.connect(self.close)
        self.ui.list_days.itemClicked.connect(self.activated_details)
        self.ui.pushButton_addRow.clicked.connect(self.add_entry_row)
        self.ui.pushButton_save.clicked.connect(self.save_entity_table)
        self.ui.pushButton_addBookRow.clicked.connect(self.add_booking_row)
        self.ui.pushButton_saveBookRow.clicked.connect(self.save_booking_table)
        self.ui.pushButton_deleteEntityRow.clicked.connect(self.delete_entry_row)
        self.ui.pushButton_deleteBookingRow.clicked.connect(self.delete_booking_row)
        self.ui.pushButton_copyTime.clicked.connect(self.copy_entries_to_bookings)
        self.ui.pushButton_rowUp.clicked.connect(self.shift_up_entry_row)
        self.ui.pushButton_rowDown.clicked.connect(self.shift_down_entry_row)
        self.ui.pushButton_bookingRowUp.clicked.connect(self.shift_up_booking_row)
        self.ui.pushButton_bookingRowDown.clicked.connect(self.shift_down_booking_row)
        self.ui.tabWidget_Details.currentChanged.connect(self.__set_selected_tab__)
        QShortcut(QKeySequence("Alt+a"), self, self.hit_alt_a)
        QShortcut(QKeySequence("Alt+d"), self, self.hit_alt_d)
        QShortcut(QKeySequence("Alt+s"), self, self.hit_alt_s)

    def __set_tool_tips__(self):
        """
        Sets tool tips for shortcuts on buttons.

        :return:
        """
        self.ui.pushButton_addRow.setToolTip("Alt+a")
        self.ui.pushButton_save.setToolTip("Alt+s")
        self.ui.pushButton_deleteEntityRow.setToolTip("Alt+d")
        self.ui.pushButton_addBookRow.setToolTip("Alt+a")
        self.ui.pushButton_saveBookRow.setToolTip("Alt+s")
        self.ui.pushButton_deleteBookingRow.setToolTip("Alt+d")

    def __transform_entity_table__(self) -> list:
        """
        Gathers working entries and transform them into a list.

        :return list of rows:
        """
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
        """
        Gathers bookings and transform them into a list.

        :return list of bookings:
        """
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
        """
        Cleans entry table when switch working day.

        :param working_date:
        :return:
        """
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
        """
        Cleans booking table when switch working day.

        :param working_date:
        :return:
        """
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

    def __sum_booked_hours__(self):
        """
        Sums up the working entries to working hours of day.

        :return hour_sum:
        """
        hr_sum = 0.
        for i in range(self.ui.table_bookings.rowCount()):
            hr_sum += self.ui.table_bookings.cellWidget(i, B_HOURS).value()
        return hr_sum

    def __set_selected_tab__(self, i):
        self.selected_tab = i

    def save_entity_table(self):
        self.time_capture_service.update_working_entries(self.__transform_entity_table__())

    def save_booking_table(self):
        self.time_capture_service.update_bookings(self.__transform_booking_table__())
        self.__sum_booked_hours__()

    def add_new_day(self):
        self.datedialog.exec_()
        working_day = self.datedialog.get_working_date()
        list_len = self.ui.list_days.count()
        items = [self.ui.list_days.item(i).text() for i in range(list_len)]
        if not str(working_day) in items:
            self.ui.list_days.addItem(str(working_day))
            self.time_capture_service.add_new_working_day(working_day)

    def activated_details(self, item: QListWidgetItem):
        """
        Handles context switch when another working day was selected in the left list.

        :param item:
        :return:
        """
        self.ui.tabWidget_Details.setEnabled(True)
        self.time_capture_service.selected_day = item.text()
        self.__clean_and_load_entries__(item.text())
        self.__clean_and_load_bookings__(item.text())
        self.ui.label_sumHours.setText("Sum: {} hrs".format(self.__sum_booked_hours__()))

    def copy_entries_to_bookings(self):
        if self.time_capture_service.selected_day is not None:
            self.__clean_and_load_bookings__()
        self.ui.label_sumHours.setText("Sum: {} hrs".format(self.__sum_booked_hours__()))

    def add_entry_row(self):
        row = self.ui.table_times.rowCount()
        self.ui.table_times.insertRow(row)
        qte = QTimeEdit(self.ui.table_times)
        qte.setFocus()
        self.ui.table_times.setCellWidget(row, E_START_TIME_COL, qte)
        self.ui.table_times.setCellWidget(row, E_END_TIME_COL, QTimeEdit(self.ui.table_times))
        self.ui.table_times.resizeRowsToContents()

    def delete_entry_row(self):
        c_row = self.ui.table_times.currentRow()
        self.ui.table_times.removeRow(c_row)

    def shift_up_entry_row(self):
        c_row = self.ui.table_times.currentRow()
        new_row = c_row - 1
        if c_row > 0:
            switch_rows(self.ui.table_times, c_row, new_row)
            self.ui.table_times.setCurrentCell(new_row, self.ui.table_times.currentColumn())

    def shift_down_entry_row(self):
        c_row = self.ui.table_times.currentRow()
        new_row = c_row + 1
        if c_row < (self.ui.table_times.rowCount() - 1):
            switch_rows(self.ui.table_times, c_row, new_row)
            self.ui.table_times.setCurrentCell(new_row, self.ui.table_times.currentColumn())

    def add_booking_row(self):
        row = self.ui.table_bookings.rowCount()
        self.ui.table_bookings.insertRow(row)
        qcb = QCheckBox(self.ui.table_bookings)
        self.ui.table_bookings.setCellWidget(row, B_BOOKED, qcb)
        qcb = QCheckBox(self.ui.table_bookings)
        self.ui.table_bookings.setCellWidget(row, B_LOGGED, qcb)
        self.ui.table_bookings.setCellWidget(row, B_HOURS, QDoubleSpinBox(self.ui.table_bookings))
        self.ui.table_bookings.resizeRowsToContents()

    def delete_booking_row(self):
        c_row = self.ui.table_bookings.currentRow()
        self.ui.table_bookings.removeRow(c_row)

    def shift_up_booking_row(self):
        c_row = self.ui.table_bookings.currentRow()
        new_row = c_row - 1
        if c_row > 0:
            switch_rows(self.ui.table_bookings, c_row, new_row)
            self.ui.table_bookings.setCurrentCell(new_row, self.ui.table_bookings.currentColumn())

    def shift_down_booking_row(self):
        c_row = self.ui.table_bookings.currentRow()
        new_row = c_row + 1
        if c_row < (self.ui.table_bookings.rowCount() - 1):
            switch_rows(self.ui.table_bookings, c_row, new_row)
            self.ui.table_bookings.setCurrentCell(new_row, self.ui.table_bookings.currentColumn())

    def hit_alt_a(self):
        if self.ui.tabWidget_Details.isEnabled():
            if TAB_ENTRY == self.selected_tab:
                self.add_entry_row()
            elif TAB_BOOKING == self.selected_tab:
                self.add_booking_row()

    def hit_alt_s(self):
        if self.ui.tabWidget_Details.isEnabled():
            if TAB_ENTRY == self.selected_tab:
                self.save_entity_table()
            elif TAB_BOOKING == self.selected_tab:
                self.save_booking_table()

    def hit_alt_d(self):
        if self.ui.tabWidget_Details.isEnabled():
            if TAB_ENTRY == self.selected_tab:
                self.delete_entry_row()
            elif TAB_BOOKING == self.selected_tab:
                self.delete_booking_row()


def clean_table(table):
    """
    Helper function to clean up table.
    Works for every table.

    :param table:
    :return:
    """
    for i in reversed(range(table.rowCount())):
        table.removeRow(i)


def switch_rows(table: QTableWidget, old_position, new_position):
    """
    Helper function to switch a row in a table.
    Works for booking and entry table.

    :param table:
    :param old_position:
    :param new_position:
    :return:
    """
    for col_index in range(table.columnCount()):
        old_item = table.item(old_position, col_index)
        new_item = table.item(new_position, col_index)
        if old_item is not None and new_item is not None:
            old_text = old_item.text()
            new_text = new_item.text()
            table.setItem(old_position, col_index, QTableWidgetItem(new_text))
            table.setItem(new_position, col_index, QTableWidgetItem(old_text))
        else:
            old_cell_widget = table.cellWidget(old_position, col_index)
            new_cell_widget = table.cellWidget(new_position, col_index)
            if old_cell_widget is not None and new_cell_widget is not None:
                if isinstance(old_cell_widget, QTimeEdit) and isinstance(new_cell_widget, QTimeEdit):
                    qte = QTimeEdit(table)
                    qte.setTime(new_cell_widget.time())
                    table.setCellWidget(old_position, col_index, qte)
                    qte = QTimeEdit(table)
                    qte.setTime(old_cell_widget.time())
                    table.setCellWidget(new_position, col_index, qte)
                if isinstance(old_cell_widget, QDoubleSpinBox) and isinstance(new_cell_widget, QDoubleSpinBox):
                    qdsb = QDoubleSpinBox(table)
                    qdsb.setValue(new_cell_widget.value())
                    table.setCellWidget(old_position, col_index, qdsb)
                    qdsb = QDoubleSpinBox(table)
                    qdsb.setValue(old_cell_widget.value())
                    table.setCellWidget(new_position, col_index, qdsb)
                if isinstance(old_cell_widget, QCheckBox) and isinstance(new_cell_widget, QCheckBox):
                    qcb = QCheckBox(table)
                    qcb.setChecked(new_cell_widget.isChecked())
                    table.setCellWidget(old_position, col_index, qcb)
                    qcb = QCheckBox(table)
                    qcb.setChecked(old_cell_widget.isChecked())
                    table.setCellWidget(new_position, col_index, qcb)


def subtract_times(minuend: time, subtrahend: time) -> timedelta:
    return datetime.combine(date.today(), minuend) - datetime.combine(date.today(), subtrahend)


if "main" in __name__:
    app = QApplication(sys.argv)
    app.setWindowIcon(Assets.load_icon())
    window = MainWindow()
    tray_icon = Assets.load_tray_icon(window)
    window.showMaximized()

    sys.exit(app.exec_())
