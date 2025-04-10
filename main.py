import sys, os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QApplication, QMessageBox
from my_utils.utils import get_config, get_internal_path
from windows.main_window import Main_Window
from my_utils.utils import delete_specific_files_and_folders
from windows.pic_operate_window import Pic_Operate_Windows
import traceback

class MainApp:
    def __init__(self, global_config, errors):
        self.global_config = global_config
        self.errors = errors
        self.flag_file = './flag_file'
        if os.path.exists(self.flag_file):
            self.global_config['enable_update'] = False
        self.main_window = Main_Window(self.open_pic_operate_window, self.global_config, self.flag_file)

    def open_pic_operate_window(self, file_path, mode):
        self.pic_operate = Pic_Operate_Windows(file_path, self.reopen_main_window, self.global_config, mode)

    def reopen_main_window(self):
        self.pic_operate = None
        self.main_window.show()

    def if_no_company_or_no_moban(self):
        if errors != []:
            if errors == ['no_company']:
                self.main_window.show_info.set_show_text('没有提供任何公司列表\n或未提供任何公司的模版信息\n添加公司列表和模版后重启软件。')
                self.main_window.show_info.show()
                self.main_window.setDisabled(True)
            elif errors == ['all']:
                self.main_window.show_info.set_show_text('所有公司都没有添加模版信息\n可添加模版信息后重启软件。')
                self.main_window.show_info.show()
                self.main_window.hide()
                self.main_window.setDisabled(True)
            else:
                show_text = ''
                for j in self.errors:
                    show_text += f'{j}\n'
                self.main_window.show_info.set_show_text(f'{show_text}这些公司没有添加模版信息\n现可操作已添加模版的公司\n如果要操作现未添加模版的公司\n先添加模版再重启软件')
                self.main_window.show_info.show()
        else:
            if os.path.exists(self.flag_file):
                os.remove(self.flag_file)
                now_version = self.global_config['version']
                self.main_window.show_info.set_show_text(f'软件更新完成！\n新版本为 version {now_version}\n可以选择手动删除上一个版本')
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
    
    # 打印到日志（可选）
    if not os.path.exists('配置'):
        os.makedirs('配置', exist_ok=True)
    with open("配置/error.log", "a") as error_log:
        error_log.write(error_details)
        error_log.write("\n")
    
    # 创建消息框
    msg_box = QMessageBox()
    msg_box.setWindowIcon(QIcon(get_internal_path('./files/icon/icon.ico')))
    msg_box.setWindowTitle("程序错误")
    msg_box.setText("程序发生了异常，请联系开发者！")
    msg_box.setDetailedText(error_details)  # 展示详细错误信息
    # 获取默认按钮并修改文本
    msg_box.addButton("关闭", QMessageBox.ButtonRole.ActionRole)
    # 设置按钮
    msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    global_config = get_config()
    if global_config['main_window_conf']['debug_mode'] == 'software':
        # 将全局异常处理器替换为自定义函数
        sys.excepthook = global_exception_handler
    delete_specific_files_and_folders('.', '__pycache__', '.DS_Store')
    companys = global_config['companys']
    result_path = '照片编辑结果'
    pic_path = '照片放这里/横向中间截图'
    gaopin_catch = './模版/高频照片'
    date_catch = './模版/缓存照片'
    errors = []
    at_lest_one_company = False
    if len(companys) != 0:
        for company in companys:
            if os.path.exists(f'{company}/模版'):
                at_lest_one_company = True
                os.chdir(company)
                os.makedirs(result_path, exist_ok=True)
                os.makedirs(pic_path, exist_ok=True)
                os.makedirs(gaopin_catch, exist_ok=True)
                os.makedirs(date_catch, exist_ok=True)
                os.chdir('..')
            else:
                errors.append(company)
    if len(errors) == 0:
        if not at_lest_one_company:
            errors = ['no_company']
    else:
        if at_lest_one_company:
            companys = list(set(companys) - set(errors))
            global_config['companys'] = companys
            global_config['company_name'] = companys[0]
            os.chdir(companys[0])
        else:
            errors = ['all']
    main_app = MainApp(global_config, errors)
    main_app.run()
    sys.exit(app.exec())
