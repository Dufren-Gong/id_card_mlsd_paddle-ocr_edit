from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
from my_utils.utils import cv_imread
from my_utils.Traditional_to_Simplified_Chinese import fan_to_jian

# 自定义 QLabel 类以支持点击事件
class ClickableLabel(QLabel):
    def __init__(self, index, photo_path, display_function, info=[], print=[], img = [], liangdu_shift=1.0, duibidu_shift=1.0, color = True, edge_ipx = 1, add_to_gaopin = False, borders = [], edge_color = (), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index  # 存储图片的索引
        self.photo_path = photo_path  # 存储图片路径
        self.display_function = display_function  # 存储显示函数
        self.info = info
        self.print = print
        self.img = img
        self.liangdu_shift = liangdu_shift
        self.borders = borders
        self.color = color
        self.duibidu_shift = duibidu_shift
        self.add_to_gaopin = add_to_gaopin
        self.edge_ipx = edge_ipx
        self.edge_color = edge_color

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:  # 检查是否左键点击
            self.display_function(self.photo_path, self.index)  # 调用传入的显示函数

class Scroll_Area(QWidget):
    def __init__(self, width_t, display_large_image_function, init_edge_ipx, init_edge_color):
        super().__init__()
        self.labels = []
        self.width_t = width_t
        self.display_large_image_function = display_large_image_function
        self.init_edge_ipx = init_edge_ipx
        self.init_edge_color = init_edge_color
        self.first_show_flag = True
        # 创建一个 QVBoxLayout 来容纳照片
        self.layout = QVBoxLayout()

        self.tip_label = QLabel('缩略图')
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tip_label.setFixedWidth(width_t)  # 设置为固定宽度

        # 创建一个 QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidgetResizable(True)

        # 创建一个 QWidget 用于放置在 QScrollArea 中
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.layout)
        
        # 将 QWidget 设置为 QScrollArea 的内容
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setFixedWidth(width_t)  # 设置为固定宽度

        # 垂直布局
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.tip_label)
        left_layout.addWidget(self.scroll_area)

        self.setLayout(left_layout)  # 设置主布局

    # 定义一个方法用于滚动到特定的 ClickableLabel
    def scroll_to_label(self, index):
        if 0 <= index < len(self.labels):  # 检查索引是否有效
            target_label = self.labels[index]  # 获取目标 ClickableLabel
            self.scroll_area.ensureWidgetVisible(target_label)  # 滚动到目标 ClickableLabel

    def add_photos_for_name(self, photo_path, catch, pic_info_dict):
        length = len(self.labels)
        photo_name = os.path.basename(photo_path).rsplit('.', maxsplit=1)
        back_name = str(eval(photo_name[0]) + 1) + '.' + photo_name[-1]
        back_path = os.path.join(os.path.dirname(photo_path), back_name)
        for index, path in enumerate([photo_path, back_path]):
            # 创建 ClickableLabel 用于显示图片
            if catch[7] == '香港':
                try:
                    catch[0] = fan_to_jian(catch[0])
                except:
                    pass
            label = ClickableLabel(length + index, path, self.display_large_image_function, info=catch, print=pic_info_dict, img=cv_imread(path), edge_ipx=self.init_edge_ipx, edge_color=self.init_edge_color)
            pixmap = QPixmap(path)
            self.labels.append(label)
            # 设置固定宽度，自动计算高度以保持纵横比
            fixed_width = self.width_t - 30
            scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
            scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            label.setPixmap(scaled_pixmap)
            label.setScaledContents(True)  # 根据需要进行缩放
            label.setFixedSize(fixed_width, scaled_height)  # 设置每张图片的固定宽度
            # label.setMaximumHeight(1000)  # 设置最大高度
            self.layout.addWidget(label)  # 将 QLabel 添加到布局中

            if index % 2 == 1:
                # 创建一个 QLabel 来显示序号
                index_label = QLabel(f"{int(length / 2) + 1} ↑")
                index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
                index_label.setFixedHeight(10)
                
                self.layout.addWidget(index_label)  # 将 QLabel 添加到布局中
        #展示第一张照片
        if self.first_show_flag:
            self.first_show_flag = False
            self.display_large_image_function(photo_path, 0)