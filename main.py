import sys, os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QApplication, QMessageBox
from my_utils.utils import get_config, get_internal_path
from windows.main_window import Main_Window
from my_utils.utils import delete_specific_files_and_folders
from windows.pic_operate_window import Pic_Operate_Windows
import traceback

class MainApp:
    def __init__(self, global_config, errors, default_excepthook):
        self.global_config = global_config
        self.default_excepthook = default_excepthook
        self.errors = errors
        self.main_window = Main_Window(self.open_pic_operate_window, self.refresh_main_window, self.global_config)

    def open_pic_operate_window(self, file_path, mode):
        self.pic_operate = Pic_Operate_Windows(file_path, self.reopen_main_window, self.global_config, mode)

    def reopen_main_window(self):
        self.pic_operate = None
        self.main_window.show()

    def refresh_main_window(self, global_config):
        self.pic_operate = None
        self.main_window.close()
        companys = global_config['companys']
        global_config['companys'] = companys
        global_config['company_name'] = companys[0]
        os.chdir(f'../{companys[0]}')
        self.main_window = Main_Window(self.open_pic_operate_window, self.refresh_main_window, global_config)
        self.main_window.show()
        if not global_config['main_window_conf']['debug_mode']:
            # 将全局异常处理器替换为自定义函数
            sys.excepthook = global_exception_handler
        else:
            sys.excepthook = self.default_excepthook

    def error_hide_mainwindow(self, tip):
        self.main_window.show_info.set_show_text(tip)
        self.main_window.show_info.row_one.exit_button.hide()
        self.main_window.show_info.row_one.tip_label.setFixedSize(self.main_window.show_info.width() - 2 * self.main_window.show_info.shape.round_gap, self.main_window.show_info.row_one.tip_label.height())
        self.main_window.show_info.show()
        self.main_window.hide()
        self.main_window.setDisabled(True)

    def if_no_company_or_no_moban(self):
        if errors != []:
            if errors == ['no_company']:
                self.error_hide_mainwindow('没有提供任何公司列表\n请检查\n添加公司列表和模版后重启软件。')
            elif errors == ['all']:
                self.error_hide_mainwindow('所有公司都没有添加模版信息\n需添加模版信息后重启软件。')
            else:
                show_text = ''
                for j in self.errors:
                    show_text += f'{j}\n'
                self.main_window.show_info.set_show_text(f'{show_text}这些公司没有添加模版信息\n现可操作已添加模版的公司\n如果要操作现未添加模版的公司\n先添加模版再重启软件')
                self.main_window.show_info.show()

    def run(self):
        self.main_window.show()
        self.if_no_company_or_no_moban()


# 全局异常捕获函数
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    捕获未处理的异常并显示在一个窗口中
    """
    # 将异常信息格式化为字符串
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # 打印到日志（可选
    with open("模版/error.log", "a") as error_log:
        error_log.write(error_details)
        error_log.write("\n")
    
    # 创建消息框
    msg_box = QMessageBox()
    msg_box.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
    msg_box.setWindowTitle("程序错误")
    msg_box.setText("程序发生了异常，请联系开发者！")
    msg_box.setDetailedText(error_details)  # 展示详细错误信息
    # 获取默认按钮并修改文本
    msg_box.addButton("关闭", QMessageBox.ButtonRole.ActionRole)
    # 设置按钮
    msg_box.exec()

if __name__ == "__main__":
    global_config = get_config()
    app = QApplication(sys.argv)
    # 保存默认的异常处理程序
    default_excepthook = sys.excepthook
    if not global_config['main_window_conf']['debug_mode']:
        # 将全局异常处理器替换为自定义函数
        sys.excepthook = global_exception_handler
    delete_specific_files_and_folders('.', '__pycache__', '.DS_Store')
    companys = global_config['companys']
    result_path = '照片编辑结果'
    pic_path = '照片放这里/横着中间截图'
    height_pic_path = '照片放这里/竖着中间截图'
    gaopin_catch = './模版/高频照片'
    date_catch = './模版/缓存照片'
    excel_beifen = './模版/excel备份'
    errors = []
    at_lest_one_company = False
    if len(companys) != 0:
        for company in companys:
            if os.path.exists(f'{company}/模版'):
                at_lest_one_company = True
            else:
                os.makedirs(f'{company}/模版', exist_ok=True)
                errors.append(company)
            os.chdir(company)
            os.makedirs(result_path, exist_ok=True)
            os.makedirs(pic_path, exist_ok=True)
            os.makedirs(height_pic_path, exist_ok=True)
            os.makedirs(gaopin_catch, exist_ok=True)
            if global_config['catch_days'] > 0:
                os.makedirs(date_catch, exist_ok=True)
            if global_config['excel_cache_num'] > 0:
                os.makedirs(excel_beifen, exist_ok=True)
            os.chdir('..')
    if len(errors) == 0:
        if not at_lest_one_company:
            errors = ['no_company']
        else:
            global_config['companys'] = companys
            global_config['company_name'] = companys[0]
            os.chdir(companys[0])
    else:
        if at_lest_one_company:
            companys = list(set(companys) - set(errors))
            global_config['companys'] = companys
            global_config['company_name'] = companys[0]
            os.chdir(companys[0])
        else:
            errors = ['all']
    main_app = MainApp(global_config, errors, default_excepthook)
    main_app.run()
    sys.exit(app.exec())