from PyQt6.QtWidgets import QMainWindow,QApplication
import sys
from form import Ui_Form

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.ui = Ui_Form()
        self.ui.setupUi(self)


    def initUI(self):
        self.setGeometry(0,0,750,500)

app = QApplication(sys.argv)
window= Window()
window.show()
app.exec()