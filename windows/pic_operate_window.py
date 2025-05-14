import os, cv2
from PyQt6.QtWidgets import QApplication
from uis.photo_gallery_ui.cut_pic_ui import Cut_Pic
from my_utils.utils import get_data_str, get_all_pic_path, cv_imread, cv_imwrite
from uis.photo_gallery_ui.name_pic_ui import Name_Pic
from windows.show_info_window import Show_Info_Window
from send2trash import send2trash

class Pic_Operate_Windows():
    def __init__(self, file_path, reopen_main_window, global_config, mode=0):
        self.file_path = file_path
        self.pic_type = '.png'
        self.global_config = global_config
        self.id_shape = tuple(self.global_config['mlsd_conf']['pic_shape'])
        self.show_info = Show_Info_Window()
        self.reopen_main_window = reopen_main_window
        self.save_floader = os.path.join("照片编辑结果", get_data_str())
        self.cut_end_floader = '截图后'
        self.cut_save_floader = os.path.join(self.save_floader, self.cut_end_floader)
        os.makedirs(self.cut_save_floader, exist_ok=True)
        #0 for cut, 1 for ocr
        if mode == 0:
            self.get_cut_window()
        elif mode == 1:
            self.show_info.set_show_text('正在加载AI模型，并识别文字信息，请稍等......')
            self.show_info.row_one.exit_button.setText('好的')
            self.show_info.show()
            QApplication.processEvents()
            self.manage_pic()
            self.info_manage_window()

    def get_cut_window(self):
        self.show_info.set_show_text('正在加载AI模型，并识别截图区域，请稍等......')
        self.show_info.show()
        QApplication.processEvents()
        self.cut_pic_window = Cut_Pic(self.global_config, self.cut_save_floader, self.pic_type, self.id_shape, self.reopen_main_window, self.pre_next_step, self.show_info)
        self.cut_pic_window.load_photos(self.file_path)
        self.cut_pic_window.init_model_and_device()

    def pre_next_step(self):
        self.show_info.init_reopen_main(self.end_cut_step)
        self.show_info.row_one.exit_button.disconnect()
        self.show_info.row_one.exit_button.clicked.connect(self.next_step)
        self.show_info.set_show_text('继续识别照片文字点击右边继续按钮，只截图不识别照片文字的话关闭这个窗口就行了')
        self.show_info.row_one.exit_button.setText('继续')
        self.show_info.show()

    def next_step(self):
        self.show_info.init_reopen_main(None)
        self.show_info.row_one.exit_button.disconnect()
        self.show_info.init_events()
        self.file_path = self.cut_save_floader
        self.cut_pic_window = None
        self.show_info.set_show_text('正在加载AI模型，并识别文字信息，请稍等......')
        self.show_info.row_one.exit_button.setText('好的')
        self.show_info.show()
        QApplication.processEvents()
        self.info_manage_window()

    def end_cut_step(self):
        if os.path.exists(self.cut_save_floader):
            paths = os.listdir(self.cut_save_floader)
            for path in paths:
                os.rename(os.path.join(self.cut_save_floader, path), os.path.join(self.save_floader, path))
            send2trash(self.cut_save_floader)
        self.cut_pic_window = None
        self.reopen_main_window()

    def manage_pic(self):
        if isinstance(self.file_path, list):
            photo_paths = self.file_path
        else:
            photo_paths = get_all_pic_path(self.file_path)
        new_p = []
        for i in range(len(photo_paths)):
            img = cv_imread(photo_paths[i])
            img = cv2.resize(img, self.id_shape)
            cv_imwrite(img, self.pic_type, os.path.join(self.cut_save_floader, str(i) + self.pic_type))
            new_p.append(os.path.join(self.cut_save_floader, str(i) + self.pic_type))
        self.file_path = new_p

    def info_manage_window(self):
        self.name_pic_window = Name_Pic(self.global_config, os.path.dirname(self.cut_save_floader), self.pic_type, self.id_shape, self.reopen_main_window, self.show_info)
        self.name_pic_window.load_photos(self.file_path)
        self.name_pic_window.init_model_and_device()
