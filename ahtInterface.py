# This Python file uses the following encoding: utf-8
import sys
import os


from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PySide2.QtCore import QFile, QTimer
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader

from qtgui_helpers import *
from logger import *

class AhtApp(QApplication):
    def __init__(self):
        super(AhtApp, self).__init__()

class AhtInterface(QWidget):
    def __init__(self, logger):
        super(AhtInterface, self).__init__()
        self.load_ui()
        self.logger = logger

        self.setWindowTitle("Arrowhead Tool - Gateway")
        self.setWindowIcon(QIcon('arrowheadtools.png'))

        self.move(10,10)


    def update(self):
        try:
            el = self.logger.GetElementToShow()
            if el is not None:
                if el.get('type','log')=='log':
                    print(el.get('text', None))
                    self.ui.txtLog.appendHtml (el.get('text', None))
                if el.get('type', 'log') == 'image':
                    filename = el.get('text', None)
                    print(filename)
                    show_image_from_file(filename,self.ui.lblImage)

        except:
            pass
        self.timer.start()

    def load_ui(self):




        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        filecss = open("stylesheet.css", "r")
        self.css = filecss.read()
        self.setStyleSheet(self.css)


        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.timer.setSingleShot(False)
        self.timer.setInterval(1000)
        self.timer.start()



        #self.setWindowState(Qt.WindowMaximized)



if __name__ == "__main__":
    app = QApplication([])
    widget = AhtInterface()
    widget.show()
    sys.exit(app.exec_())
