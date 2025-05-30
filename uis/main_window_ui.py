from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import copy

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

def merge_position(shape, position, shift = 1, gap = 2):
    shape_temp = copy.deepcopy(shape)
    if position == 'up':
        shape_temp = [shape_temp[0], shape_temp[1] - shift, shape_temp[2], int(shape_temp[3] / 2 + shift - gap / 2)]
    elif position == 'down':
        shape_temp = [shape_temp[0], int(shape_temp[1] + shape_temp[3] / 2 + gap / 2), shape_temp[2], int(shape_temp[3] / 2 + shift - gap / 2)]
    return shape_temp

class Row_Zero():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 file_types_combobox_shape: tuple,
                 replace_buttonz_shape: tuple,
                 exit_button_shape: tuple) -> None:
        self.centralwidget = centralwidget
        self.file_types = ["文件夹", "照片"]
        self.init_one_tip_label(tip_label_shape)
        self.init_one_column_two_select_file_file_type_combobox(file_types_combobox_shape)
        self.init_one_pic_name_lineedit(file_types_combobox_shape)
        self.init_two_column_three_replace_pushbutton(replace_buttonz_shape)
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
        self.file_type_combobox.setToolTip("添加的文件夹或压缩包包含照片为双数。添加的照片数量也必须是双数。")
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
        self.select_newest_checkbox.setText("默认最新编辑文件夹")
        # self.select_newest_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.select_newest_checkbox.setToolTip("默认选择最新编辑结果的文件夹，就不用再选择了，直接制作word，如果要选择其他文件夹，取消选中")
        self.select_newest_checkbox.hide()
        self.select_newest_checkbox.setChecked(True)
        self.select_newest_checkbox.setStyleSheet("QCheckBox { text-align: right; }")

    def init_two_column_three_replace_pushbutton(self, shape):
        self.replace_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.replace_button.setGeometry(QtCore.QRect(*shape))
        self.replace_button.setObjectName("replace_button")
        self.replace_button.setText("替换文本")
        self.replace_button.setToolTip('点击之后选择word,输入被替换文本和替换文本')
        self.replace_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

class Row_One():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 select_function_combobox_shape: tuple,
                 pic_here_shape: tuple,
                 enable_update) -> None:
        self.centralwidget = centralwidget
        self.enable_update = enable_update
        self.mode_options = ["截图识别", '文字识别', '查询信息', '合并信息到最新', "开单", "拿货", "转单", "年费", "补单", "补卡", "退单", "所有类型", "PDF转照片", '更新软件']
        self.init_one_tip_label(tip_label_shape)
        self.init_one_column_two_select_function_combobox(select_function_combobox_shape)
        self.init_one_pic_here_checkbox(pic_here_shape)
        self.init_outside_search_checkbox(pic_here_shape)
        self.init_open_floader_checkbox(pic_here_shape, 'up')
        self.init_open_text_checkbox(pic_here_shape, 'down')
        self.init_searched_checkbox(pic_here_shape)

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
            self.function_combobox.addItems(self.mode_options[:-1] + ['下载源码'])
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

    def init_one_pic_here_checkbox(self, shape):
        self.pic_here_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.pic_here_checkbox.setGeometry(QtCore.QRect(*shape))
        self.pic_here_checkbox.setObjectName("pic_here_checkbox")
        self.pic_here_checkbox.setText("选照片放这里")
        self.pic_here_checkbox.setToolTip("默认选择照片放这里文件夹，就不用再选择了，直接制作word，如果要选择其他文件夹，取消选中")
        self.pic_here_checkbox.setChecked(True)
        self.pic_here_checkbox.setStyleSheet("QCheckBox { text-align: right; }")

    def init_open_floader_checkbox(self, shape, position):
        self.open_floader_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        use_shape = merge_position(shape, position, shift=5)
        self.open_floader_checkbox.setGeometry(QtCore.QRect(*use_shape))
        self.open_floader_checkbox.setObjectName("open_floader_checkbox")
        self.open_floader_checkbox.setText("  打开文件夹")
        self.open_floader_checkbox.setToolTip("查找到照片的话是否打开文件夹")
        self.open_floader_checkbox.hide()
        self.open_floader_checkbox.setChecked(True)
        self.open_floader_checkbox.setStyleSheet("QCheckBox { text-align: left; }")

    def init_open_text_checkbox(self, shape, position):
        self.open_text_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        use_shape = merge_position(shape, position, shift=5)
        self.open_text_checkbox.setGeometry(QtCore.QRect(*use_shape))
        self.open_text_checkbox.setObjectName("open_text_checkbox")
        self.open_text_checkbox.setText("打开全部info")
        self.open_text_checkbox.setToolTip("查找到照片的话是否打开所有找到的.info文件,方便更改")
        self.open_text_checkbox.hide()
        self.open_text_checkbox.setChecked(True)
        self.open_text_checkbox.setStyleSheet("QCheckBox { text-align: left; }")

    def init_outside_search_checkbox(self, shape):
        self.outside_search_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.outside_search_checkbox.setGeometry(QtCore.QRect(*shape))
        self.outside_search_checkbox.setObjectName("outside_search_checkbox")
        self.outside_search_checkbox.setText("开启外部查找")
        self.outside_search_checkbox.hide()
        self.outside_search_checkbox.setToolTip("制作word的时候发现照片不存在,则在外部文件夹里查找照片,外部文件夹里照片可能比较多,照片找到的话会复制到'查找结果'文件夹里,将这个文件夹里的照片粗知道你想要的位置里")
        self.outside_search_checkbox.setChecked(False)
        self.outside_search_checkbox.setStyleSheet("QCheckBox { text-align: right; }")

    def init_searched_checkbox(self, shape):
        self.searched_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.searched_checkbox.setGeometry(QtCore.QRect(*shape))
        self.searched_checkbox.setObjectName("searched_checkbox")
        self.searched_checkbox.setText("查找到的照片")
        self.searched_checkbox.hide()
        self.searched_checkbox.setToolTip("默认选择合并'查找到的照片'文件夹里的照片到最新编辑结果里")
        self.searched_checkbox.setChecked(False)
        self.searched_checkbox.setStyleSheet("QCheckBox { text-align: right; }")

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
        self.select_files_button.setText("确认制作")
        self.select_files_button.setToolTip('默认使用照片放这里的照片来编辑')
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

class Select_Company():
    def __init__(self,
                 centralwidget,
                 companys,
                 tip_shape,
                 row_catch_shape: tuple,
                 config_shape) -> None:
        self.centralwidget = centralwidget
        self.companys = companys
        self.init_one_tip_label(tip_shape)
        self.init_one_company_name_lineedit(row_catch_shape)
        self.init_one_config_pushbutton(config_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tip_label.setObjectName("tip_label")
        self.tip_label.setText("选择公司:")
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_company_name_lineedit(self, shape):
        self.company_combobox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.company_combobox.setGeometry(QtCore.QRect(*shape))
        self.company_combobox.setObjectName("company_combobox")
        self.company_combobox.setToolTip("选择公司名称.")
        self.company_combobox.addItems(self.companys)
        self.company_combobox.setCurrentIndex(0)
        self.company_combobox.setStyleSheet("""
            QComboBox {
                border-width: 1px;
                border-style: solid;
                border-color: black;
                background-color: white;
                color: black;  /* 设置字体颜色为红色 */
            }
        """)

    def init_one_config_pushbutton(self, shape):
        self.confit_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.confit_button.setGeometry(QtCore.QRect(*shape))
        self.confit_button.setObjectName("confit_button")
        self.confit_button.setText("更改配置")
        self.confit_button.setToolTip('更改软件配置')
        self.confit_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)

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