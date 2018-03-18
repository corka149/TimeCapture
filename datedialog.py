from qtpy.QtWidgets import QDialog
from UiQt.datedialog import Ui_Dialog


class DateDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialog = Ui_Dialog()
        self.dialog.setupUi(self)
