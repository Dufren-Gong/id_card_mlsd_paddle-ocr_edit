import os, copy
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QPlainTextEdit)
from PyQt6.QtGui import QIcon, QDragEnterEvent, QRegularExpressionValidator
from PyQt6.QtCore import QFileInfo, Qt, QRegularExpression, QTimer
from my_utils.utils import get_internal_path, to_relative_paths
from windows.show_info_window import Show_Info_Window
from my_utils.operate_word import count_placeholder_occurrences, replace_text_with_same_format

class Replace_Select(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.setWindowTitle("只可处理.docx文件")
        self.setGeometry(100, 100, 500, 50)
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.show_info_window = Show_Info_Window()

        self.line_one_layout = QHBoxLayout()
        self.search_input_tip = QLabel(self)
        self.search_input_tip.setText('查询文本:')
        self.search_input_tip.setFixedWidth(60)
        self.search_input = QLineEdit()
        self.top_button = QPushButton('取消置顶')
        self.line_one_layout.addWidget(self.search_input_tip)
        self.line_one_layout.addWidget(self.search_input)
        self.line_one_layout.addWidget(self.top_button)

        self.line_two_layout = QHBoxLayout()
        self.replacement_tip = QLabel(self)
        self.replacement_tip.setText('替换文本:')
        self.replacement_tip.setFixedWidth(60)
        self.replacement_input = QLineEdit()
        self.replace_button = QPushButton('开始替换')
        self.line_two_layout.addWidget(self.replacement_tip)
        self.line_two_layout.addWidget(self.replacement_input)
        self.line_two_layout.addWidget(self.replace_button)

        self.line_three_layout = QHBoxLayout()
        self.delete_button = QPushButton('删除样本')
        self.delete_button.setToolTip('输入样本的序号然后删除')
        self.del_tip = QLabel(self)
        self.del_tip.setText('删除序号:')
        self.del_tip.setFixedWidth(60)
        self.delete_input = QLineEdit()
        regexp = QRegularExpression(r'[0-9,，]*')  # * 代表任意长度由这些字符组成的字符串
        validator = QRegularExpressionValidator(regexp)
        self.delete_input.setValidator(validator)
        self.delete_input.setPlaceholderText('如 1,3,5')
        self.line_three_layout.addWidget(self.del_tip)
        self.line_three_layout.addWidget(self.delete_input)
        self.line_three_layout.addWidget(self.delete_button)

        self.line_four_layout = QHBoxLayout()
        self.selected_label = QPlainTextEdit()
        self.selected_label.setReadOnly(True)
        self.selected_label.setFixedHeight(300)
        self.line_four_layout.addWidget(self.selected_label)
        # self.selected_label.setGeometry(QRect(*shape))

        # 将所有布局添加到主布局中
        self.main_layout.addLayout(self.line_one_layout)
        self.main_layout.addLayout(self.line_two_layout)
        self.main_layout.addLayout(self.line_three_layout)
        self.main_layout.addLayout(self.line_four_layout)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)  # 单次触发
        self.debounce_timer.timeout.connect(self.search_again)

        # 启用拖放
        self.setAcceptDrops(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.on_top = True
        self.setLayout(self.main_layout)
        self.init_events()

    def remove_stay_on_top_or_not(self):
        self.on_top = not self.on_top
        if self.on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            self.top_button.setText('取消置顶')
        else:
            # 取消总在最上方的标志
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.top_button.setText('置顶')
        self.show()  # 重新显示窗口以应用更改

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 只要拖拽内容包含 URL,就接受拖拽
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # 接受所有拖拽操作
        else:
            event.ignore()  # 如果没有 URL,忽略拖拽

    def dropEvent(self, event):
        length_before = len(self.file_paths)
        # 获取拖拽的所有文件或文件夹路径
        urls = event.mimeData().urls()
        if urls:
            for index_t, url in enumerate(urls):
                local_path = url.toLocalFile()  # 获取本地路径
                if local_path:
                    file_info = QFileInfo(local_path)
                    if file_info.isFile():  # 如果是文件
                        # 检查文件扩展名
                        file_extension = file_info.suffix().lower()  # 获取文件后缀,并转为小写
                        if file_extension in ['docx']:
                            t = to_relative_paths([local_path], os.getcwd())
                            if t[0] not in self.file_paths:  # 如果文件不在已添加的列表中
                                self.file_paths.extend(t)
                    elif file_info.isDir():  # 如果是文件夹
                        file_paths = []
                        # 遍历文件夹及子文件夹
                        for root, _, files in os.walk(local_path):
                            for file in files:
                                file_info = QFileInfo(file)
                                file_extension = file_info.suffix().lower()  # 获取文件后缀,并转为小写
                                # 获取完整的文件路径
                                if file != '.DS_Store' and file_extension in ['docx']:
                                    file_paths.extend(to_relative_paths([os.path.join(root, file)], os.getcwd()))
                        for j in file_paths:
                            if j not in self.file_paths:
                                self.file_paths.extend(file_paths)
        length_after = len(self.file_paths)
        if length_after != length_before:
            search_text = self.search_input.text()
            for i in range(length_before, length_after):
                show_strs = f'({i+1}){self.file_paths[i]}'
                if search_text != '':
                    try:
                        count = count_placeholder_occurrences(self.file_paths[i], search_text)
                    except:
                        count = -1
                    if count >= 0:
                        show_strs += f'    有{count}处'
                    else:
                        show_strs += '不存在或打不开'
                self.selected_label.appendPlainText(show_strs)

    def replace_all_text(self):
        if self.file_paths == []:
            self.show_info_window.set_show_text('你还未添加文件,请先拖拽添加文件。')
            self.show_info_window.show()
            return
        if not self.search_input.text() or not self.replacement_input.text():
            self.show_info_window.set_show_text('请先填写查询文本和替换文本，再替换。')
            self.show_info_window.show()
            return
        passed_word = {}
        for i in self.file_paths:
            try:
                doc, count = replace_text_with_same_format(i, self.search_input.text(), self.replacement_input.text())
                doc.save(i)
                base = os.path.basename(i)
                if base in passed_word.keys():
                    info = base.rsplit('.')
                    count_t = 1
                    while f'{info[0]}_{count_t}.{info[1]}' in passed_word.keys():
                        count_t += 1
                    passed_word[f'{info[0]}_{count_t}.{info[1]}'] = count
                else:
                    passed_word[i] = count
            except:
                pass
        self.show_info_window.set_show_text('操作成功!')
        self.show_info_window.show()

    def search_again(self):
        self.selected_label.clear()
        now_text = self.search_input.text()
        for i in range(len(self.file_paths)):
            show_strs = f'({i+1}){self.file_paths[i]}'
            if now_text != '':
                try:
                    count = count_placeholder_occurrences(self.file_paths[i], now_text)
                except:
                    count = -1
                if count >= 0:
                    show_strs += f'    有{count}处'
                else:
                    show_strs += '不存在或打不开'
            self.selected_label.appendPlainText(show_strs)

    def del_some(self):
        if self.file_paths == []:
            self.show_info_window.set_show_text('你还未添加文件,请先拖拽添加文件。')
            self.show_info_window.show()
            return
        del_text = self.delete_input.text().strip().replace('，', ',')
        if del_text == '':
            self.show_info_window.set_show_text('请先在左侧文本框输入要删除的样本序号。')
            self.show_info_window.show()
            return
        del_arr_all = del_text.split(',')
        if all(s.isdigit() for s in del_arr_all):
            del_arr = [int(i) - 1 for i in del_arr_all if int(i) <= len(self.file_paths) and int(i) > 0]
            if len(del_arr_all) != len(del_arr):
                num_del = sorted([i+1 for i in del_arr])
                self.delete_input.setText(','.join([str(i) for i in num_del]))
            now_text = self.selected_label.toPlainText().split('\n')
            check_text = copy.deepcopy(now_text)
            chech_file_paths = copy.deepcopy(self.file_paths)
            for i in del_arr:
                check_text.remove(now_text[i])
                chech_file_paths.remove(self.file_paths[i])
            self.file_paths = chech_file_paths
            check_text = [f'({i+1})' + j.split(')', maxsplit = 1)[-1] for i,j in enumerate(check_text)]
            self.selected_label.setPlainText('\n'.join(check_text))

    def on_text_changed(self):
        # 每次文本变化，重启定时器
        self.debounce_timer.start(1000)  # 1000毫秒 = 1秒

    def init_events(self):
        self.replace_button.clicked.connect(self.replace_all_text)
        self.search_input.textChanged.connect(self.on_text_changed)
        self.delete_button.clicked.connect(self.del_some)
        self.top_button.clicked.connect(self.remove_stay_on_top_or_not)