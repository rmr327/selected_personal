import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel
from PyQt5 import QtCore, QtGui


class App(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self, flags=QtCore.Qt.WindowStaysOnTopHint)
        self.title = 'IoT App'
        self.left = 100
        self.top = 100
        self.width = 950
        self.height = 190
        self.button = QPushButton('START', self)
        self.btn_press_cnt = 0
        self.textbox = QLineEdit(self)
        self.textbox_1 = QLineEdit(self)
        self.textbox_2 = QLineEdit(self)
        self.textbox_3 = QLineEdit(self)
        self.textbox_4 = QLineEdit(self)
        self.ae_name = None
        self.dic_name = None
        self.ir_name = None
        self.coll_name = None
        self.doc_name = None
        self.init_ui()

    def init_ui(self):
        # Add window icon and title
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon('drexel.png'))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("background-color: rgb(255,215,0);")

        # Add background
        # background = QtGui.QImage("logo.png")
        # background = background.scaled(QtCore.QSize(950, 190))
        # palette = QtGui.QPalette()
        # palette.setBrush(self.backgroundRole(), QtGui.QBrush(background))
        # self.setPalette(palette)

        # Add text
        label = QLabel(self)
        label.setText('  AE file name')
        label.resize(110, 40)
        label.move(10, 10)
        label.setStyleSheet("background-color: rgb(25,25,112); color: yellow; font: bold 14px; ")

        label_1 = QLabel(self)
        label_1.setText('  IR file name')
        label_1.resize(110, 40)
        label_1.move(11, 70)
        label_1.setStyleSheet("background-color: rgb(25,25,112); color: yellow; font: bold 14px;")

        label_2 = QLabel(self)
        label_2.setText('  DIC file name')
        label_2.resize(110, 40)
        label_2.move(10, 130)
        label_2.setStyleSheet("background-color: rgb(25,25,112); color: yellow; font: bold 14px;")

        label_3 = QLabel(self)
        label_3.setText(' Collection name')
        label_3.resize(120, 40)
        label_3.move(500, 10)
        label_3.setStyleSheet("background-color: rgb(25,25,112); color: yellow; font: bold 14px;")

        label_4 = QLabel(self)
        label_4.setText(' Document name')
        label_4.resize(120, 40)
        label_4.move(500, 70)
        label_4.setStyleSheet("background-color: rgb(25,25,112); color: yellow; font: bold 14px;")

        # Create textbox
        self.textbox.resize(280, 40)
        self.textbox.move(120, 10)

        self.textbox_1.resize(280, 40)
        self.textbox_1.move(120, 70)

        self.textbox_2.resize(280, 40)
        self.textbox_2.move(120, 130)

        self.textbox_3.resize(280, 40)
        self.textbox_3.move(620, 10)

        self.textbox_4.resize(280, 40)
        self.textbox_4.move(620, 70)

        # Create a button in the window
        self.button.resize(410, 40)
        self.button.move(500, 130)
        self.button.setStyleSheet("background-color: rgb(25,25,112); color: green; font: bold 22px;"
                                  "border: 3px solid green")

        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    def on_click(self):
        if self.btn_press_cnt == 0:
            self.button.setText('STOP')
            self.button.setStyleSheet("background-color: rgb(25,25,112); color: red; font: bold 22px;"
                                      "border: 3px solid red")

            self.ae_name = self.textbox.text()
            self.ir_name = self.textbox_1.text()
            self.dic_name = self.textbox_2.text()
            self.coll_name = self.textbox_3.text()
            self.doc_name = self.textbox_4.text()

            print(self.ae_name, self.ir_name, self.dic_name, self.coll_name, self.doc_name)

            self.btn_press_cnt = 1
        else:
            self.button.setText('START')
            self.button.setStyleSheet("background-color: rgb(25,25,112); color: green; font: bold 22px;"
                                      "border: 3px solid green")
            self.btn_press_cnt = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
