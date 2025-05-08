from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QLabel, QCheckBox, QPushButton)
from PyQt6.QtGui import QDoubleValidator, QIntValidator, QIcon
from my_utils.utils import get_internal_path
import copy

class Set_Config_Window(QWidget):
    def __init__(self, global_config):
        super().__init__()
        self.global_config = copy.deepcopy(global_config)
        self.setWindowTitle("设置软件配置")
        self.setGeometry(100, 100, 320, 100)
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(1)

        self.line_one_layout = QHBoxLayout()
        self.pic_catch_days_tip = QLabel(self)
        self.pic_catch_days_tip.setText('照片缓存天数:')
        self.pic_catch_days_input = QLineEdit(str(self.global_config['catch_days']))
        self.pic_catch_days_input.setToolTip('0代表一直缓存,其他正数代表照片缓存天数，缓存照片在[./模版/excel备份]中')
        # 设置输入验证器，只允许输入正整数
        int_validator = QIntValidator(0, 1000000)  # 设置最小值为 1，最大值为 1000000
        self.pic_catch_days_input.setValidator(int_validator)
        self.pic_catch_days_input.setFixedWidth(60)

        self.excel_catch_num_tip = QLabel(self)
        self.excel_catch_num_tip.setText('excel缓存个数:')
        self.excel_catch_num_input = QLineEdit(str(self.global_config['excel_cache_num']))
        self.excel_catch_num_input.setToolTip('防止excel损坏丢失数据，每次制作word之前在[./模版/excel备份]中备份一定数量的excel.')
        # 设置输入验证器，只允许输入正整数
        int_validator = QIntValidator(0, 1000000)  # 设置最小值为 1，最大值为 1000000
        self.excel_catch_num_input.setValidator(int_validator)
        self.excel_catch_num_input.setFixedWidth(60)

        self.line_one_layout.addWidget(self.pic_catch_days_tip)
        self.line_one_layout.addWidget(self.pic_catch_days_input)
        self.line_one_layout.addWidget(self.excel_catch_num_tip)
        self.line_one_layout.addWidget(self.excel_catch_num_input)

        self.line_two_layout = QHBoxLayout()

        self.cup_prob_tip = QLabel(self)
        self.cup_prob_tip.setText('横着切割比例:')
        self.cup_prob_input = QLineEdit(str(self.global_config['cut_proportion']))
        self.cup_prob_input.setToolTip('从上到下的比例.')
        # 设置输入验证器，只允许输入正整数
        double_validator = QDoubleValidator()
        self.cup_prob_input.setValidator(double_validator)
        self.cup_prob_input.setFixedWidth(60)

        self.height_cup_prob_tip = QLabel(self)
        self.height_cup_prob_tip.setText('竖着切割比例:')
        self.height_cup_prob_input = QLineEdit(str(self.global_config['height_cut_proportion']))
        self.height_cup_prob_input.setToolTip('从左到右切割的比例.')
        # 设置输入验证器，只允许输入正整数
        double_validator = QDoubleValidator()
        self.height_cup_prob_input.setValidator(double_validator)
        self.height_cup_prob_input.setFixedWidth(60)

        self.line_two_layout.addWidget(self.cup_prob_tip)
        self.line_two_layout.addWidget(self.cup_prob_input)
        self.line_two_layout.addWidget(self.height_cup_prob_tip)
        self.line_two_layout.addWidget(self.height_cup_prob_input)

        self.line_three_layout = QHBoxLayout()
        self.enable_update_tip = QLabel(self)
        self.enable_update_tip.setText('更新开关:')
        self.enable_update_input = QCheckBox()
        if self.global_config['enable_update']:
            self.enable_update_input.setChecked(True)
        else:
            self.enable_update_input.setChecked(False)

        self.debug_mode_tip = QLabel(self)
        self.debug_mode_tip.setText('Debug模式:')
        self.debug_mode_input = QCheckBox()
        if self.global_config['main_window_conf']['debug_mode']:
            self.debug_mode_input.setChecked(True)
        else:
            self.debug_mode_input.setChecked(False)

        self.line_three_layout.addWidget(self.debug_mode_tip)
        self.line_three_layout.addWidget(self.debug_mode_input)
        self.line_three_layout.addWidget(self.enable_update_tip)
        self.line_three_layout.addWidget(self.enable_update_input)

        self.line_four_layout = QHBoxLayout()
        self.in_folader_tip = QLabel(self)
        self.in_folader_tip.setText('每单创建单独文件夹并复制照片:')
        self.in_folader_input = QCheckBox()
        if self.global_config['in_floader']:
            self.in_folader_input.setChecked(True)
        else:
            self.in_folader_input.setChecked(False)

        self.line_four_layout.addWidget(self.in_folader_tip)
        self.line_four_layout.addWidget(self.in_folader_input)

        self.line_five_layout = QHBoxLayout()
        self.forever_ensure_button = QPushButton('永久保存')
        self.forever_ensure_button.setToolTip('保存永久应用，写入到配置文件中.')
        self.forever_ensure_button.setFixedWidth(80)

        self.ensure_button = QPushButton('单次保存')
        self.ensure_button.setToolTip('保存只应用一次，下次打开恢复默认.')
        self.ensure_button.setFixedWidth(80)
        self.line_five_layout.addWidget(self.forever_ensure_button)
        self.line_five_layout.addWidget(self.ensure_button)

        # self.line_six_layout = QHBoxLayout()
        # self.add_company_label = QLabel('添加公司名称:')
        # self.add_company_label.setFixedWidth(80)

        # self.add_company_edit = QLineEdit()
        # self.add_company_edit.setPlaceholderText("新公司的名称,不要带'.',符合文件夹命名规则.")
        # self.line_six_layout.addWidget(self.add_company_label)
        # self.line_six_layout.addWidget(self.add_company_edit)

        # self.line_seven_layout = QHBoxLayout()
        # self.copy_company_label = QLabel('模版复制公司:')
        # self.copy_company_label.setFixedWidth(80)

        # self.copy_company_edit = QComboBox()
        # self.copy_company_label.setToolTip('添加的新公司的模版从哪个公司哪里复制.')
        # self.copy_company_edit.addItems(self.global_config['companys'])
        # self.copy_company_edit.setCurrentIndex(0)
        # self.line_seven_layout.addWidget(self.copy_company_label)
        # self.line_seven_layout.addWidget(self.copy_company_edit)

        # 将所有布局添加到主布局中
        self.main_layout.addLayout(self.line_two_layout)
        self.main_layout.addLayout(self.line_one_layout)
        # self.main_layout.addLayout(self.line_six_layout)
        # self.main_layout.addLayout(self.line_seven_layout)
        self.main_layout.addLayout(self.line_three_layout)
        self.main_layout.addLayout(self.line_four_layout)
        self.main_layout.addLayout(self.line_five_layout)
        self.setLayout(self.main_layout)
        self.init_events()

    def cache_day_change_config(self):
        a = self.pic_catch_days_input.text()
        if a:
            self.global_config['catch_days'] = int(eval(a))
        else:
            self.pic_catch_days_input.setText('0')

    def excel_num_change_config(self):
        a = self.excel_catch_num_input.text()
        if a:
            self.global_config['excel_cache_num'] = int(eval(a))
        else:
            self.excel_catch_num_input.setText('0')

    def cut_prob_change_config(self):
        num_str = self.cup_prob_input.text()
        if num_str:
            try:
                num_str = eval(self.cup_prob_input.text().lstrip('-').lstrip('0'))
                if num_str <= 0:
                    num_str = '0.'
                elif num_str >= 1:
                    num_str = '0.999'
                else:
                    num_str = str(num_str)
            except:
                num_str = '0.'
            self.cup_prob_input.setText(num_str)
            self.global_config['cut_proportion'] = eval(num_str)
        else:
            self.cup_prob_input.setText('0.')

    def height_cut_prob_change_config(self):
        num_str = self.cup_prob_input.text()
        if num_str:
            try:
                num_str = eval(self.cup_prob_input.text().lstrip('-').lstrip('0'))
                if num_str <= 0:
                    num_str = '0.'
                elif num_str >= 1:
                    num_str = '0.999'
                else:
                    num_str = str(num_str)
            except:
                num_str = '0.'
            self.cup_prob_input.setText(num_str)
            self.global_config['height_cut_proportion'] = eval(num_str)
        else:
            self.cup_prob_input.setText('0.')

    def in_folder_change_config(self):
        self.global_config['in_floader'] = self.in_folader_input.isChecked()

    def update_change_config(self):
        self.global_config['enable_update'] = self.enable_update_input.isChecked()

    def debug_change_config(self):
        self.global_config['main_window_conf']['debug_mode'] = self.debug_mode_input.isChecked()

    def init_events(self):
        self.pic_catch_days_input.textChanged.connect(self.cache_day_change_config)
        self.excel_catch_num_input.textChanged.connect(self.excel_num_change_config)
        self.cup_prob_input.textChanged.connect(self.cut_prob_change_config)
        self.height_cup_prob_input.textChanged.connect(self.height_cut_prob_change_config)
        self.in_folader_input.stateChanged.connect(self.in_folder_change_config)
        self.enable_update_input.stateChanged.connect(self.update_change_config)
        self.debug_mode_input.stateChanged.connect(self.debug_change_config)