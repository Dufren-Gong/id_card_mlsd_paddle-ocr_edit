import sys, os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QApplication, QMessageBox
from my_utils.utils import get_config, get_internal_path
from windows.main_window import Main_Window
from my_utils.utils import delete_specific_files_and_folders
from windows.pic_operate_window import Pic_Operate_Windows
import traceback

class MainApp:
    def __init__(self, global_config):
        self.global_config = global_config
        self.flag_file = './flag_file'
        if os.path.exists(self.flag_file):
            self.global_config['enable_update'] = False
        self.main_window = Main_Window(self.open_pic_operate_window, self.global_config, self.flag_file)

    def open_pic_operate_window(self, file_path, mode):
        self.pic_operate = Pic_Operate_Windows(file_path, self.reopen_main_window, self.global_config, mode)

    def reopen_main_window(self):
        self.pic_operate = None
        self.main_window.show()

    def run(self):
        self.main_window.show()
        if os.path.exists(self.flag_file):
            os.remove(self.flag_file)
            now_version = self.global_config['version']
            self.main_window.show_info.set_show_text(f'软件更新完成！\n新版本为 version {now_version}\n可以选择手动删除上一个版本')
            self.main_window.show_info.show()

# 全局异常捕获函数
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    捕获未处理的异常并显示在一个窗口中
    """
    # 将异常信息格式化为字符串
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # 打印到日志（可选）
    if not os.path.exists('./模版/配置和记录/'):
        os.makedirs('./模版/配置和记录/', exist_ok=True)
    with open("./模版/配置和记录/error.log", "a") as error_log:
        error_log.write(error_details)
        error_log.write("\n")
    
    # 创建消息框
    msg_box = QMessageBox()
    msg_box.setWindowIcon(QIcon(get_internal_path('./模版/files/icon/icon.ico')))
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
    result_path = '照片编辑结果'
    pic_path = '照片放这里'
    gaopin_catch = './模版/高频照片'
    date_catch = './模版/缓存照片'
    os.makedirs(result_path, exist_ok=True)
    os.makedirs(pic_path, exist_ok=True)
    os.makedirs(gaopin_catch, exist_ok=True)
    os.makedirs(date_catch, exist_ok=True)
    main_app = MainApp(global_config)
    main_app.run()
    sys.exit(app.exec())
