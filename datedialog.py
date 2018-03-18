from qtpy.QtWidgets import QDialog
from qtpy.QtCore import Qt
from UiQt.datedialog import Ui_Dialog
from datetime import date


class DateDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__dialog = Ui_Dialog()
        self.__dialog.setupUi(self)
        self.__set_date_now()

    def __set_date_now(self):
        now = date.today()
        d = self.__dialog.dateEdit_WorkingDate.date()
        d.setDate(now.year, now.month, now.day)
        self.__dialog.dateEdit_WorkingDate.setDate(d)

    def __set_modal(self):
        self.setWindowModality(Qt.WindowModal)
        self.setModal(True)

    def get_working_date(self) -> date:
        d = self.__dialog.dateEdit_WorkingDate.date()
        return date(d.year(), d.month(), d.day())
