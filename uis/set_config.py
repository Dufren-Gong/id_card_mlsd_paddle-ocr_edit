from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QLabel, QCheckBox, QPushButton, QFileDialog)
from PyQt6.QtGui import QDoubleValidator, QIntValidator, QIcon, QValidator
from my_utils.utils import get_internal_path
import copy

class NoDotValidator(QValidator):
    def validate(self, input_str, pos):
        if input_str:
            first = input_str[0]
            if '.' in input_str or '  ' in input_str or first in [' ', '_']:
                return (QValidator.State.Invalid, input_str, pos)
        return (QValidator.State.Acceptable, input_str, pos)

class Set_Config_Window(QWidget):
    def __init__(self, global_config):
        super().__init__()
        self.global_config = copy.deepcopy(global_config)
        self.setWindowTitle("配置软件")
        self.setGeometry(100, 100, 320, 100)
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        self.main_layout = QVBoxLayout()
        # self.main_layout.setSpacing(1)

        self.line_one_layout = QHBoxLayout()
        self.pic_catch_days_tip = QLabel(self)
        self.pic_catch_days_tip.setText('照片缓存天数:')
        self.pic_catch_days_input = QLineEdit(str(self.global_config['catch_days']))
        self.pic_catch_days_input.setToolTip('0代表一直缓存,其他正数代表照片缓存天数,缓存照片在[./模版/excel备份]中')
        # 设置输入验证器,只允许输入正整数
        int_validator = QIntValidator(0, 1000000)  # 设置最小值为 1,最大值为 1000000
        self.pic_catch_days_input.setValidator(int_validator)
        self.pic_catch_days_input.setFixedWidth(60)

        self.excel_catch_num_tip = QLabel(self)
        self.excel_catch_num_tip.setText('excel缓存个数:')
        self.excel_catch_num_input = QLineEdit(str(self.global_config['excel_cache_num']))
        self.excel_catch_num_input.setToolTip('防止excel损坏丢失数据,每次制作word之前在[./模版/excel备份]中备份一定数量的excel.')
        # 设置输入验证器,只允许输入正整数
        int_validator = QIntValidator(0, 1000000)  # 设置最小值为 1,最大值为 1000000
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
        # 设置输入验证器,只允许输入正整数
        double_validator = QDoubleValidator()
        self.cup_prob_input.setValidator(double_validator)
        self.cup_prob_input.setFixedWidth(60)

        self.height_cup_prob_tip = QLabel(self)
        self.height_cup_prob_tip.setText('竖着切割比例:')
        self.height_cup_prob_input = QLineEdit(str(self.global_config['height_cut_proportion']))
        self.height_cup_prob_input.setToolTip('从左到右切割的比例.')
        # 设置输入验证器,只允许输入正整数
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

        self.mandatory_update_tip = QLabel(self)
        self.mandatory_update_tip.setText('强制更新:')
        self.mandatory_update_tip.setToolTip('版本号相同,强制更新')
        self.mandatory_update_input = QCheckBox()
        if self.global_config['mandatory_update']:
            self.mandatory_update_input.setChecked(True)
        else:
            self.mandatory_update_input.setChecked(False)

        self.update_window_tip = QLabel(self)
        self.update_window_tip.setText('更新显示窗口:')
        self.update_window_tip.setToolTip('更新的时候是否打开黑色窗口显示更新进度')
        self.update_window_input = QCheckBox()
        if self.global_config['update_window']:
            self.update_window_input.setChecked(True)
        else:
            self.update_window_input.setChecked(False)

        self.line_three_layout.addWidget(self.enable_update_tip)
        self.line_three_layout.addWidget(self.enable_update_input)
        self.line_three_layout.addWidget(self.mandatory_update_tip)
        self.line_three_layout.addWidget(self.mandatory_update_input)
        self.line_three_layout.addWidget(self.update_window_tip)
        self.line_three_layout.addWidget(self.update_window_input)

        self.line_four_layout = QHBoxLayout()

        self.update_save_mode_tip = QLabel(self)
        self.update_save_mode_tip.setText('更新缓存:')
        self.update_save_mode_tip.setToolTip('更新之后,保留上一个版本软件内公司信息以保证上一个版本功能正常还是删除上一个版本公司信息以节省空间')
        self.update_save_mode_input = QCheckBox()
        if self.global_config['stay_old']:
            self.update_save_mode_input.setChecked(True)
        else:
            self.update_save_mode_input.setChecked(False)

        self.in_folader_tip = QLabel(self)
        self.in_folader_tip.setText('缓存信息和照片:')
        self.in_folader_tip.setToolTip('每单的照片和信息以及制作的word放到单独的文件夹里,方便保存')
        self.in_folader_input = QCheckBox()
        if self.global_config['in_floader']:
            self.in_folader_input.setChecked(True)
        else:
            self.in_folader_input.setChecked(False)

        self.debug_mode_tip = QLabel(self)
        self.debug_mode_tip.setText('Debug模式:')
        self.debug_mode_input = QCheckBox()
        if self.global_config['main_window_conf']['debug_mode']:
            self.debug_mode_input.setChecked(True)
        else:
            self.debug_mode_input.setChecked(False)

        self.line_four_layout.addWidget(self.update_save_mode_tip)
        self.line_four_layout.addWidget(self.update_save_mode_input)
        self.line_four_layout.addWidget(self.in_folader_tip)
        self.line_four_layout.addWidget(self.in_folader_input)
        self.line_four_layout.addWidget(self.debug_mode_tip)
        self.line_four_layout.addWidget(self.debug_mode_input)

        self.line_five_layout = QHBoxLayout()
        self.change_outside_floader_button = QPushButton('更改外部查找文件夹路径')
        self.change_outside_floader_button.setToolTip('更改外部查找文件夹路径,在高频和缓存里都找不到照片的话,会在这个文件夹自动查找所有缺失照片并且归总到一个文件夹里.')
        self.change_outside_floader_button.setFixedWidth(150)

        self.forever_ensure_button = QPushButton('永久保存')
        self.forever_ensure_button.setToolTip('保存永久应用,写入到配置文件中.')
        self.forever_ensure_button.setFixedWidth(60)

        self.ensure_button = QPushButton('单次保存')
        self.ensure_button.setToolTip('保存只应用一次,下次打开恢复默认.')
        self.ensure_button.setFixedWidth(60)
        self.line_five_layout.addWidget(self.change_outside_floader_button)
        self.line_five_layout.addWidget(self.forever_ensure_button)
        self.line_five_layout.addWidget(self.ensure_button)

        self.line_six_layout = QHBoxLayout()
        self.add_company_label = QLabel('添加公司名称:')
        self.add_company_label.setFixedWidth(80)

        self.add_company_edit = QLineEdit()
        validator = NoDotValidator()
        self.add_company_edit.setValidator(validator)
        self.add_company_edit.setPlaceholderText("新公司名,需符合文件夹命名规则")
        self.line_six_layout.addWidget(self.add_company_label)
        self.line_six_layout.addWidget(self.add_company_edit)

        self.line_seven_layout = QHBoxLayout()
        self.copy_company_label = QLabel('模版复制公司:')
        self.copy_company_label.setFixedWidth(80)

        self.copy_company_edit = QComboBox()
        self.copy_company_label.setToolTip('添加的新公司的模版从哪个公司哪里复制.')
        self.copy_company_edit.addItems(self.global_config['companys'])
        self.copy_company_edit.setCurrentIndex(0)
        self.line_seven_layout.addWidget(self.copy_company_label)
        self.line_seven_layout.addWidget(self.copy_company_edit)

        # 将所有布局添加到主布局中
        self.main_layout.addLayout(self.line_two_layout)
        self.main_layout.addLayout(self.line_one_layout)
        self.main_layout.addLayout(self.line_six_layout)
        self.main_layout.addLayout(self.line_seven_layout)
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

    def mandatory_update_change_config(self):
        self.global_config['mandatory_update'] = self.mandatory_update_input.isChecked()

    def update_window_change_config(self):
        self.global_config['update_window'] = self.update_window_input.isChecked()

    def update_save_change_config(self):
        self.global_config['stay_old'] = self.update_save_mode_input.isChecked()

    def change_outside_floader(self):
        self.global_config['outside_search_path'] = QFileDialog.getExistingDirectory(self, "选择外部搜索文件夹")

    def init_events(self):
        self.pic_catch_days_input.textChanged.connect(self.cache_day_change_config)
        self.excel_catch_num_input.textChanged.connect(self.excel_num_change_config)
        self.cup_prob_input.textChanged.connect(self.cut_prob_change_config)
        self.height_cup_prob_input.textChanged.connect(self.height_cut_prob_change_config)
        self.in_folader_input.stateChanged.connect(self.in_folder_change_config)
        self.enable_update_input.stateChanged.connect(self.update_change_config)
        self.debug_mode_input.stateChanged.connect(self.debug_change_config)
        self.mandatory_update_input.stateChanged.connect(self.mandatory_update_change_config)
        self.update_window_input.stateChanged.connect(self.update_window_change_config)
        self.update_save_mode_input.stateChanged.connect(self.update_save_change_config)
        self.change_outside_floader_button.clicked.connect(self.change_outside_floader)