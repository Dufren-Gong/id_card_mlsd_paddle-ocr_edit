from PyQt6.QtWidgets import QMainWindow, QWidget
from uis.shapes import Ui_Shapes
from uis.show_info_window_ui import Row_One
from PyQt6.QtGui import QIcon
from my_utils.utils import get_internal_path
from PyQt6.QtCore import Qt

class Show_Info_Window(QMainWindow):
    def __init__(self, height_num = 5, width = [200, 35]):
        super().__init__()
        self.reopen_main_window = None
        self.shape = Ui_Shapes(round_gap=10)
        self.shape.layout([self.shape.label_height*height_num],
                          [width])
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        self.init_ui()
        self.init_events()
         # 设置窗口为置顶
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def closeEvent(self, event):
        if self.reopen_main_window != None:
            self.reopen_main_window()
            self.reopen_main_window = None
        self.row_one.exit_button.disconnect()
        self.init_events()
        self.hide()

    def init_reopen_main(self, reopen):
        self.reopen_main_window = reopen

    def set_show_text(self, show_text):
        self.hide()
        self.row_one.tip_label.setPlainText(show_text)

    def exit_application(self):
        try:
            self.hide()
        except:
            pass

    def show_window(self):
        try:
            self.show()
        except:
            pass

    def init_ui(self):
        self.setWindowTitle("提示")
        self.setGeometry(self.shape.start_width, self.shape.start_height, self.shape.width, self.shape.height)
        self.setFixedSize(self.shape.width, self.shape.height)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.row_one = Row_One(
            central_widget,
            self.shape.shape_tuples[0][0],
            self.shape.shape_tuples[0][1],
        )

    def init_events(self):
        self.row_one.exit_button.clicked.connect(self.exit_application)