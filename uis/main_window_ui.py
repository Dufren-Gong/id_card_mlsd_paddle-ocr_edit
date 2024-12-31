from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

def merge_shape(shapes, gap):
    start_width = shapes[0][0]
    start_height = shapes[0][1]
    height = shapes[0][3]
    width = 0
    for i in shapes:
        width += i[2]
    gaps = len(shapes) - 1
    width += gaps * gap
    return (start_width, start_height, width, height)

class Row_Zero():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 file_types_combobox_shape: tuple,
                 exit_button_shape: tuple) -> None:
        self.centralwidget = centralwidget
        self.file_types = ["文件夹", "照片"]
        self.init_one_tip_label(tip_label_shape)
        self.init_one_column_two_select_file_file_type_combobox(file_types_combobox_shape)
        self.init_one_pic_name_lineedit(file_types_combobox_shape)
        self.init_two_column_three_exit_pushbutton(exit_button_shape)
        self.init_one_select_newest_checkbox(merge_shape([tip_label_shape, file_types_combobox_shape], 4))

    def init_two_column_three_exit_pushbutton(self, shape):
        self.exit_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.exit_button.setGeometry(QtCore.QRect(*shape))
        self.exit_button.setObjectName("exit_button")
        self.exit_button.setText("打开/清空照片")
        self.exit_button.setToolTip('短按打开“照片放这里”文件夹,长按清空“照片放这里”文件夹里的所有照片')
        self.exit_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label")
        self.tip_label.setText("文件类型:")
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_column_two_select_file_file_type_combobox(self, shape):
        self.file_type_combobox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.file_type_combobox.setGeometry(QtCore.QRect(*shape))
        self.file_type_combobox.setObjectName("file_type_combobox")
        self.file_type_combobox.setToolTip("添加的文件夹或压缩包只能含照片，并且是双数。添加的照片数量也必须是双数。")
        self.file_type_combobox.addItems(self.file_types)
        self.file_type_combobox.setCurrentIndex(0)
        self.file_type_combobox.setStyleSheet("""
            QComboBox {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: white;/* 背景颜色 */
            }
        """)

    def init_one_pic_name_lineedit(self, shape):
        self.pic_name_lineedit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.pic_name_lineedit.setGeometry(QtCore.QRect(*shape))
        self.pic_name_lineedit.setObjectName("pic_name_lineedit4")
        self.pic_name_lineedit.setToolTip("在这里输入要查询的名字")
        self.pic_name_lineedit.hide()
        validator = QRegularExpressionValidator(QRegularExpression(r"^[^\n]*$"))
        self.pic_name_lineedit.setValidator(validator)
        self.pic_name_lineedit.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

    def init_one_select_newest_checkbox(self, shape):
        self.select_newest_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.select_newest_checkbox.setGeometry(QtCore.QRect(*shape))
        self.select_newest_checkbox.setObjectName("select_newest_checkbox")
        self.select_newest_checkbox.setText("默认最新编辑的文件夹")
        # self.select_newest_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.select_newest_checkbox.setToolTip("默认选择最新编辑结果的文件夹，就不用再选择了，直接制作word，如果要选择其他文件夹，取消选中")
        self.select_newest_checkbox.hide()
        self.select_newest_checkbox.setChecked(True)

class Row_One():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 select_function_combobox_shape: tuple,
                 enable_update) -> None:
        self.centralwidget = centralwidget
        self.enable_update = enable_update
        self.mode_options = ["截图识别", '文字识别', '查询信息', '合并信息到最新', "开单", "拿货", "转单", "年费", "补单", "补卡", "所有类型", "PDF转照片", '更新软件']
        self.init_one_tip_label(tip_label_shape)
        self.init_one_column_two_select_function_combobox(select_function_combobox_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label")
        self.tip_label.setText("选择功能:")
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_column_two_select_function_combobox(self, shape):
        self.function_combobox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.function_combobox.setGeometry(QtCore.QRect(*shape))
        self.function_combobox.setObjectName("function_combobox")
        self.function_combobox.setToolTip("前两个选项   :所选择的文件夹只能包含图片,并且保证身正面照在前\n                    如果直接识别照片文字请确保照片方向和正反顺序正确\n查询信息      :在高频信息里和缓存照片里查找这个人是否已经编辑过且保存下来了\n                    有这个人的照片和信息的话就不用编辑这个人的照片了\npdf转照片    :直接选择pdf文件,照片会生成到'最新编辑结果'的最新文件夹里\n合并最新编辑:选择文件夹,把里面的所有照片和.info信息合并到'最新编辑结果'的最新文件夹里\n制作全部      :是同时制作所有类型的word,其他都是单独制作某个类型的word")
        if not self.enable_update:
            self.function_combobox.addItems(self.mode_options[:-1])
        else:
            self.function_combobox.addItems(self.mode_options)
        self.function_combobox.setMaxVisibleItems(len(self.mode_options))
        self.function_combobox.setCurrentIndex(0)
        self.function_combobox.setStyleSheet("""
            QComboBox {
                border-width: 1px;
                border-style: solid;
                border-color: black;
                background-color: white;
                color: black;  /* 设置字体颜色为红色 */
            }
        """)

class Row_Two():
    def __init__(self,
                 centralwidget,
                 open_excel_shape: tuple,
                 open_newest_button_shape: tuple,
                 select_files_button_shape: tuple,
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_two_column_one_open_newest_pushbutton(open_newest_button_shape)
        self.init_two_column_one_open_excel_pushbutton(open_excel_shape)
        self.init_two_column_one_select_files_pushbutton(select_files_button_shape)

    def init_two_column_one_select_files_pushbutton(self, shape):
        self.select_files_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.select_files_button.setGeometry(QtCore.QRect(*shape))
        self.select_files_button.setObjectName("select_files_button")
        self.select_files_button.setText("选择文件/文件夹")
        self.select_files_button.setToolTip('选择文件或者文件夹直接跳转开始编辑')
        self.select_files_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

    def init_two_column_one_open_newest_pushbutton(self, shape):
        self.open_newest_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.open_newest_button.setGeometry(QtCore.QRect(*shape))
        self.open_newest_button.setObjectName("open_newest_button")
        self.open_newest_button.setText("打开最新/删除所有编辑")
        self.open_newest_button.setToolTip('短按打开编辑结果中最新生成结果的文件夹，长按删除"照片编辑结果"中所有编辑')
        self.open_newest_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

    def init_two_column_one_open_excel_pushbutton(self, shape):
        self.open_excel_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.open_excel_button.setGeometry(QtCore.QRect(*shape))
        self.open_excel_button.setObjectName("open_excel_button")
        self.open_excel_button.setText("打开excel")
        self.open_excel_button.setToolTip('打开excel进行编辑')
        self.open_excel_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

class ResizablePlainTextEdit(QtWidgets.QPlainTextEdit):
    # 定义一个信号，传递当前状态（收起或展开）给父窗口
    doubleClickedSignal = QtCore.pyqtSignal(object)
    def __init__(self, max_height, min_height, parent=None):
        super().__init__(parent)
        self.is_collapsed = False  # 用于记录当前状态（展开或收起）
        self.max_height = max_height
        self.min_height = min_height

    def mouseDoubleClickEvent(self, event):
        """处理双击事件，切换高度"""
        if self.is_collapsed:
            self.setFixedHeight(self.min_height)
            shift = -(self.max_height - self.min_height)
        else:
            self.setFixedHeight(self.max_height)
            shift = self.max_height - self.min_height
        self.is_collapsed = not self.is_collapsed
        # 发送信号，通知父窗口当前状态
        self.doubleClickedSignal.emit(int(shift))
        # 调用父类的双击事件处理（如果有需要）
        super().mouseDoubleClickEvent(event)

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
        paste_action = menu.addAction("粘贴")
        cut_action = menu.addAction("剪切")
        select_all_action = menu.addAction("全选")
        delete_action = menu.addAction("删除")
        menu.addSeparator()
        undo_action = menu.addAction("撤销")
        redo_action = menu.addAction("恢复")

        # 连接动作
        copy_action.triggered.connect(self.copy)
        paste_action.triggered.connect(self.paste)
        select_all_action.triggered.connect(self.selectAll)
        undo_action.triggered.connect(self.undo)
        redo_action.triggered.connect(self.redo)
        cut_action.triggered.connect(self.cut)
        delete_action.triggered.connect(self.delete_selected_text)

        # 显示菜单
        menu.exec(event.globalPos())

    def delete_selected_text(self):
        """
        删除选中的文本。
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()

class Row_Catch():
    def __init__(self,
                 centralwidget,
                 row_catch_shape: tuple,
                 max_height) -> None:
        self.centralwidget = centralwidget
        self.init_one_pic_name_lineedit(row_catch_shape, max_height)

    def init_one_pic_name_lineedit(self, shape, max_height):
        self.pic_name_lineedit = ResizablePlainTextEdit(max_height, shape[3], parent=self.centralwidget)
        self.pic_name_lineedit.setGeometry(QtCore.QRect(*shape))
        self.pic_name_lineedit.setObjectName("pic_name_lineedit8")
        self.pic_name_lineedit.setToolTip('当出现选择文本复制，但复制不全的时候，可以把所有文本复制到这里进行选取复制。')
        self.pic_name_lineedit.setPlaceholderText('文本暂存区,可随意复制,粘贴。双击展开/收起')
        self.pic_name_lineedit.setStyleSheet("""
            QPlainTextEdit {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: white;/* 背景颜色 */
            }
        """)