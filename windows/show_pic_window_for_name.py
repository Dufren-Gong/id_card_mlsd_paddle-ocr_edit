from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication
from uis.function_and_info_ui import Row_Zero, Row_One, Row_Two, Row_Three, Row_Four, Row_Five, Row_Six, Row_Seven, Row_Eight, Row_Nine
from PyQt6.QtGui import QPainter
from uis.shapes import Ui_Shapes
from windows.show_info_window import Show_Info_Window
import copy

class Show_Pic_Window(QMainWindow):
    def __init__(self, show_info: Show_Info_Window, global_config, init_edge_color, height_gap):
        super().__init__()
        self.height_gap = height_gap
        self.screen_size = QApplication.primaryScreen().size()
        self.max_size = (self.screen_size.width()*0.8, self.screen_size.height()*0.8)
        self.show_info_window = show_info
        self.global_config = global_config
        self.map_color = copy.deepcopy(self.global_config['mlsd_conf']['map_color'])
        self.map_color[3] = int(255 * self.map_color[3])
        self.points = []
        self.scale = 1
        self.middle_points = []
        self.dragging_point = None
        self.dragging_middle = None
        self.selected_point = None
        self.selected_middle_point = None
        self.pixmap = None
        self.show_pic_shape = Ui_Shapes(round_gap=5)
        self.show_pic_shape.layout([50], [[80]])

        self.init_edge_color = init_edge_color
        self.shape = Ui_Shapes(start_width=870, start_height=50, round_gap=10)
        self.shape.layout([self.shape.label_height] * 4 + [self.shape.label_height * 3] + [self.shape.label_height] + [self.shape.label_height * 7] +[self.shape.label_height] * 3,
                            [[30, 94] + [20] * 4] * 2 + [[30, 25, 28, 63] + [20] * 3] + [[30, 124, 80]] + [[30, 210]] * 3 + [[80] * 3] * 3)
        self.init_ui()

    def clear_content(self):
        # 清空相关属性
        self.pixmap = None  # 确保不再绘制当前图像
        self.update()  # 刷新界面

    def clear_content_point_and_line(self):
        # 清空所有与绘图相关的属性
        self.update()  # 刷新界面

    def change_size(self, shape=(500, 800)):
        self.show_pic_shape.layout([shape[0]],
                                   [[shape[1]]])
        self.setFixedSize(self.show_pic_shape.round_gap * 2 + shape[1] + self.shape.round_gap + self.shape.width, self.show_pic_shape.round_gap * 2 + shape[0])

    def init_ui(self):
        self.setGeometry(self.show_pic_shape.start_width, self.show_pic_shape.start_height,
                         self.show_pic_shape.width, self.show_pic_shape.height)
        central_widget = QWidget()
                # 设置窗口样式表，添加黑色边框
        self.setCentralWidget(central_widget)
        keyboard_shift = 6
        self.row_zero = Row_Zero(
            central_widget,
            self.shape.shape_tuples[0][0],
            self.shape.shape_tuples[0][1],
            self.shape.shape_tuples[0][2],
            self.shape.shape_tuples[0][3],
            self.shape.shape_tuples[0][4],
            self.shape.shape_tuples[0][5],
            keyboard_shift,
        )

        self.row_one = Row_One(
            central_widget,
            self.shape.shape_tuples[1][0],
            self.shape.shape_tuples[1][1],
            self.shape.shape_tuples[1][2],
            self.shape.shape_tuples[1][3],
            self.shape.shape_tuples[1][4],
            self.shape.shape_tuples[1][5],
            keyboard_shift
        )

        self.row_two = Row_Two(
            central_widget,
            self.shape.shape_tuples[2][0],
            self.shape.shape_tuples[2][1],
            self.shape.shape_tuples[2][2],
            self.shape.shape_tuples[2][3],
            self.shape.shape_tuples[2][4],
            self.shape.shape_tuples[2][5],
            self.shape.shape_tuples[2][6],
            keyboard_shift
        )

        self.row_four = Row_Four(
            central_widget,
            self.shape.shape_tuples[3][0],
            self.shape.shape_tuples[3][1],
            self.shape.shape_tuples[3][2],
            self.init_edge_color,
            keyboard_shift
        )

        self.row_five = Row_Five(
            central_widget,
            self.shape.shape_tuples[4][0],
            self.shape.shape_tuples[4][1],
        )

        self.row_six = Row_Six(
            central_widget,
            self.shape.shape_tuples[5][0],
            self.shape.shape_tuples[5][1],
        )

        self.row_seven = Row_Seven(
            central_widget,
            self.shape.shape_tuples[6][0],
            self.shape.shape_tuples[6][1],
        )

        self.row_three = Row_Three(
            central_widget,
            self.shape.shape_tuples[7][0],
            self.shape.shape_tuples[7][1],
            self.shape.shape_tuples[7][2],
        )

        self.row_eight = Row_Eight(
            central_widget,
            self.shape.shape_tuples[8][0],
            self.shape.shape_tuples[8][1],
            self.shape.shape_tuples[8][2],
        )

        self.row_nine = Row_Nine(
            central_widget,
            self.shape.shape_tuples[9][0],
            self.shape.shape_tuples[9][1],
            self.shape.shape_tuples[9][2],
        )

    def set_pic(self, pixmap):
        self.pixmap = pixmap
        # 左对齐：x 坐标为 0
        left_x = 0  
        # 垂直居中：计算 y 坐标
        center_y = (self.height() - self.pixmap.height() - self.height_gap // 2) // 2
        # 设置图片的矩形区域
        self.image_rect = self.pixmap.rect().translated(left_x, center_y)

    def paintEvent(self, event):
        painter = QPainter(self)

        # 1. 绘制图片
        if self.pixmap:
            painter.drawPixmap(self.image_rect.topLeft(), self.pixmap)

        # 确保 painter 正确结束
        painter.end()