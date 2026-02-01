from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt6 import QtCore
from PyQt6.QtGui import QPainter, QPen, QPainterPath, QColor
from uis.shapes import Ui_Shapes
from windows.show_info_window import Show_Info_Window
import numpy as np
import copy
from my_utils.utils import calculate_distance

class Show_Pic_Window(QMainWindow):
    points_updated = QtCore.pyqtSignal(list)
    def __init__(self, show_info: Show_Info_Window, global_config):
        super().__init__()
        self.screen_size = QApplication.primaryScreen().size()
        self.max_size = (self.screen_size.width()*0.8, self.screen_size.height()*0.8)
        self.show_info_window = show_info
        self.global_config = global_config
        self.n_px = global_config['mlsd_conf']['n_px']
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
        self.init_ui()

    def change_position(self, start=(100, 100)):
        self.show_pic_shape.start_width = start[0]
        self.show_pic_shape.start_height = start[1]
        self.refresh_ui()

    def clear_content(self):
        # 清空相关属性
        self.points = []
        self.pixmap = None  # 确保不再绘制当前图像
        self.update()  # 刷新界面

    def clear_content_point_and_line(self):
        # 清空所有与绘图相关的属性
        self.points = []
        self.new_points = []
        self.dragging_point = None
        self.update()  # 刷新界面

    def change_size(self, shape=(500, 800)):
        self.show_pic_shape.layout([shape[0]],
                                   [[shape[1]]])
        self.refresh_ui()
        self.setFixedSize(self.show_pic_shape.round_gap * 2 + shape[1], self.show_pic_shape.round_gap * 2 + shape[0])

    def init_ui(self):
        self.setGeometry(self.show_pic_shape.start_width, self.show_pic_shape.start_height,
                         self.show_pic_shape.width, self.show_pic_shape.height)
        central_widget = QWidget()
                # 设置窗口样式表，添加黑色边框
        self.setCentralWidget(central_widget)

    def refresh_ui(self):
        self.setFixedSize(self.show_pic_shape.width, self.show_pic_shape.height)

    def set_points(self, points, shou_flag = True):
        #在第四象限，从原点最近的点起，顺时针排序
        if len(points) == 4:
            if shou_flag:
                width = (calculate_distance(points[0], points[1]) + calculate_distance(points[2], points[3])) / 2
                height= (calculate_distance(points[2], points[1]) + calculate_distance(points[0], points[3])) / 2
                if width > height:
                    up_gap = self.global_config['mlsd_conf']['up_gap']
                    down_gap = self.global_config['mlsd_conf']['down_gap']
                    left_gap = self.global_config['mlsd_conf']['left_gap']
                    right_gap = self.global_config['mlsd_conf']['right_gap']
                else:
                    up_gap = self.global_config['mlsd_conf']['left_gap']
                    down_gap = self.global_config['mlsd_conf']['right_gap']
                    left_gap = self.global_config['mlsd_conf']['up_gap']
                    right_gap = self.global_config['mlsd_conf']['down_gap']
                points[0][0] = points[0][0] + left_gap
                points[0][1] = points[0][1] + up_gap
                points[1][0] = points[1][0] - right_gap
                points[1][1] = points[1][1] + up_gap
                points[2][0] = points[2][0] - right_gap
                points[2][1] = points[2][1] - down_gap
                points[3][0] = points[3][0] + left_gap
                points[3][1] = points[3][1] - down_gap
            self.points = [QtCore.QPoint(x+self.show_pic_shape.round_gap, y+self.show_pic_shape.round_gap) for x, y in points]
            self.calculate_middle_points()
            self.new_points = points
            self.update()
        else:
            self.points = []
            self.middle_points = []
            self.update()
        self.new_points = np.array([[point.x() - self.show_pic_shape.round_gap, point.y() - self.show_pic_shape.round_gap] for point in self.points])
        self.points_updated.emit(self.new_points)

    def set_pic(self, pixmap):
        self.pixmap = pixmap
        # self.setMinimumSize(self.pixmap.width(), self.pixmap.height())
        # Calculate center to display image
        center_x = (self.width() - self.pixmap.width()) // 2
        center_y = (self.height() - self.pixmap.height()) // 2
        self.image_rect = self.pixmap.rect().translated(center_x, center_y)

    def calculate_middle_points(self):
        self.middle_points.clear()
        for i in range(4):
            p1 = self.points[i]
            p2 = self.points[(i+1) % 4]
            middle_point = QtCore.QPoint((p1.x() + p2.x()) // 2, (p1.y() + p2.y()) // 2)
            self.middle_points.append(middle_point)

    def paintEvent(self, event):
        painter = QPainter(self)

        # 1. 绘制图片
        if self.pixmap:
            painter.drawPixmap(self.image_rect.topLeft(), self.pixmap)

        # 2. 绘制四边形外部灰白色屏障
        if len(self.points) == 4:
            # 创建全窗口的路径
            shou_arr = [self.show_pic_shape.round_gap] * 2 + [-self.show_pic_shape.round_gap] * 2
            rect_with_margin = self.rect().adjusted(*shou_arr)
            full_path = QPainterPath()
            full_path.addRect(QtCore.QRectF(rect_with_margin))

            # 创建四边形路径
            polygon_path = QPainterPath()
            polygon_path.moveTo(QtCore.QPointF(self.points[0]))
            for i in range(1, 4):
                polygon_path.lineTo(QtCore.QPointF(self.points[i]))
            polygon_path.closeSubpath()

            # 减去四边形路径，保留外部路径
            full_path -= polygon_path
            painter.fillPath(full_path, QColor(*self.map_color))  # 灰白色遮罩, RGBA，最后一个参数表示透明度

        # 3. 绘制四边形的边框和点
            pen = QPen(QtCore.Qt.GlobalColor.red)
            pen.setWidth(1)
            painter.setPen(pen)
            for i in range(4):
                painter.drawLine(self.points[i], self.points[(i + 1) % 4])

            # 绘制绿色角点
            painter.setBrush(QtCore.Qt.GlobalColor.green)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            for point in self.points:
                painter.drawEllipse(point, 4, 4)

            # 绘制蓝色中间点
            painter.setBrush(QtCore.Qt.GlobalColor.blue)
            for middle_point in self.middle_points:
                painter.drawEllipse(middle_point, 4, 4)

        # 确保 painter 正确结束
        painter.end()

    def mousePressEvent(self, event):
        for i, point in enumerate(self.points):
            if abs(event.position().x() - point.x()) <= 10 and abs(event.position().y() - point.y()) <= 10:
                self.dragging_point = i
                self.selected_point = i
                self.selected_middle_point = None
                return

        for i, middle_point in enumerate(self.middle_points):
            if i % 2 == 0:
                if abs(event.position().x() - middle_point.x()) <= 20 and abs(event.position().y() - middle_point.y()) <= 5:
                    self.dragging_middle = i
                    self.selected_point = None
                    self.selected_middle_point = i
                    return
            else:
                if abs(event.position().x() - middle_point.x()) <= 5 and abs(event.position().y() - middle_point.y()) <= 20:
                    self.dragging_middle = i
                    self.selected_point = None
                    self.selected_middle_point = i
                    return
        self.selected_point = None
        self.selected_middle_point = None

    def gap(self, point):
        new_x, new_y = point
        flag = False
        # 检查边界条件，如果超出则限制在边界内
        if new_x < self.show_pic_shape.round_gap:
            new_x = self.show_pic_shape.round_gap
            flag = True
        elif new_x > -self.show_pic_shape.round_gap + int(self.show_pic_shape.width*self.scale):
            new_x = -self.show_pic_shape.round_gap + int(self.show_pic_shape.width*self.scale)
            flag = True

        if new_y < self.show_pic_shape.round_gap:
            new_y = self.show_pic_shape.round_gap
            flag = True
        elif new_y > -self.show_pic_shape.round_gap + int(self.show_pic_shape.height*self.scale):
            new_y = -self.show_pic_shape.round_gap + int(self.show_pic_shape.height*self.scale)
            flag = True
        return new_x, new_y, flag

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Up \
            or event.key() == QtCore.Qt.Key.Key_Down \
            or event.key() == QtCore.Qt.Key.Key_Left \
            or event.key() == QtCore.Qt.Key.Key_Right:
            if self.selected_point is not None:
                if event.key() == QtCore.Qt.Key.Key_Up:
                    new_y = self.points[self.selected_point].y() - self.n_px
                    _, new_y, _ = self.gap((self.points[self.selected_point].x(), new_y))
                    self.points[self.selected_point].setY(new_y)
                elif event.key() == QtCore.Qt.Key.Key_Down:
                    new_y = self.points[self.selected_point].y() + self.n_px
                    _, new_y, _ = self.gap((self.points[self.selected_point].x(), new_y))
                    self.points[self.selected_point].setY(new_y)
                elif event.key() == QtCore.Qt.Key.Key_Left:
                    new_x = self.points[self.selected_point].x() - self.n_px
                    new_x, _, _ = self.gap((new_x, self.points[self.selected_point].x()))
                    self.points[self.selected_point].setX(new_x)
                elif event.key() == QtCore.Qt.Key.Key_Right:
                    new_x = self.points[self.selected_point].x() + self.n_px
                    new_x, _, _ = self.gap((new_x, self.points[self.selected_point].x()))
                    self.points[self.selected_point].setX(new_x)
                # 重新计算中间点并更新显示
                self.calculate_middle_points()
                self.update()
            if self.selected_middle_point is not None:
                # 设置每次移动的像素数量
                i = self.selected_middle_point
                p1 = self.points[i]
                p2 = self.points[(i+1) % 4]
                if event.key() == QtCore.Qt.Key.Key_Up:
                    new_x = self.middle_points[self.selected_middle_point].x()
                    new_y = self.middle_points[self.selected_middle_point].y() - self.n_px
                elif event.key() == QtCore.Qt.Key.Key_Down:
                    new_x = self.middle_points[self.selected_middle_point].x()
                    new_y = self.middle_points[self.selected_middle_point].y() + self.n_px
                elif event.key() == QtCore.Qt.Key.Key_Left:
                    new_x = self.middle_points[self.selected_middle_point].x() - self.n_px
                    new_y = self.middle_points[self.selected_middle_point].y()
                elif event.key() == QtCore.Qt.Key.Key_Right:
                    new_x = self.middle_points[self.selected_middle_point].x() + self.n_px
                    new_y = self.middle_points[self.selected_middle_point].y()
                delta_x = round(new_x) - (p1.x() + p2.x()) // 2
                delta_y = round(new_y) - (p1.y() + p2.y()) // 2
                newx_1, newy_1, flag1 = self.gap((p1.x() + delta_x, p1.y() + delta_y))
                newx_2, newy_2, flag2 = self.gap((p2.x() + delta_x, p2.y() + delta_y))
                if not flag1 and not flag2:
                    p2.setX(newx_2)
                    p1.setX(newx_1)
                    p1.setY(newy_1)
                    p2.setY(newy_2)
                # 重新计算中间点并更新显示
                self.calculate_middle_points()
                self.update()

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Up or event.key() == QtCore.Qt.Key.Key_Down or event.key() == QtCore.Qt.Key.Key_Left or event.key() == QtCore.Qt.Key.Key_Right:
            self.new_points = np.array([[point.x() - self.show_pic_shape.round_gap, point.y() - self.show_pic_shape.round_gap] for point in self.points])
            self.points_updated.emit(self.new_points)

    def mouseMoveEvent(self, event):
        if self.dragging_point is not None:
            new_x = round(event.position().x())
            new_y = round(event.position().y())
            new_x, new_y, _ = self.gap((new_x, new_y))
            self.points[self.dragging_point].setX(round(new_x))
            self.points[self.dragging_point].setY(round(new_y))
            self.calculate_middle_points()
            self.update()
        elif self.dragging_middle is not None:
            i = self.dragging_middle
            p1 = self.points[i]
            p2 = self.points[(i+1) % 4]
            delta_x = round(event.position().x()) - (p1.x() + p2.x()) // 2
            delta_y = round(event.position().y()) - (p1.y() + p2.y()) // 2
            newx_1, newy_1, flag1 = self.gap((p1.x() + delta_x, p1.y() + delta_y))
            newx_2, newy_2, flag2 = self.gap((p2.x() + delta_x, p2.y() + delta_y))
            if not (flag1 or flag2):
                if i % 2 == 1:
                    p2.setX(newx_2)
                    p1.setX(newx_1)
                else:
                    p1.setY(newy_1)
                    p2.setY(newy_2)
            self.calculate_middle_points()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_point = None
        self.dragging_middle = None
        self.new_points = np.array([[point.x() - self.show_pic_shape.round_gap, point.y() - self.show_pic_shape.round_gap] for point in self.points])
        self.points_updated.emit(self.new_points)  # 发出信号