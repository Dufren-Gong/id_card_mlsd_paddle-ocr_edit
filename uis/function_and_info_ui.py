from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QRegularExpressionValidator, QFont, QPalette

names = ['姓名', '性别', '民族', '生日', '住址', '卡号', '有效期']

class DraggableLineEdit(QtWidgets.QLineEdit):
    def __init__(self, shape, parent=None, scale_width=None, space_flag = False, font_size = None, data_flag = False, init_pos = None, init_hk_pas = None, tip=None):
        super().__init__(parent)
        self.shape = shape
        self.setStyleSheet("""QLineEdit {border-width: 1px;border-style: solid;border-color: black;background-color:white;color: black;}QToolTip{background-color: white;color: black;border: 1px solid black;font-size: 12px;}""")
        self.setGeometry(*shape)  # 设置初始位置和大小
        self.default_font = self.font()
        self.space_flag = space_flag
        self.data_flag = data_flag
        self.scale_width = scale_width or shape[2]
        self.font_size = font_size or 24
        self.init_pos = init_pos
        self.init_hk_pas = init_hk_pas
        self.enable_move_flag = False
        self.moved_flag = False
        self.init_flag = True
        self.current_pos = QtCore.QPoint(*shape[:2])
        self.initial_pos = None  # 初始位置
        if tip != None:
            self.setToolTip(tip)

    def get_font_color(self):
        # 使用调色板获取字体颜色
        palette = self.palette()
        color = palette.color(QPalette.ColorRole.WindowText)
        return color.name()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录鼠标按下时的位置
            if self.enable_move_flag:
                self.initial_pos = event.position().toPoint()  # 记录相对于控件的鼠标按下位置
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.enable_move_flag and self.initial_pos != None:
            # 如果有按下事件并且鼠标移动，则更新位置
            # 计算鼠标相对于屏幕的偏移量
            delta = event.position().toPoint() - self.initial_pos
            # 计算控件的新位置
            new_pos = self.current_pos + delta
            # 获取父窗口的几何范围
            parent_widget = self.parent()  # 获取父控件
            if parent_widget:
                parent_rect = parent_widget.rect()  # 父控件的矩形范围

                # 获取控件的宽度和高度
                widget_width = self.width()
                widget_height = self.height()

                # 检查并限制 new_pos 在父窗口范围内
                new_x = max(parent_rect.left(), min(new_pos.x(), parent_rect.right() - widget_width))
                new_y = max(parent_rect.top(), min(new_pos.y(), parent_rect.bottom() - widget_height))
                new_pos = QtCore.QPoint(new_x, new_y)

            # 移动控件并更新当前的位置
            self.move(new_pos)
            
            # 更新控件当前的位置
            self.current_pos = new_pos
            # 将控件置于顶层
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.enable_move_flag:
                self.setCursor(Qt.CursorShape.IBeamCursor)  # 恢复鼠标形状
                self.initial_pos = None
                self.enable_move_flag = False
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        # 创建自定义右键菜单
        menu = QtWidgets.QMenu(self)

        # 设置菜单样式
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid black;
                color: black;
                font-size: 12px;
            }
        """)

        # 添加动作
        move_action = menu.addAction("移动")
        reflect_action = menu.addAction("归位")
        menu.addSeparator()
        copy_action = menu.addAction("复制")
        paste_action = menu.addAction("粘贴")
        cut_action = menu.addAction("剪切")
        select_all_action = menu.addAction("全选")
        delete_action = menu.addAction("删除")
        menu.addSeparator()
        undo_action = menu.addAction("撤销")
        redo_action = menu.addAction("恢复")


        # 连接动作
        copy_action.triggered.connect(lambda: (self.copy(), self.no_drag()))
        paste_action.triggered.connect(lambda: (self.paste(), self.no_drag()))
        select_all_action.triggered.connect(lambda: (self.selectAll(), self.no_drag()))
        undo_action.triggered.connect(lambda: (self.undo(), self.no_drag()))
        redo_action.triggered.connect(lambda: (self.redo(), self.no_drag()))
        cut_action.triggered.connect(lambda: (self.cut(), self.no_drag()))
        delete_action.triggered.connect(lambda: (self.delete_selected_text(), self.no_drag()))
        move_action.triggered.connect(self.move_event)
        reflect_action.triggered.connect(self.reflect_action)

        # 显示菜单
        menu.exec(event.globalPos())

    def delete_selected_text(self):
        """
        删除选中的文本。
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()

    def change_pos(self, mode):
        if mode == 1:
            if self.init_pos != None:
                self.move_event()
                self.move(QtCore.QPoint(self.init_pos[0], self.init_pos[1]))
        elif mode == 2:
            if self.init_hk_pas != None:
                self.move_event()
                self.move(QtCore.QPoint(self.init_hk_pas[0], self.init_hk_pas[1]))
            else:
                self.reflect_action()
        elif mode == 0:
            self.reflect_action()
        self.no_drag()

    def move_event(self):
        # 将控件置于顶层
        if self.init_flag and not self.moved_flag:
            self.moved_flag = True
            QApplication.processEvents()
            self.raise_()
            self.init_flag = False
            color = self.get_font_color()
            self.setStyleSheet(f'QLineEdit{{background-color: rgba(255, 255, 255, 0);border: none;color:{color};}}QToolTip{{background-color: white;color: black;border: 1px solid black;font-size: 12px;}}')
            font = QFont("SimHei", self.font_size)  # "SimHei" 是黑体的字体名称，14 是字号
            self.setFont(font)
            self.setFixedSize(self.scale_width, self.font_size + 7)
            text = self.text()
            if self.space_flag:
                self.setText('\u2009'.join(text))
            if self.data_flag:
                if '年' in text and '月' in text and '日' in text:
                    text = text.replace('年', '*').replace('月', '*').replace('日', '*')
                    info = text.split('*')
                    if len(info) == 4:
                        text = [info[0]] + ['年'] + [info[1]] + ['月'] + [info[2]] + ['日']
                        self.setText(' '.join(text))
        self.setCursor(Qt.CursorShape.ClosedHandCursor)  # 改变鼠标形状为抓取
        self.enable_move_flag = True

    def no_drag(self):
        self.enable_move_flag = False
        self.setCursor(Qt.CursorShape.IBeamCursor)  # 恢复鼠标形状    

    def reflect_action(self):
        if self.moved_flag:
            self.enable_move_flag = False
            self.moved_flag = False
            self.init_flag = True
            QApplication.processEvents()
            self.setFont(self.default_font)
            self.setFixedSize(self.shape[2], self.shape[3])
            self.initial_pos = None  # 停止拖动
            self.setText(self.text().replace(' ', '').replace('\u2009', ''))
            color = self.get_font_color()
            self.setStyleSheet(f"QLineEdit{{border-width: 1px;border-style: solid;border-color: black;background-color:white;color: {color};}}QToolTip{{background-color: white;color: black;border: 1px solid black;font-size: 12px;}}")
            self.move(QtCore.QPoint(*self.shape[:2]))  # 可以选择是否重置位置
            self.current_pos = QtCore.QPoint(*self.shape[:2])
            self.setCursor(Qt.CursorShape.IBeamCursor)  # 恢复鼠标形状

class CustomLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def contextMenuEvent(self, event):
        # 创建自定义右键菜单
        menu = QtWidgets.QMenu(self)

        # 设置菜单样式
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid black;
                color: black;
                font-size: 12px;
            }
        """)

        # 添加动作
        copy_action = menu.addAction("复制")
        # paste_action = menu.addAction("粘贴")
        select_all_action = menu.addAction("全选")

        # 禁用粘贴功能，因为控件是只读的
        # paste_action.setEnabled(False)

        # 连接动作
        copy_action.triggered.connect(self.copy)
        # paste_action.triggered.connect(self.paste)
        select_all_action.triggered.connect(self.selectAll)

        # 显示菜单
        menu.exec(event.globalPos())

class Row_Zero():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 border_width_plus_shape:tuple,
                 up_left_shape: tuple,
                 up_shape: tuple,
                 up_right_shape: tuple,
                 keyboard_shift = 6,
                 ) -> None:
        self.centralwidget = centralwidget
        self.keyboard_shift = keyboard_shift
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)
        self.edge_border_width_plus_pushbutton(border_width_plus_shape)
        self.enable_border_pushbutton(border_width_plus_shape)
        self.edge_up_left_pushbutton(up_left_shape)
        self.edge_up_pushbutton(up_shape)
        self.edge_up_right_pushbutton(up_right_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label0")
        self.tip_label.setText("图名:")
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = CustomLineEdit(parent=self.centralwidget)
        self.pic_name_lineedit.setGeometry(QtCore.QRect(*shape))
        self.pic_name_lineedit.setReadOnly(True)
        self.pic_name_lineedit.setObjectName("pic_name_lineedit0")
        self.pic_name_lineedit.setStyleSheet("""
            QLineEdit {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: white;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def enable_border_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift] + [shape[1]] + [shape[2] * 4 + self.keyboard_shift * 5] + [shape[3]])
        self.enable_border_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.enable_border_button.setGeometry(QtCore.QRect(QtCore.QRect(*shape_temp)))
        self.enable_border_button.setObjectName("enable_border_button")
        self.enable_border_button.setText("开启添加边框功能")
        self.enable_border_button.setToolTip("打开添加边框功能区域按键")
        self.enable_border_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_border_width_plus_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift] + list(shape[1:]))
        self.border_width_plus_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_width_plus_button.setGeometry(QtCore.QRect(QtCore.QRect(*shape_temp)))
        self.border_width_plus_button.setObjectName("border_width_plus_button")
        self.border_width_plus_button.setText("+")
        self.border_width_plus_button.setToolTip("增加添加边框的宽度")
        self.border_width_plus_button.hide()
        self.border_width_plus_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_up_left_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 2] + list(shape[1:]))
        self.border_up_left_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_up_left_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_up_left_button.setObjectName("border_up_left_button")
        self.border_up_left_button.setText("↖")
        self.border_up_left_button.setToolTip("添加/删除左上边框")
        self.border_up_left_button.hide()
        self.border_up_left_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_up_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 3] + list(shape[1:]))
        self.border_up_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_up_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_up_button.setObjectName("border_up_button")
        self.border_up_button.setText("↑")
        self.border_up_button.setToolTip("添加/删除上边框")
        self.border_up_button.hide()
        self.border_up_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_up_right_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 4] + list(shape[1:]))
        self.border_up_right_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_up_right_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_up_right_button.setObjectName("border_up_right_button")
        self.border_up_right_button.setText("↗")
        self.border_up_right_button.setToolTip("添加/删除右上边框")
        self.border_up_right_button.hide()
        self.border_up_right_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class Row_One():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 border_width_minues_shape:tuple,
                 left_shape: tuple,
                 all_shape: tuple,
                 right_shape: tuple,
                 keyboard_shift = 6,
                 init_pos = None,
                 init_hk_pos = None
                 ) -> None:
        self.centralwidget = centralwidget
        self.keyboard_shift = keyboard_shift
        self.init_pos = init_pos
        self.init_hk_pos = init_hk_pos
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)
        self.edge_border_width_minues_pushbutton(border_width_minues_shape)
        self.edge_left_pushbutton(left_shape)
        self.edge_all_pushbutton(all_shape)
        self.edge_right_pushbutton(right_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label")
        self.tip_label.setText(names[0] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = DraggableLineEdit(shape, parent=self.centralwidget, scale_width=230, init_pos=self.init_pos, font_size=26, init_hk_pas=self.init_hk_pos)
        self.pic_name_lineedit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[^\n]*$")))
        self.pic_name_lineedit.setObjectName("pic_name_lineedit")

    def edge_border_width_minues_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift] + list(shape[1:]))
        self.border_width_minues_pushbutton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_width_minues_pushbutton.setGeometry(QtCore.QRect(*shape_temp))
        self.border_width_minues_pushbutton.setObjectName("border_width_minues_pushbutton")
        self.border_width_minues_pushbutton.setText("-")
        self.border_width_minues_pushbutton.setToolTip("减小添加边框的宽度")
        self.border_width_minues_pushbutton.hide()
        self.border_width_minues_pushbutton.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_left_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 2] + list(shape[1:]))
        self.border_left_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_left_button.setGeometry(QtCore.QRect(QtCore.QRect(*shape_temp)))
        self.border_left_button.setObjectName("border_left_button")
        self.border_left_button.setText("←")
        self.border_left_button.setToolTip("添加/删除左边框")
        self.border_left_button.hide()
        self.border_left_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_all_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 3] + list(shape[1:]))
        self.border_all_pushbutton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_all_pushbutton.setGeometry(QtCore.QRect(*shape_temp))
        self.border_all_pushbutton.setObjectName("border_all_pushbutton")
        # self.border_all_pushbutton.setText("□")
        self.border_all_pushbutton.setText("⏻")
        self.border_all_pushbutton.setToolTip("关闭添加边框功能")
        # self.border_all_pushbutton.setToolTip("添加/删除所有边框")
        self.border_all_pushbutton.hide()
        self.border_all_pushbutton.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
                color: red
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_right_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 4] + list(shape[1:]))
        self.border_right_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_right_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_right_button.setObjectName("border_right_button")
        self.border_right_button.setText("→")
        self.border_right_button.setToolTip("添加/删除右边框")
        self.border_right_button.hide()
        self.border_right_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class Row_Two():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 two_tip_label_shape: tuple,
                 two_info_lineedit_shape: tuple,
                 change_shape: tuple,
                 done_left_shape: tuple,
                 down_shape: tuple,
                 down_right_shape: tuple,
                 keyboard_shift = 6,
                 init_pos = None,
                 init_hk_pos = None,
                 init_pos_two = None
                 ) -> None:
        self.centralwidget = centralwidget
        self.keyboard_shift = keyboard_shift
        self.init_pos = init_pos
        self.init_hk_pos = init_hk_pos
        self.init_pos_two = init_pos_two
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)
        self.init_two_tip_label(two_tip_label_shape)
        self.init_two_pic_name_lineedit(two_info_lineedit_shape)
        self.edge_change_pushbutton(change_shape)
        self.edge_down_left_pushbutton(done_left_shape)
        self.edge_down_pushbutton(down_shape)
        self.edge_down_right_pushbutton(down_right_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label2")
        self.tip_label.setText(names[1] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)


    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = DraggableLineEdit(shape, parent=self.centralwidget, scale_width=45, init_pos=self.init_pos, init_hk_pas=self.init_hk_pos, tip='性别，男或者女')
        self.pic_name_lineedit.setObjectName("pic_name_lineedit2")
        self.pic_name_lineedit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[^\n]*$")))
        self.pic_name_lineedit.setMaxLength(1)

    def init_two_tip_label(self, shape):
        self.two_tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.two_tip_label.setGeometry(QtCore.QRect(*shape))
        self.two_tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.two_tip_label.setObjectName("tip_label3")
        self.two_tip_label.setText(names[2] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.two_tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)


    def init_two_pic_name_lineedit(self, shape):
        self.two_pic_name_lineedit = DraggableLineEdit(shape, parent=self.centralwidget, scale_width=135, init_pos=self.init_pos_two, tip='民族，中华56个民族均可')
        self.two_pic_name_lineedit.setObjectName("pic_name_lineedit3")
        self.pic_name_lineedit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[^\n]*$")))

    def edge_change_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 1] + list(shape[1:]))
        self.change_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.change_button.setGeometry(QtCore.QRect(*shape_temp))
        self.change_button.setObjectName("change_button")
        self.change_button.setText("\u296E")
        self.change_button.setToolTip("交换这组照片的位置，并且重新识别正面照片的文字")
        self.change_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_down_left_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 2] + list(shape[1:]))
        self.border_down_left_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_down_left_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_down_left_button.setObjectName("border_down_left_button")
        self.border_down_left_button.setText("↙")
        self.border_down_left_button.setToolTip("添加/删除左下边框")
        self.border_down_left_button.hide()
        self.border_down_left_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_down_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 3] + list(shape[1:]))
        self.border_down_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_down_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_down_button.setObjectName("border_down_button")
        self.border_down_button.setText("↓")
        self.border_down_button.setToolTip("添加/删除下边框")
        self.border_down_button.hide()
        self.border_down_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def edge_down_right_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 4] + list(shape[1:]))
        self.border_down_right_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.border_down_right_button.setGeometry(QtCore.QRect(*shape_temp))
        self.border_down_right_button.setObjectName("border_down_right_button")
        self.border_down_right_button.setText("↘")
        self.border_down_right_button.setToolTip("添加/删除右下边框")
        self.border_down_right_button.hide()
        self.border_down_right_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class Row_Three():
    def __init__(self,
                 centralwidget,
                 match_liangdu_shape: tuple,
                 black_shap: tuple,
                 skip_shape: tuple
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_two_column_three_match_liangdu_pushbutton(match_liangdu_shape)
        self.init_two_column_three_black_pushbutton(black_shap)
        self.init_two_column_three_skip_pushbutton(skip_shape)

    def init_two_column_three_skip_pushbutton(self, shape):
        self.skip_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.skip_button.setGeometry(QtCore.QRect(*shape))
        self.skip_button.setObjectName("skip_button")
        self.skip_button.setText("跳过检查")
        self.skip_button.setDisabled(True)
        self.skip_button.setToolTip('认为全部文字信息正确，可以点击左侧确认所有信息跳过此步骤')
        self.skip_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_two_column_three_match_liangdu_pushbutton(self, shape):
        self.match_liangdu_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.match_liangdu_button.setGeometry(QtCore.QRect(*shape))
        self.match_liangdu_button.setObjectName("match_liangdu_button")
        self.match_liangdu_button.setText("加入高频")
        self.match_liangdu_button.setToolTip('将这组照片和信息添加到高频信息里')
        self.match_liangdu_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_two_column_three_black_pushbutton(self, shape):
        self.black_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.black_button.setGeometry(QtCore.QRect(*shape))
        self.black_button.setObjectName("black_button")
        self.black_button.setText("黑白/彩色")
        self.black_button.setDisabled(True)
        self.black_button.setToolTip('图片变成黑白或者彩色，短按只改变这一张，长按改变所有')
        self.black_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class Row_Four():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 regin_shape:tuple,
                 color_shape:tuple,
                 init_edge_color,
                 keyboard_shift = 6,
                 init_pos = None,
                 init_pos_hk = None
                 ) -> None:
        self.init_edge_color = init_edge_color
        self.keyboard_shift = keyboard_shift
        self.init_pos = init_pos
        self.init_pos_hk = init_pos_hk
        self.colors = ['黑', '偏黑', '灰', '暗灰', '偏白', '白']
        self.regins = ["内地", '香港']
        self.centralwidget = centralwidget
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)
        self.init_one_column_regin_combobox(regin_shape)
        self.init_one_column_two_select_border_color_combobox(color_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label4")
        self.tip_label.setText(names[3] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)


    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = DraggableLineEdit(shape, parent=self.centralwidget, scale_width=340, data_flag=True, init_pos=self.init_pos, init_hk_pas=self.init_pos_hk, tip='生日，顺序年月日，只要以相同分隔符分割即可，会自适应，如2000/12/29')
        self.pic_name_lineedit.setObjectName("pic_name_lineedit4")
        self.pic_name_lineedit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[^\n]*$")))

    def init_one_column_regin_combobox(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift] + list(shape[1:]))
        self.rigin_combobox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.rigin_combobox.setGeometry(QtCore.QRect(*shape_temp))
        self.rigin_combobox.setObjectName("rigin_combobox")
        self.rigin_combobox.setToolTip("身份证归属地类型，可以控制默认位置，如果识别错误，就在这里更改")
        self.rigin_combobox.addItems(self.regins)
        self.rigin_combobox.setStyleSheet("""
            QComboBox {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: white;/* 背景颜色 */
                color: blue;              /* 字体颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_one_column_two_select_border_color_combobox(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift * 2] + list(shape[1:]))
        self.border_color_combobox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.border_color_combobox.setGeometry(QtCore.QRect(*shape_temp))
        self.border_color_combobox.setObjectName("border_color_combobox")
        self.border_color_combobox.setToolTip("选择边框颜色")
        self.border_color_combobox.addItems(self.colors)
        self.border_color_combobox.setCurrentIndex(self.colors.index(self.init_edge_color))
        self.border_color_combobox.hide()
        self.border_color_combobox.setStyleSheet("""
            QComboBox {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: white;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class CustomPlainTextEdit(QtWidgets.QPlainTextEdit):
    # # 定义信号，传递当前文本
    # textSubmitted = pyqtSignal(str)
    def __init__(self, shape, parent=None, init_pos = None, init_hk_pos = None, tip = None):
        super().__init__(parent)
        self.shape = shape
        self.setStyleSheet("""QPlainTextEdit {border-width: 1px;border-style: solid;border-color: black;background-color:white;color: black;}QToolTip{background-color: white;color: black;border: 1px solid black;font-size: 12px;}""")
        self.setGeometry(*shape)  # 设置初始位置和大小
        self.default_font = self.font()
        self.init_pos = init_pos
        self.init_hk_pos = init_hk_pos
        self.enable_move_flag = False
        self.moved_flag = False
        self.init_flag = True
        self.current_pos = QtCore.QPoint(*shape[:2])
        self.initial_pos = None  # 初始位置
        if tip != None:
            self.setToolTip(tip)

    def keyPressEvent(self, event):
        # 检测回车键并发出自定义信号
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # self.textSubmitted.emit(self.toPlainText())
            return  # 阻止默认行为（如换行）
        # 调用父类的 keyPressEvent 处理其他按键
        else:
            key_text = event.text()
            # 禁止输入空格和换行符
            if key_text in [' ', '\n', '\r']:
                return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.enable_move_flag:
                self.initial_pos = event.position().toPoint() 
        super().mousePressEvent(event)

    def get_font_color(self):
        # 使用调色板获取字体颜色
        palette = self.palette()
        color = palette.color(QPalette.ColorRole.WindowText)
        return color.name()

    def no_drag(self):
        self.enable_move_flag = False 

    def mouseMoveEvent(self, event):
        if self.enable_move_flag and self.initial_pos != None:
            # 如果有按下事件并且鼠标移动，则更新位置
            # 计算鼠标相对于屏幕的偏移量
            delta = event.position().toPoint() - self.initial_pos
            # 计算控件的新位置
            new_pos = self.current_pos + delta
            # 获取父窗口的几何范围
            parent_widget = self.parent()  # 获取父控件
            if parent_widget:
                parent_rect = parent_widget.rect()  # 父控件的矩形范围

                # 获取控件的宽度和高度
                widget_width = self.width()
                widget_height = self.height()
                # 检查并限制 new_pos 在父窗口范围内
                new_x = max(parent_rect.left(), min(new_pos.x(), parent_rect.right() - widget_width))
                new_y = max(parent_rect.top(), min(new_pos.y(), parent_rect.bottom() - widget_height))
                new_pos = QtCore.QPoint(new_x, new_y)

            # 移动控件并更新当前的位置
            self.move(new_pos)
            
            # 更新控件当前的位置
            self.current_pos = new_pos
            # 将控件置于顶层
        super().mouseMoveEvent(event)

    def change_pos(self, mode):
        if mode == 1:
            if self.init_pos != None:
                self.move_event()
                self.move(QtCore.QPoint(self.init_pos[0], self.init_pos[1]))
        elif mode == 2:
            if self.init_hk_pos != None:
                self.move_event()
                self.move(QtCore.QPoint(self.init_hk_pos[0], self.init_hk_pos[1]))
            else:
                self.reflect_action()
        elif mode == 0:
            self.reflect_action()
        self.no_drag()

    def move_event(self):
        if self.init_flag and not self.moved_flag:
            self.moved_flag = True
            QApplication.processEvents()
            self.raise_()
            self.init_flag = False
            color = self.get_font_color()
            self.setStyleSheet(f'QPlainTextEdit{{background-color: rgba(255, 255, 255, 0);border: none;color:{color};}}QToolTip{{background-color: white;color: black;border: 1px solid black;font-size: 12px;}}')
            font = QFont("SimHei", 24)  # "SimHei" 是黑体的字体名称，14 是字号
            self.setFont(font)
            self.setFixedSize(375, 120)
        self.enable_move_flag = True

    def contextMenuEvent(self, event):
        # 创建自定义右键菜单
        menu = QtWidgets.QMenu(self)

        # 设置菜单样式
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid black;
                color: black;
                font-size: 12px;
            }
        """)

        # 添加动作
        move_action = menu.addAction("移动")
        reflect_action = menu.addAction("归位")
        menu.addSeparator()
        copy_action = menu.addAction("复制")
        paste_action = menu.addAction("粘贴")
        cut_action = menu.addAction("剪切")
        select_all_action = menu.addAction("全选")
        delete_action = menu.addAction("删除")
        menu.addSeparator()
        undo_action = menu.addAction("撤销")
        redo_action = menu.addAction("恢复")

        # 连接动作
        copy_action.triggered.connect(lambda: (self.copy(), self.no_drag()))
        paste_action.triggered.connect(lambda: (self.paste(), self.no_drag()))
        select_all_action.triggered.connect(lambda: (self.selectAll(), self.no_drag()))
        undo_action.triggered.connect(lambda: (self.undo(), self.no_drag()))
        redo_action.triggered.connect(lambda: (self.redo(), self.no_drag()))
        cut_action.triggered.connect(lambda: (self.cut(), self.no_drag()))
        delete_action.triggered.connect(lambda: (self.delete_selected_text(), self.no_drag()))
        move_action.triggered.connect(self.move_event)
        reflect_action.triggered.connect(self.reflect_action)

        # 显示菜单
        menu.exec(event.globalPos())

    def delete_selected_text(self):
        """
        删除选中的文本。
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()

    def reflect_action(self):
        if self.moved_flag:
            self.enable_move_flag = False
            self.moved_flag = False
            self.init_flag = True
            QApplication.processEvents()
            self.setFont(self.default_font)
            self.setFixedSize(self.shape[2], self.shape[3])
            self.initial_pos = None  # 停止拖动
            color = self.get_font_color()
            self.setStyleSheet(f"QPlainTextEdit{{border-width: 1px;border-style: solid;border-color: black;background-color:white;color: {color};}}QToolTip{{background-color: white;color: black;border: 1px solid black;font-size: 12px;}}")
            self.move(QtCore.QPoint(*self.shape[:2]))  # 可以选择是否重置位置
            self.current_pos = QtCore.QPoint(*self.shape[:2])

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.enable_move_flag:
                # self.setCursor(Qt.CursorShape.IBeamCursor)  # 恢复鼠标形状
                self.initial_pos = None
                self.enable_move_flag = False
        super().mouseReleaseEvent(event)

class Row_Five():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 init_pos = None
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_pos = init_pos
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label5")
        self.tip_label.setText(names[4] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = CustomPlainTextEdit(shape, parent=self.centralwidget, init_pos=self.init_pos, tip='地址，有时候背景花纹会识别为"上"， 末尾会多"中国"字样等，\n文本会变成检查色，注意检查，出现检查色不更改也没问题。')
        self.pic_name_lineedit.setObjectName("pic_name_lineedit5")

class Row_Six():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 all_moved_shape: tuple,
                 keyboard_shift,
                 init_pos = None,
                 init_pos_hk = None,
                 ) -> None:
        self.centralwidget = centralwidget
        self.keyboard_shift = keyboard_shift
        self.init_pos = init_pos
        self.init_pos_hk = init_pos_hk
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)
        self.init_two_column_all_moved_pushbutton(all_moved_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label6")
        self.tip_label.setText(names[5] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = DraggableLineEdit(shape, parent=self.centralwidget, scale_width=500, space_flag=True, font_size=28, init_pos=self.init_pos, init_hk_pas=self.init_pos_hk)
        self.pic_name_lineedit.setObjectName("pic_name_lineedit6")
        self.pic_name_lineedit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[^\n]*$")))

    def init_two_column_all_moved_pushbutton(self, shape):
        shape_temp = tuple([shape[0] + self.keyboard_shift] + list(shape[1:]))
        self.all_moved_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.all_moved_button.setGeometry(QtCore.QRect(*shape_temp))
        self.all_moved_button.setObjectName("all_moved_button")
        self.all_moved_button.setToolTip('默认将所有对比信息文本框移动到照片默认位置比较，或者不移动')
        self.all_moved_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class CustomPlainTextEdit_fun(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QPlainTextEdit {
                border-width: 1px;
                border-style: solid;
                border-color: black;
                background-color: white;
                color: black;
                font-size: 12px;
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def contextMenuEvent(self, event):
        # 创建自定义右键菜单
        menu = QtWidgets.QMenu(self)

        # 设置菜单样式
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid black;
                color: black;
                font-size: 12px;
            }
        """)

        # 添加动作
        copy_action = menu.addAction("复制")
        # paste_action = menu.addAction("粘贴")
        select_all_action = menu.addAction("全选")

        # 禁用粘贴功能，因为控件是只读的
        # paste_action.setEnabled(False)

        # 连接动作
        copy_action.triggered.connect(self.copy)
        # paste_action.triggered.connect(self.paste)
        select_all_action.triggered.connect(self.selectAll)

        # 显示菜单
        menu.exec(event.globalPos())

class Row_six_seven():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 init_pos = None,
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_pos = init_pos
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label")
        self.tip_label.setText(names[6] + ':')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = DraggableLineEdit(shape, parent=self.centralwidget, tip='身份证有效期信息', init_pos=self.init_pos)
        self.pic_name_lineedit.setObjectName("pic_name_lineedit")
        self.pic_name_lineedit.setReadOnly(True)

class Row_Seven():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 info_lineedit_shape: tuple,
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_one_tip_label(tip_label_shape)
        self.init_one_pic_name_lineedit(info_lineedit_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label8")
        self.tip_label.setText('参考：')
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)


    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = CustomPlainTextEdit_fun(parent=self.centralwidget)
        self.pic_name_lineedit.setGeometry(QtCore.QRect(*shape))
        self.pic_name_lineedit.setObjectName("pic_name_lineedit8")
        self.pic_name_lineedit.setToolTip("识别出来的所有照片文字")
        self.pic_name_lineedit.setReadOnly(True)

class Row_Eight():
    def __init__(self,
                 centralwidget,
                 liangdu_plus_shape: tuple,
                 duibidu_plus_shape: tuple,
                 confire_all_shape: tuple,
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_two_column_three_confire_all_pushbutton(confire_all_shape)
        self.init_two_column_two_liangdu_plus_pushbutton(liangdu_plus_shape)
        self.init_two_column_two_duibidu_plus_pushbutton(duibidu_plus_shape)

    def init_two_column_three_confire_all_pushbutton(self, shape):
        self.confire_all_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.confire_all_button.setGeometry(QtCore.QRect(*shape))
        self.confire_all_button.setObjectName("confire_all_button")
        self.confire_all_button.setText("确认所有")
        self.confire_all_button.setToolTip('确认全部文字信息，确保所有组的正面照片都点击了确认文字按钮，或者点击跳过检查按钮，然后点击这个按钮，照片编辑结束')
        self.confire_all_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_two_column_two_duibidu_plus_pushbutton(self, shape):
        self.duibidu_plus_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.duibidu_plus_button.setGeometry(QtCore.QRect(*shape))
        self.duibidu_plus_button.setObjectName("duibidu_plus_button")
        self.duibidu_plus_button.setText("\u262F  +")
        self.duibidu_plus_button.setToolTip('增加图像对比度')
        self.duibidu_plus_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_two_column_two_liangdu_plus_pushbutton(self, shape):
        self.liangdu_plus_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.liangdu_plus_button.setGeometry(QtCore.QRect(*shape))
        self.liangdu_plus_button.setObjectName("liangdu_plus_button")
        self.liangdu_plus_button.setText("\u2600  +")
        self.liangdu_plus_button.setToolTip('增加图像亮度')
        self.liangdu_plus_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

class Row_Nine():
    def __init__(self,
                 centralwidget,
                 liangdu_minues_shape: tuple,
                 duibidu_minues_shape: tuple,
                 comfire_button_shape: tuple,
                 ) -> None:
        self.centralwidget = centralwidget
        self.switch_flag = True
        self.init_two_column_two_comfire_info_pushbutton(comfire_button_shape)
        self.init_two_column_two_liangdu_minues_pushbutton(liangdu_minues_shape)
        self.init_two_column_two_duibidu_minues_pushbutton(duibidu_minues_shape)

    def init_two_column_two_comfire_info_pushbutton(self, shape):
        self.comfire_info_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.comfire_info_button.setGeometry(QtCore.QRect(*shape))
        self.comfire_info_button.setObjectName("comfire_info_button")
        self.comfire_info_button.setText("确认文字")
        self.comfire_info_button.setToolTip('点击确认文字表示你检查过了，在你编辑信息的时候信息其实已经保存了')
        self.comfire_info_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_two_column_two_duibidu_minues_pushbutton(self, shape):
        self.duibidu_minues_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.duibidu_minues_button.setGeometry(QtCore.QRect(*shape))
        self.duibidu_minues_button.setObjectName("duibidu_minues_button")
        self.duibidu_minues_button.setText("\u262F  -")
        self.duibidu_minues_button.setToolTip('降低图像对比度')
        self.duibidu_minues_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)

    def init_two_column_two_liangdu_minues_pushbutton(self, shape):
        self.liangdu_minues_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.liangdu_minues_button.setGeometry(QtCore.QRect(*shape))
        self.liangdu_minues_button.setObjectName("liangdu_minues_button")
        self.liangdu_minues_button.setText("\u2600  -")
        self.liangdu_minues_button.setToolTip('降低图像亮度')
        self.liangdu_minues_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
            QToolTip {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    font-size: 12px;
                }
        """)