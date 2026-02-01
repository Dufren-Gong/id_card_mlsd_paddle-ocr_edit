from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout, QSlider
from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore
import numpy as np

# 自定义 QLabel 类以支持点击事件
class ClickableLabel(QLabel):
    def __init__(self, index, photo_path, display_function, points=[], scale=1, max_flag=False, img = [], outside_color = (), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index  # 存储图片的索引
        self.photo_path = photo_path  # 存储图片路径
        self.display_function = display_function  # 存储显示函数
        self.points = points
        self.points_cache = np.array([])
        self.outside_color = outside_color
        self.scale = scale
        self.scale_cache = 1
        self.img = img
        self.img_cache = []
        self.middle_points = []
        self.max_flag = max_flag
        self.moved_flag = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:  # 检查是否左键点击
            shou_flag = not self.moved_flag and not self.max_flag
            self.display_function(self.index, shou_flag=shou_flag)  # 调用传入的显示函数

class Scroll_Area(QWidget):
    def __init__(self, global_config, width_t, display_large_image_function):
        super().__init__()
        self.global_config = global_config
        self.width_t = width_t
        self.display_large_image_function = display_large_image_function

        self.first_show_flag = True
        # 创建一个 QVBoxLayout 来容纳照片
        self.layout = QVBoxLayout()
        
        # 创建一个新的水平布局来放置 skip_button 和 max_button
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)  # 例如，设置为 10 像素，可以根据需要调整
        # 设置布局内部模块与边界之间的间距
        button_layout.setContentsMargins(0, 0, 0, 0)
        # 创建按钮
        self.up_button = QPushButton("↑")
        self.up_button.setToolTip('调整顺序，将这张照片上移一个位置')
        self.up_button.setFixedWidth(int(width_t / 6))  # 设置按钮的固定宽度

        # 创建按钮
        self.down_button = QPushButton("↓")
        self.down_button.setToolTip('调整顺序，将这张照片下移一个位置')
        self.down_button.setFixedWidth(int(width_t / 6))  # 设置按钮的固定宽度

        # 创建按钮
        self.skip_button = QPushButton("跳过检查")
        self.skip_button.setToolTip('认为全部截图信息正确，点击这个按钮后，可以点击确认所有进入下一步')
        self.skip_button.setDisabled(True)
        self.skip_button.setFixedWidth(int(width_t / 3))  # 设置按钮的固定宽度

        # 创建按钮
        self.confirem_button = QPushButton("确认所有")
        self.confirem_button.setToolTip('确认全部截图信息，将进行下一步，确保所有照片都检查过了，或者点击跳过所有检查按钮。')
        self.confirem_button.setFixedWidth(int(width_t / 3))  # 设置按钮的固定宽度

        # button_layout.addWidget(self.skip_button)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addWidget(self.skip_button)
        button_layout.addWidget(self.confirem_button)
        button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)

        # 创建一个新的水平布局来放置 skip_button 和 max_button
        button_layout1 = QHBoxLayout()
        button_layout1.setSpacing(2)  # 例如，设置为 10 像素，可以根据需要调整
        # 设置布局内部模块与边界之间的间
        button_layout1.setContentsMargins(0, 0, 0, 0)

        # 创建按钮
        self.lift_rotate_button = QPushButton("↺")
        self.lift_rotate_button.setToolTip('向左旋转，逆时针旋转')
        self.lift_rotate_button.setFixedWidth(int(width_t / 6))  # 设置按钮的固定宽度

        # 创建按钮
        self.right_rotate_button = QPushButton("↻")
        self.right_rotate_button.setToolTip('向右旋转，顺时针旋转')
        self.right_rotate_button.setFixedWidth(int(width_t / 6))  # 设置按钮的固定宽度

        # 创建按钮
        self.previous_button = QPushButton("重截这张")
        self.previous_button.setToolTip('放弃上次的截图，重新选择区域')
        self.previous_button.setFixedWidth(int(width_t / 3))  # 设置按钮的固定宽度

        # 创建按钮
        self.confire_this_button = QPushButton("确认截图")
        self.confire_this_button.setToolTip('确认这张截图，并保存')
        self.confire_this_button.setFixedWidth(int(width_t / 3))  # 设置按钮的固定宽度
        button_layout1.addWidget(self.lift_rotate_button)
        button_layout1.addWidget(self.right_rotate_button)
        button_layout1.addWidget(self.previous_button)
        button_layout1.addWidget(self.confire_this_button)
        button_layout1.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)

        # 创建一个新的水平布局来放置 skip_button 和 max_button
        button_layout2 = QHBoxLayout()
        button_layout2.setSpacing(2)  # 例如，设置为 10 像素，可以根据需要调整
        button_layout2.setContentsMargins(0, 0, 0, 0)

        # self.tip_label_color = QLabel('圆弧外围颜色:')
        # self.tip_label_color.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        # self.tip_label_color.setFixedWidth(int(1 * width_t / 3))  # 设置按钮的固定宽度

        # 创建水平滑块
        self.slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)       # 最小值
        self.slider.setMaximum(255)     # 最大值
        self.slider.setInvertedAppearance(True)
        try:
            self.slider.setValue(self.global_config['mlsd_conf']['outside_color'])       # 默认值
        except:
            self.slider.setValue(0)         # 默认值
        self.slider.setTickInterval(50) # 刻度间隔，可选
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow) # 显示刻度，可选
        self.slider.setToolTip('更改圆弧外围颜色,数值越小颜色越深.先确认截图再调色.')
        self.slider.setFixedWidth(int(width_t))  # 设置按钮的固定宽度

        # button_layout2.addWidget(self.tip_label_color)
        button_layout2.addWidget(self.slider)

        self.tip_label = QLabel('缩略图')
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # 创建一个 QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidgetResizable(True)
        # 创建一个 QWidget 用于放置在 QScrollArea 中
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.layout)
        self.tip_label.setFixedWidth(width_t)  # 设置为固定宽度
        
        # 将 QWidget 设置为 QScrollArea 的内容
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setFixedWidth(width_t)  # 设置为固定宽度

        # 垂直布局
        left_layout = QVBoxLayout()
        left_layout.addLayout(button_layout)
        left_layout.addLayout(button_layout1)
        left_layout.addLayout(button_layout2)
        left_layout.addWidget(self.tip_label)
        left_layout.addWidget(self.scroll_area)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(left_layout)  # 设置主布局
        self.labels = []

        # 定义一个方法用于滚动到特定的 ClickableLabel
    def scroll_to_label(self, index):
        if 0 <= index < len(self.labels):  # 检查索引是否有效
            target_label = self.labels[index]  # 获取目标 ClickableLabel
            self.scroll_area.ensureWidgetVisible(target_label)  # 滚动到目标 ClickableLabel

    def add_photos(self, cv_pairs, photo_paths, pair_points=np.array([]), max_flags = [False] * 2, scales=[1]):
        length = len(self.labels)
        for index, path in enumerate(photo_paths):
            # 创建 ClickableLabel 用于显示图片
            out_side_color = self.global_config['mlsd_conf']['outside_color']
            label = ClickableLabel(length + index, path, self.display_large_image_function, pair_points[index], scales[index], max_flag=max_flags[index], img=cv_pairs[index], outside_color=(out_side_color, out_side_color, out_side_color))
            pixmap = QPixmap(path)
            self.labels.append(label)
            # 设置固定宽度，自动计算高度以保持纵横比
            fixed_width = self.width_t - 30
            scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
            scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            label.setPixmap(scaled_pixmap)
            # label.setScaledContents(True)  # 根据需要进行缩放
            label.setFixedSize(fixed_width, scaled_height)  # 设置每张图片的固定宽度
            if index % 2 == 0:
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)  # 左对齐，垂直居中
            else:
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignRight)  # 右对齐，垂直居中
            # label.setMaximumHeight(1000)  # 设置最大高度
            self.layout.addWidget(label)

            # 创建一个 QLabel 来显示序号
            if index % 2 == 0:
                tail = '正面'
            else:
                tail = '背面'
            index_label = QLabel(f"{length + index + 1}  {tail} ↑")
            index_label.setStyleSheet(f"font-size: 16px;")
            index_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # 居中对齐
            index_label.setFixedHeight(15)

            # 将容器添加到主布局
            self.layout.addWidget(index_label)
            if self.first_show_flag:
                self.first_show_flag = False
                self.display_large_image_function(0, not max_flags[index])
