import os, shutil, copy, re
from PyQt6.QtWidgets import QMainWindow, QWidget, QFileDialog, QApplication
from uis.shapes import Ui_Shapes
from docx import Document
from my_utils.utils import delete_specific_files_and_folders
from uis.main_window_ui import Row_Zero, Row_One, Row_Two, Select_Company, Row_Catch
from windows.show_info_window import Show_Info_Window
from uis.set_config import Set_Config_Window
from my_utils.threads import Pdf_to_Pic_Thread, Download_Sourcecode, Download_Copy_Large
from my_utils.utils import get_data_str, open_floader, find_in_catch_pic, get_internal_path, get_config, download_single_file, split_image, write_config, recursive_update
from my_utils import operate_excel as utils_operate_excel
from each_types import kaidan, nahuo, zhuandan, budan, nianfei, buka, tuidan
from PyQt6.QtGui import QIcon#, QDragEnterEvent
from PyQt6.QtCore import QThreadPool, QTimer#, QFileInfo
from my_utils.operate_word import copy_template, replace_text_with_same_format, replace_pic, append_fullpage_image_center, concat_two_words, is_word_empty
from natsort import natsorted
from concurrent.futures import ThreadPoolExecutor, as_completed
from my_utils.Traditional_to_Simplified_Chinese import fan_to_jian
import subprocess, platform
from send2trash import send2trash
from uis.replace_select import Replace_Select
import pandas as pd
        
class Main_Window(QMainWindow):
    def __init__(self, open_pic_operate_window, refresh_main_window, global_config):
        super().__init__()
        self.show_info = Show_Info_Window()
        self.refresh_main_window = refresh_main_window
        self.Thread_pdf_to_pic = None
        self.global_config = global_config
        self.formates = ['jpg', 'jpeg', 'png', 'info']
        self.have_error_flag = False
        self.pic_scale = 0.378
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(1)
        self.open_pic_operate_window = open_pic_operate_window
        self.select_file_flag = False
        self.shape = Ui_Shapes(round_gap=10)
        self.concat_index = 3
        self.pdf_to_pic_count = 0
        self.add_front_path = '../配置/pics/前面.docx'
        self.add_back_path = '../配置/pics/后面.docx'
        self.front_doc = None
        self.back_doc = None
        self.pdf_to_pic_finished = 0
        # 启用拖放
        # self.setAcceptDrops(True)
        self.shape.layout([self.shape.combobox_height, self.shape.combobox_height, self.shape.button_height, self.shape.combobox_height, 27],
                          [[60, 170, 60]] + [[60, 135, 95]] + [[60, 71, 60, 95]] + [[60, 135, 95]] + [[298]])
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        self.init_ui()
        self.init_events()
        self.row_one.open_floader_checkbox.setChecked(self.global_config['open_search_floader'])
        self.row_one.open_text_checkbox.setChecked(self.global_config['open_search_info'])

    # def dragEnterEvent(self, event: QDragEnterEvent):
    #     # 只要拖拽内容包含 URL,就接受拖拽
    #     if self.row_one.function_combobox.currentIndex() != 2:
    #         if event.mimeData().hasUrls():
    #             event.acceptProposedAction()  # 接受所有拖拽操作
    #         else:
    #             event.ignore()  # 如果没有 URL,忽略拖拽
    #     else:
    #         event.ignore()

    # def dropEvent(self, event):
    #     index = self.row_one.function_combobox.currentIndex()
    #     pic_check_index = [0, 1]
    #     # floader_check_index = [3, 4, 5, 6, 7, 8, 9, 10]
    #     no_event_arr = [2, 12, 13]
    #     # 获取拖拽的所有文件或文件夹路径
    #     urls = event.mimeData().urls()
    #     if urls:
    #         for index_t, url in enumerate(urls):
    #             local_path = url.toLocalFile()  # 获取本地路径
    #             if local_path:
    #                 file_info = QFileInfo(local_path)
    #                 if file_info.isFile():  # 如果是文件
    #                     # 检查文件扩展名
    #                     file_extension = file_info.suffix().lower()  # 获取文件后缀,并转为小写
    #                     if index != 13 and index != 12:
    #                         if file_extension in self.formates[:-1]:
    #                             shutil.copy(local_path, os.path.join('./照片放这里', get_data_str() + f'_{index_t}.' + file_extension))
    #                     elif index == 12:
    #                         if file_extension == 'pdf':
    #                             self.pdf_to_pic_count += 1
    #                             self.open_folder_dialog(local_path)
    #                     elif index == 13:
    #                         if file_extension == 'zip':
    #                             shutil.move(local_path, '.')
    #                         else:
    #                             self.show_info.set_show_text('该功能拖拽只接受后缀为zip类型的压缩包')
    #                             self.show_info.show_window()
    #                 elif file_info.isDir():  # 如果是文件夹
    #                     if index not in no_event_arr:
    #                         if not (self.row_zero.file_type_combobox.currentIndex() == 1 and index in pic_check_index):
    #                             self.open_folder_dialog(local_path)
    #                         break

    def closeEvent(self, event):
        if self.thread_pool is not None:
            self.thread_pool.clear()
        delete_specific_files_and_folders('.', '__pycache__', '.DS_Store')
        self.deleteLater()
        self.close()

    def concat_all(self, path_t, files):
        flag = False
        items = os.listdir(path_t)
        if len(items) != 0:
            # 过滤出文件夹的名称
            directories = natsorted([item for item in items if os.path.isdir(os.path.join(path_t, item))])
            source_dir = self.folder_path
            destination_dir = os.path.join(path_t, directories[-1])
            if source_dir != destination_dir:
                # 获取源目录中的所有条目
                for item in files:
                    # 构造完整的文件路径
                    source_item_path = os.path.join(source_dir, item)
                    
                    # 目标文件路径
                    destination_item_path = os.path.join(destination_dir, item)

                    # 检查该条目是否为文件
                    if os.path.isfile(source_item_path):
                        # 检查目标目录是否已经存在同名文件
                        if not os.path.exists(destination_item_path):
                            # 复制文件到目标目录
                            shutil.copy(source_item_path, destination_item_path)
                            flag = True
        return flag

    def open_folder_dialog(self, floader_path = None):
        selected_options = self.row_one.function_combobox.currentIndex()
        if selected_options != 12:
            # 打开文件夹选择对话框
            if selected_options == 0 or selected_options == 1:
                if self.row_zero.file_type_combobox.currentIndex() == 0:
                    if floader_path == None:
                        self.folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
                    else:
                        self.folder_path = floader_path
                    if self.folder_path:
                        folder_path_pic = os.listdir(self.folder_path)
                        self.folder_path = [os.path.join(self.folder_path, i) for i in folder_path_pic if i.rsplit('.', maxsplit=1)[-1] in self.formates[:-1]]
                        if len(self.folder_path) == 0:
                            self.folder_path = None
                elif self.row_zero.file_type_combobox.currentIndex() == 1:
                    self.folder_path, _ = QFileDialog.getOpenFileNames(self, '选择照片文件', '',
                                                                        '图像文件 (*.jpg *.jpeg *.png);;所有文件 (*)')
                if self.folder_path != '' and self.folder_path != []:
                    if self.folder_path == None:
                        self.select_file_flag = False
                        self.show_info.set_show_text('所选文件夹内无照片')
                        self.show_info.show_window()
                    elif len(self.folder_path) % 2 != 0:
                        self.select_file_flag = False
                        self.show_info.set_show_text('照片数量为单数,必须为双数')
                        self.show_info.show_window()
                    else:
                        self.select_file_flag = True
            else:
                if selected_options == self.concat_index and self.row_one.searched_checkbox.isChecked():
                    if os.path.exists('./查找到的照片'):
                        self.folder_path = './查找到的照片'
                    else:
                        self.show_info.set_show_text('你选择了合并查找到的照片选项，但是没有”查找到的照片“文件夹，请先查找照片，或者取消勾选合并查找到的照片选项')
                        self.show_info.show()
                        return
                else:
                    if floader_path == None:
                        self.folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
                    else:
                        self.folder_path = floader_path
                if self.folder_path:  # 检查是否选择了文件夹
                    files = os.listdir(self.folder_path)
                    if ".DS_Store" in files:
                        files.remove('.DS_Store')
                    if selected_options == self.concat_index:
                        files = [i for i in files if i.rsplit('.', maxsplit = 1)[-1] in self.formates]
                        if len(files) == 0:
                            self.show_info.set_show_text('所选文件夹无可合并信息!检查是否全是同名文件或者选择了合并到同一个文件')
                        else:
                            if self.concat_all('照片编辑结果', files):
                                self.show_info.set_show_text('合并文件夹照片成功,但不包含文件夹和同名文件')
                            else:
                                self.show_info.set_show_text('还未操作过照片,请先操作照片.')
                        self.show_info.show_window()
                    else:
                        self.excel_name = '非身份证信息需求.xlsx'
                        if not os.path.exists(os.path.join('模版', self.excel_name)):
                            self.show_info.set_show_text(f'缺少"{self.excel_name}"文件')
                            self.show_info.show_window()
                        else:
                            if selected_options != 11:
                                self.show_info.set_show_text('正在制作中,请稍后!')
                                self.show_info.show_window()
                                QApplication.processEvents()
                                if selected_options == 4:
                                    self.make_singe('开单')
                                elif selected_options == 5:
                                    self.make_singe('拿货')
                                elif selected_options == 6:
                                    self.make_singe('转单')
                                elif selected_options == 7:
                                    self.make_singe('年费')
                                elif selected_options == 8:
                                    self.make_singe('补单')
                                elif selected_options == 9:
                                    self.make_singe('补卡')
                                elif selected_options == 10:
                                    self.make_singe('退单')
                                if not self.have_error_flag:
                                    duration = self.global_config['show_tip_timer_duration']
                                    if duration > 0:
                                        self.show_info.set_show_text('制作完成!')
                                        self.show_info.show_window()
                                        self.combbox_change_tips_timer.start(duration) 
                            else:
                                self.show_info.row_one.exit_button.disconnect()
                                self.show_info.row_one.exit_button.clicked.connect(self.start_processing)
                                self.show_info.set_show_text('同时制作所有类型需用多线程对excel进行读写,可能导致excel损坏,若损坏,在{模版/excel备份}内有备份,替换excel后重新逐步制作.点击好的开始制作.')
                                self.show_info.show_window()
                else:
                    self.select_file_flag = False
        else:
            if floader_path == None:
                self.folder_path, _ = QFileDialog.getOpenFileName(self, '选择pdf文件', '', 'Pdf Files (*.pdf);;All Files (*)')
            else:
                self.folder_path = floader_path
            self.select_file_flag = True
        if self.select_file_flag and ((isinstance(self.folder_path, list) and len(self.folder_path) != 0) or (isinstance(self.folder_path, str) and self.folder_path)):
            if selected_options == 0 or selected_options == 1:
                self.hide()
                self.open_pic_operate_window(natsorted(self.folder_path), selected_options)
            elif selected_options == 12:
                if floader_path == None:
                    self.pdf_to_pic_count += 1
                if self.pdf_to_pic_finished == 0:
                    self.row_two.select_files_button.setDisabled(True)
                    self.show_info.set_show_text('可能需要一些时间,请等待')
                    self.show_info.show_window()
                    QApplication.processEvents()
                save_path = os.path.join('./照片编辑结果', get_data_str())
                os.makedirs(save_path, exist_ok=True)
                self.Thread_pdf_to_pic = Pdf_to_Pic_Thread(self.folder_path, save_path, 'png')
                self.Thread_pdf_to_pic.signals.finished.connect(self.end_pdf_to_pic)  # 把任务完成的信号与任务完成后处理的槽函数绑定
                self.thread_pool.start(self.Thread_pdf_to_pic)
        self.have_error_flag = False
        self.select_file_flag = False

    def cache_excel(self, excel_path, cache_floader):
        cache_excels = os.listdir(cache_floader)
        cache_excels = natsorted([i for i in cache_excels if os.path.isfile(os.path.join(cache_floader, i))], reverse=True)
        if len(cache_excels) >= self.global_config['excel_cache_num']:
            dels = cache_excels[self.global_config['excel_cache_num'] - 1:]
            for i in dels:
                send2trash(os.path.join(cache_floader, i))
        save_name = os.path.join(cache_floader, get_data_str() + '.xlsx')
        shutil.copy(excel_path, save_name)

    def outside_floader_exsit(self, path):
        if path:
            if os.path.exists(path):
                return True, ''
            else:
                return False, '你开启了查找外部文件夹,但是提供的文件夹不存在,请在更改配置里修改文件夹路径,如果不需要请取消查找外部文件夹'
        else:
            return False, '你开启了查找外部文件夹,但未提供外部查找文件夹路径,请在更改配置里修改文件夹路径,如果不需要请取消查找外部文件夹'

    def start_processing(self):
        outside_search_path = self.global_config['outside_search_path']
        outside_search_passed_flag = True
        if self.row_one.outside_search_checkbox.isChecked():
            outside_search_passed_flag, tip = self.outside_floader_exsit(outside_search_path)
            if tip:
                self.show_info.set_show_text(tip)
                self.show_info.show_window()
                self.have_error_flag = True
        if outside_search_passed_flag:
            self.show_info.row_one.exit_button.disconnect()
            self.show_info.init_events()
            self.show_info.set_show_text('正在制作中,请稍后!')
            self.show_info.show_window()
            QApplication.processEvents()
            try:
                excel_path = os.path.join('模版', self.excel_name)
                self.cache_excel(excel_path, './模版/excel备份')
                pass_flag, error_rows, extra_searched = utils_operate_excel.check_excel(excel_path, self.folder_path, search_extra_floader = (self.row_one.outside_search_checkbox.isChecked(), outside_search_path), map_flag=self.global_config['map_flag'])
                self.row_one.outside_search_checkbox.setChecked(False)
            except PermissionError:
                pass_flag = 'excel未关闭或excel文件损坏!若损坏,在{./模版/excel备份}内有备份,替换excel后重新逐步制作.'
            if pass_flag == True:
                functions = [self.make_all_single] * len(utils_operate_excel.sheet_names)
                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(fn, inp) for fn, inp in zip(functions, utils_operate_excel.sheet_names)]
                    results = []
                    for future in as_completed(futures):
                        result = future.result()
                        results.append(result)
                # 处理所有函数返回的结果
                self.handle_results(results)
            else:
                open_floader(os.path.join('模版', self.excel_name))
                self.have_error_flag = True
                if pass_flag == False:
                    str_to_show = ','.join(natsorted(error_rows))
                    if len(extra_searched) != 0:
                        open_floader('./查找到的照片')
                        str_to_show_extra = '\n【' + ','.join(extra_searched) + '】的照片在外部文件夹找到,已经复制到“查找到的照片”文件夹里,请复制到相应的位置.'
                    else:
                        str_to_show_extra = ''
                    self.show_info.set_show_text(f'excel中{str_to_show}行信息有误,已经将有误的地方标为红色,请检查!{str_to_show_extra}')
                else:
                    self.show_info.set_show_text(pass_flag)
                self.show_info.show_window()

    def make_singe(self, mode):
        outside_search_path = self.global_config['outside_search_path']
        outside_search_passed_flag = True
        if self.row_one.outside_search_checkbox.isChecked():
            outside_search_passed_flag, tip = self.outside_floader_exsit(outside_search_path)
            if tip:
                self.show_info.set_show_text(tip)
                self.show_info.show_window()
                self.have_error_flag = True
        if outside_search_passed_flag:
            try:
                self.row_one.outside_search_checkbox.setChecked(False)
            except:
                pass
            try:
                #缓存一定个数的excel,防止信息丢失
                excel_path = os.path.join('模版', self.excel_name)
                self.cache_excel(excel_path, './模版/excel备份')
                pass_flag, error_rows, extra_searched = utils_operate_excel.check_excel(os.path.join('模版', self.excel_name), self.folder_path, mode, search_extra_floader = (self.row_one.outside_search_checkbox.isChecked(), outside_search_path), map_flag=self.global_config['map_flag'])
            except PermissionError:
                pass_flag = 'excel未关闭或excel文件损坏!若损坏,在{./模版/excel备份}内有备份,替换excel后重新逐步制作.'
            if pass_flag == True:
                try:
                    self.which_func(mode, True)
                    pass_flag_after, error_rows_after = utils_operate_excel.check_excel_after(os.path.join('模版', self.excel_name), mode)
                    if not pass_flag_after:
                        open_floader(os.path.join('模版', self.excel_name))
                        self.have_error_flag = True
                        if len(error_rows_after) != 0:
                            str_to_show_after = ','.join(error_rows_after) + ' 行'
                        else:
                            str_to_show_after = ''
                        self.show_info.set_show_text(f'已将 {str_to_show_after}可能有误的照片编辑信息标红,请检查,word已按原信息制作,若检查无误就不用管,若确实有问题需修改对应照片的.info后重新制作.')
                        self.show_info.show_window()
                except:
                    self.shwo_total_error()
            else:
                self.have_error_flag = True
                if pass_flag == False:
                    open_floader(os.path.join('模版', self.excel_name))
                    str_to_show = ','.join(natsorted(error_rows))
                    if len(extra_searched) != 0:
                        open_floader('./查找到的照片')
                        str_to_show_extra = '\n【' + ','.join(extra_searched) + '】的照片在外部文件夹找到,已经复制到“查找到的照片”文件夹里,请复制到相应的位置.'
                    else:
                        str_to_show_extra = ''
                    self.show_info.set_show_text(f'excel中{str_to_show}行信息有误,已经将有误的地方标为红色,请检查!{str_to_show_extra}')
                else:
                    self.show_info.set_show_text(pass_flag)
                self.show_info.show_window()

    def make_all_single(self, mode):
        error_part = []
        show_str = []
        try:
            str = self.get_error_str(mode, self.which_func(mode))
            if str != '':
                show_str.append(str)
        except:
            error_part.append(mode)
        return (show_str, error_part)
    
    def handle_results(self, results):
        error_part = []
        show_str = []
        for result in results:
            if result[0] != []:
                show_str.extend(result[0])
            if result[1] != []:
                error_part.extend(result[1])
        show_str = [i for i in show_str if i != '']
        show_s = ''
        if len(error_part) != 0:
            show_s = ','.join(error_part) + '制作失败\n'
            self.have_error_flag = True
        if len(show_str) != 0:
            sstr = '\n'.join(show_str)
            show_s += f'{sstr}\n'
            self.have_error_flag = True
        if show_s != '':
            show_s += '请检查提供的信息和照片是否完全,或者联系作者.'
            self.show_info.set_show_text(show_s)
            self.show_info.show_window()
        else:
            pass_flag_after, error_rows_after = utils_operate_excel.check_excel_after(os.path.join('模版', self.excel_name))
            self.row_one.outside_search_checkbox.setChecked(False)
            if not pass_flag_after:
                open_floader(os.path.join('模版', self.excel_name))
                self.have_error_flag = True
                if len(error_rows_after) != 0:
                    str_to_show_after = '第' + ','.join(error_rows_after) + '行'
                else:
                    str_to_show_after = ''
                self.show_info.set_show_text(f'已将{str_to_show_after}可能有误的照片编辑信息标红,请检查,word已按原信息制作,若检查无误就不用管,若确实有问题需修改对应照片的.info后重新制作.')
                self.show_info.show_window()
            if not self.have_error_flag:
                duration = self.global_config['show_tip_timer_duration']
                if duration > 0:
                    self.show_info.set_show_text('制作完成!')
                    self.show_info.show_window()
                    self.combbox_change_tips_timer.start(duration) 

    def which_func(self, mode, check=False):
        if mode == '开单':
            return self.creat_kaidan(mode, check)
        elif mode == '拿货':
            return self.creat_nahuo(mode, check)
        elif mode == '转单':
            return self.creat_zhuandan(mode, check)
        elif mode == '年费':
            return self.creat_nianfei(mode, check)
        elif mode == '补单':
            return self.creat_budan(mode, check)
        elif mode == '补卡':
            return self.creat_buka(mode, check)
        elif mode == '退单':
            return self.creat_tuidan(mode, check)

    def shwo_total_error(self):
        self.show_info.set_show_text('制作失败或部分成功\n提供的信息缺失或excel未关闭\n如果检查无误\n就是代码有问题\n请联系作者')
        self.show_info.show_window()

    def get_error_str(self, cue, errors):
        if len(errors) != 0:
            errors_s = ','.join(errors)
            return f'{cue}:{errors_s}'
        else:
            return ''

    def end_pdf_to_pic(self):
        self.pdf_to_pic_finished += 1
        if self.pdf_to_pic_finished == self.pdf_to_pic_count:
            self.row_two.select_files_button.setEnabled(True)
            duration = self.global_config['show_tip_timer_duration']
            if duration > 0:
                self.show_info.set_show_text('转换成功!')
                self.show_info.show_window()
                self.combbox_change_tips_timer.start(duration)  
            self.pdf_to_pic_finished = 0
            self.pdf_to_pic_count = 0

    def show_error(self, errors):
        if len(errors) != 0:
            name_str = ','.join(errors)
            self.show_info.set_show_text(f"部分制作完成\n{name_str}\n信息缺失或照片缺失\n注意红色部分信息填写完整\n如果不知道怎么填看第一页的模版\n其所在内组的word未制作")
            self.show_info.show()
            self.have_error_flag = True

    def show_excel_none(self, mode):
        self.have_error_flag = True
        self.show_info.set_show_text(f'excel里没有填写<{mode}>的任何信息,请先填写信息再制作.')
        self.show_info.show()

    def add_certain_pics(self, doc):
        try:
            if self.global_config['which_add_pic_way'] == 1:
                doc = append_fullpage_image_center(doc, margin_mm=self.global_config['margin_mm'])
            else:
                if self.front_doc == None:
                    if os.path.exists(self.add_front_path):
                        doc_temp = Document(self.add_front_path)
                        if not is_word_empty(doc_temp):
                            self.front_doc = doc_temp
                            doc = concat_two_words(self.front_doc, doc, mode = 0)
                        else:
                            self.front_doc = 'empty'
                    else:
                        self.front_doc = 'ne'
                else:
                    doc = concat_two_words(self.front_doc, doc)
                if self.back_doc == None:
                    if os.path.exists(self.add_back_path):
                        doc_temp = Document(self.add_back_path)
                        if not is_word_empty(doc_temp):
                            self.back_doc = doc_temp
                            doc = concat_two_words(doc, self.back_doc, mode = 1)
                        else:
                            self.back_doc = 'empty'
                    else:
                        self.back_doc = 'ne'
                else:
                    doc = concat_two_words(doc, self.back_doc)
        except:
            pass
        return doc

    def creat_zhuandan(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_zhuandan_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                words = ['转让', '授权', '年费']
                #如果被委托人的卡号为空就不需要办年费,不为空就办
                if not isinstance(kaidan_pair.beiweituo.sail_card_id, str):
                    words.pop()
                for word in words:
                    name_concat = kaidan_pair.beiweituo.name + '_' + kaidan_pair.client.name + '_' + kaidan_pair.entrusted.name
                    count = 0
                    if kaidan_pair.client.native == '香港':
                        count += 1
                    if kaidan_pair.entrusted.native == '香港':
                        count += 1
                    kaidan_path = copy_template(mode, self.folder_path, name_concat, count, word, in_floader=True)
                    shift = 0
                    if word == '转让':
                        company = self.global_config['company_name']
                        changes, obj = zhuandan.get_sub_arr_zhuanrang(kaidan_pair, self.global_config[f'{company}_config']['zhuandan_before'], self.global_config[f'{company}_config']['zhuandan_after'])
                        shift = -4
                    elif word == '授权':
                        changes, obj = zhuandan.get_sub_arr_shouquan(kaidan_pair, self.global_config['company_name'])
                        shift = 4
                    elif word == '年费':
                        changes, obj = zhuandan.get_sub_arr_nianfei(kaidan_pair)
                        shift = 2
                    doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                    doc = replace_pic(doc, obj, 18 + shift, kaidan_path, 0, 6, self.pic_scale)
                    doc = replace_pic(doc, obj, 16 + shift, kaidan_path, 1, 6, self.pic_scale)
                    if self.global_config['add_certain_pics']:
                        doc = self.add_certain_pics(doc)
                    try:
                        utils_operate_excel.fill_information(obj, f'./模版/{self.excel_name}', mode, cache_all_flag=True)
                    except:
                        pass
                    doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 3)
            self.show_error(errors)
            return errors

    def creat_nahuo(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_nahuo_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                name_concat = kaidan_pair.entrusted.name + '_' + kaidan_pair.client.name
                count = 0
                if kaidan_pair.client.native == '香港':
                    count += 1
                if kaidan_pair.entrusted.native == '香港':
                    count += 1
                kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                changes = nahuo.get_sub_arr(kaidan_pair)
                doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                doc = replace_pic(doc, kaidan_pair,18, kaidan_path, 0, 6, self.pic_scale, self.global_config['in_floader'])
                doc = replace_pic(doc, kaidan_pair, 16, kaidan_path, 1, 6, self.pic_scale, self.global_config['in_floader'])
                if self.global_config['add_certain_pics']:
                    doc = self.add_certain_pics(doc)
                try:
                    utils_operate_excel.fill_information(kaidan_pair, f'./模版/{self.excel_name}', mode, cache_all_flag=False)
                except:
                    pass
                doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 2)
            self.show_error(errors)
            return errors
    
    def creat_nianfei(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_nianfei_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                name_concat = kaidan_pair.entrusted.name + '_' + kaidan_pair.client.name
                count = 0
                if kaidan_pair.client.native == '香港':
                    count += 1
                if kaidan_pair.entrusted.native == '香港':
                    count += 1
                kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                changes = nianfei.get_sub_arr_nianfei(kaidan_pair)
                doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                doc = replace_pic(doc, kaidan_pair,20, kaidan_path, 0, 6, self.pic_scale, self.global_config['in_floader'])
                doc = replace_pic(doc, kaidan_pair, 18, kaidan_path, 1, 6, self.pic_scale, self.global_config['in_floader'])
                if self.global_config['add_certain_pics']:
                    doc = self.add_certain_pics(doc)
                try:
                    utils_operate_excel.fill_information(kaidan_pair, f'./模版/{self.excel_name}', mode, cache_all_flag=False)
                except:
                    pass
                doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 2)
            self.show_error(errors)
            return errors

    def creat_kaidan(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_kaidan_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                name_concat = kaidan_pair.entrusted.name + '_' + kaidan_pair.client.name
                count = 0
                if kaidan_pair.client.native == '香港':
                    count += 1
                if kaidan_pair.entrusted.native == '香港':
                    count += 1
                card_id_client = kaidan_pair.client.sail_card_id
                card_id_entrusted = kaidan_pair.entrusted.sail_card_id
                kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                if (card_id_client != '' and not pd.isna(card_id_client)) and (card_id_entrusted != '' and not pd.isna(card_id_entrusted)):
                    kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'], template_sub_path=['有经销商卡号'])
                    changes = kaidan.get_sub_arr(kaidan_pair, mode = 'id')
                else:
                    kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                    changes = kaidan.get_sub_arr(kaidan_pair)
                doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                doc = replace_pic(doc, kaidan_pair, 20, kaidan_path, 0, 6, self.pic_scale, self.global_config['in_floader'])
                doc = replace_pic(doc, kaidan_pair, 18, kaidan_path, 1, 6, self.pic_scale, self.global_config['in_floader'])
                if self.global_config['add_certain_pics']:
                    doc = self.add_certain_pics(doc)
                try:
                    utils_operate_excel.fill_information(kaidan_pair, f'./模版/{self.excel_name}', mode, cache_all_flag=False)
                except:
                    pass
                doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 2)
            self.show_error(errors)
            return errors
    
    def creat_budan(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_budan_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                name_concat = kaidan_pair.entrusted.name + '_' + kaidan_pair.client.name
                count = 0
                if kaidan_pair.client.native == '香港':
                    count += 1
                if kaidan_pair.entrusted.native == '香港':
                    count += 1
                kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                changes = budan.get_sub_arr_budan(kaidan_pair)
                doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                doc = replace_pic(doc, kaidan_pair, 14, kaidan_path, 0, 6, self.pic_scale, self.global_config['in_floader'])
                doc = replace_pic(doc, kaidan_pair, 12, kaidan_path, 1, 6, self.pic_scale, self.global_config['in_floader'])
                if self.global_config['add_certain_pics']:
                    doc = self.add_certain_pics(doc)
                try:
                    utils_operate_excel.fill_information(kaidan_pair, f'./模版/{self.excel_name}', mode, cache_all_flag=False)
                except:
                    pass
                doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 2)
            self.show_error(errors)
            return errors
    
    def creat_buka(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_buka_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                name_concat = kaidan_pair.entrusted.name + '_' + kaidan_pair.client.name
                count = 0
                if kaidan_pair.client.native == '香港':
                    count += 1
                if kaidan_pair.entrusted.native == '香港':
                    count += 1
                kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                changes = buka.get_sub_arr_buka(kaidan_pair)
                doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                doc = replace_pic(doc, kaidan_pair, 15, kaidan_path, 0, 6, self.pic_scale, self.global_config['in_floader'])
                doc = replace_pic(doc, kaidan_pair, 13, kaidan_path, 1, 6, self.pic_scale, self.global_config['in_floader'])
                if self.global_config['add_certain_pics']:
                    doc = self.add_certain_pics(doc)
                try:
                    utils_operate_excel.fill_information(kaidan_pair, f'./模版/{self.excel_name}', mode, cache_all_flag=False)
                except:
                    pass
                doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 2)
            self.show_error(errors)
            return errors

    def creat_tuidan(self, mode, check_none = False):
        df = utils_operate_excel.read_sheets(f'./模版/{self.excel_name}', mode)
        kaidan_pairs, errors = utils_operate_excel.get_tuidan_pairs(df, self.folder_path)
        if check_none and len(kaidan_pairs) == 0 and len(errors) == 0:
            self.show_excel_none(mode)
        else:
            for kaidan_pair in kaidan_pairs:
                assert isinstance(kaidan_pair, utils_operate_excel.Pair)
                name_concat = kaidan_pair.entrusted.name + '_' + kaidan_pair.client.name
                count = 0
                if kaidan_pair.client.native == '香港':
                    count += 1
                if kaidan_pair.entrusted.native == '香港':
                    count += 1
                kaidan_path = copy_template(mode, self.folder_path, name_concat, count, in_floader=self.global_config['in_floader'])
                changes = tuidan.get_sub_arr_tuidan(kaidan_pair)
                doc, _ = replace_text_with_same_format(kaidan_path, "<<<<>", changes)
                doc = replace_pic(doc, kaidan_pair, 17, kaidan_path, 0, 6, self.pic_scale, self.global_config['in_floader'])
                doc = replace_pic(doc, kaidan_pair, 15, kaidan_path, 1, 6, self.pic_scale, self.global_config['in_floader'])
                if self.global_config['add_certain_pics']:
                    doc = self.add_certain_pics(doc)
                try:
                    utils_operate_excel.fill_information(kaidan_pair, f'./模版/{self.excel_name}', mode, cache_all_flag=False)
                except:
                    pass
                doc.save(kaidan_path)
                if self.global_config['in_floader']:
                    kaidan.move_pic(kaidan_pair, self.folder_path, os.path.dirname(kaidan_path), 2)
            self.show_error(errors)
            return errors

    def init_ui(self):
        self.setWindowTitle("选择功能")
        self.setGeometry(self.shape.start_width, self.shape.start_height, self.shape.width, self.shape.height)
        self.setFixedSize(self.shape.width, self.shape.height)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.row_company = Select_Company(
            central_widget,
            self.global_config['companys'],
            self.shape.shape_tuples[0][0],
            self.shape.shape_tuples[0][1],
            self.shape.shape_tuples[0][2]
        )

        self.row_zero = Row_Zero(
            central_widget,
            self.shape.shape_tuples[2][0],
            self.shape.shape_tuples[2][1],
            self.shape.shape_tuples[2][2],
            self.shape.shape_tuples[2][3],
        )

        self.row_one = Row_One(
            central_widget,
            self.shape.shape_tuples[1][0],
            self.shape.shape_tuples[1][1],
            self.shape.shape_tuples[1][2],
            self.global_config['enable_update']
        )

        self.row_two = Row_Two(
            central_widget,
            self.shape.shape_tuples[3][0],
            self.shape.shape_tuples[3][1],
            self.shape.shape_tuples[3][2],
        )

        self.row_catch = Row_Catch(
            central_widget,
            self.shape.shape_tuples[4][0],
            self.shape.label_height * self.global_config['main_window_conf']['catch_max_height']
        )

    def change_function_index(self):
        self.row_two.select_files_button.clicked.disconnect()
        try:
            self.row_two.open_newest_button.clicked.disconnect()
        except:
            self.row_two.open_newest_button.pressed.disconnect()
            self.row_two.open_newest_button.released.disconnect()
        current_index = self.row_one.function_combobox.currentIndex()
        if current_index == 0 or current_index == 1:
            # if current_index == 0:
            #     self.row_one.pic_here_checkbox.setChecked(True)
            # else:
            #     self.row_one.pic_here_checkbox.setChecked(False)
            self.row_one.pic_here_checkbox.setChecked(True)
            self.row_one.open_floader_checkbox.hide()
            self.row_one.open_text_checkbox.hide()
            self.row_one.pic_here_checkbox.show()
            self.row_one.searched_checkbox.hide()
            self.row_one.outside_search_checkbox.hide()
            self.row_zero.tip_label.setText('文件类型:')
            self.row_two.open_newest_button.setText('打开最新/删除所有编辑')
            self.row_two.open_newest_button.setToolTip('短按打开编辑结果中最新生成结果的文件夹,长按删除"照片编辑结果"中所有编辑')
            self.row_two.open_newest_button.pressed.connect(self.open_newest_pressed)
            self.row_two.open_newest_button.released.connect(self.open_newest_released)
            self.row_zero.tip_label.show()
            self.row_zero.file_type_combobox.setEnabled(True)
            self.row_zero.file_type_combobox.show()
            self.row_zero.pic_name_lineedit.hide()
            self.row_zero.select_newest_checkbox.hide()
            self.change_moren_pic()
        elif current_index == 2:
            self.row_one.open_floader_checkbox.show()
            self.row_one.open_text_checkbox.show()
            self.row_one.pic_here_checkbox.hide()
            self.row_one.searched_checkbox.hide()
            self.row_one.outside_search_checkbox.hide()
            self.row_zero.tip_label.setText('输入名字:')
            self.row_two.open_newest_button.setText('繁体转简体')
            self.row_two.select_files_button.setText('查询')
            self.row_two.select_files_button.setToolTip('输入完名称之后在高频照片和缓存照片里开始查询')
            self.row_two.open_newest_button.setToolTip('如果输入的名字时香港人的名字且带繁体,输入查询的人名后将名字从繁体转为简体')
            self.row_two.select_files_button.clicked.connect(self.search_name)
            self.row_two.open_newest_button.clicked.connect(self.fan_zhuan_jian)
            self.row_zero.tip_label.show()
            self.row_zero.pic_name_lineedit.show()
            self.row_zero.file_type_combobox.hide()
            self.row_zero.select_newest_checkbox.hide()
            self.row_zero.pic_name_lineedit.setFocus()
        elif current_index == self.concat_index or current_index == 12 or current_index == 13:
            self.row_one.open_floader_checkbox.hide()
            self.row_one.open_text_checkbox.hide()
            self.row_one.pic_here_checkbox.hide()
            self.row_one.outside_search_checkbox.hide()
            if current_index == self.concat_index:
                self.row_one.searched_checkbox.show()
                self.change_searched_concat_mode()
            else:
                self.row_one.searched_checkbox.hide()
            self.row_two.open_newest_button.setText('打开最新/删除所有编辑')
            self.row_zero.tip_label.setText('文件类型:')
            self.row_two.open_newest_button.setToolTip('短按打开编辑结果中最新生成结果的文件夹,长按删除"照片编辑结果"中所有编辑')
            self.row_two.open_newest_button.pressed.connect(self.open_newest_pressed)
            self.row_two.open_newest_button.released.connect(self.open_newest_released)
            self.row_zero.tip_label.show()
            self.row_zero.file_type_combobox.show()
            self.row_zero.file_type_combobox.setDisabled(True)
            self.row_zero.pic_name_lineedit.hide()
            self.row_zero.select_newest_checkbox.hide()
            if current_index != 13:
                if current_index != self.concat_index:
                    self.row_two.select_files_button.setText('选择文件/文件夹')
                    self.row_two.select_files_button.setToolTip('选择文件或者文件夹直接跳转开始编辑')
                self.row_two.select_files_button.clicked.connect(lambda: self.open_folder_dialog())
            else:
                if self.global_config['enable_update']:
                    self.row_two.select_files_button.setText('开始更新')
                    self.row_two.select_files_button.setToolTip('开始更新程序')
                    self.row_two.select_files_button.clicked.connect(self.update_software)
                else:
                    self.row_two.select_files_button.setText('开始下载')
                    self.row_two.select_files_button.setToolTip('从云空间下载源码,手动更新软件')
                    self.row_two.select_files_button.clicked.connect(self.only_download_source_code)
        else:
            self.row_one.open_floader_checkbox.hide()
            self.row_one.open_text_checkbox.hide()
            self.row_one.pic_here_checkbox.hide()
            self.row_one.searched_checkbox.hide()
            self.row_one.outside_search_checkbox.show()
            self.row_two.open_newest_button.setText('打开最新/删除所有编辑')
            self.row_two.open_newest_button.setToolTip('短按打开编辑结果中最新生成结果的文件夹,长按删除"照片编辑结果"中所有编辑')
            self.row_two.open_newest_button.pressed.connect(self.open_newest_pressed)
            self.row_two.open_newest_button.released.connect(self.open_newest_released)
            self.row_zero.file_type_combobox.hide()
            self.row_zero.pic_name_lineedit.hide()
            self.row_zero.tip_label.hide()
            self.row_zero.select_newest_checkbox.show()
            self.change_moren()

    def only_download_source_code(self):
        self.pwd = os.getcwd()
        os.chdir('..')
        self.show_info.set_show_text(f'正在下载源代码,请稍等......')
        self.show_info.show()
        QApplication.processEvents()
        self.download_source_code_thread = Download_Sourcecode(self.global_config, 1, 1, '源码', 1, 1, True)
        self.download_source_code_thread.resSignal.connect(self.end_only_download_sourcecode)
        self.download_source_code_thread.start()

    def end_only_download_sourcecode(self, pos1, pos2, pos3, pos4, pos5):
        self.show_info.set_show_text(f'下载完成,请在根目录下查看,手动更新软件.')
        self.show_info.show()
        os.chdir(self.pwd)

    def update_software(self):
        current_os = platform.system() 
        if current_os == "Windows":
            os.chdir('..')
            self.new_name_flag = False
            result_name = '身份证照片识别'
            name = self.global_config['repo']
            ref = self.global_config['ref']
            name = f'{name}-{ref}'
            zip_file_path = f'{result_name}.zip'
            root_floader = os.path.abspath('.')
            old_version = self.global_config['version']
            conf_path = '配置/conf.yaml'
            if not os.path.exists(self.global_config['repo']) and not os.path.exists(name):
                download_single_file(self.global_config, conf_path, 'conf.yaml')
                config_check = get_config('conf.yaml')
                new_version = config_check['version']
                os.remove('conf.yaml')
                if new_version == old_version and not self.global_config['mandatory_update']:
                    self.show_info.set_show_text(f'已是最新版本,不需要更新')
                    self.show_info.show()
                    return
                else:
                    self.show_info.set_show_text(f'正在下载源代码,请稍等......')
                    self.show_info.show()
                    QApplication.processEvents()
                    self.download_source_code_thread = Download_Sourcecode(self.global_config, name, zip_file_path, result_name, root_floader, new_version)
                    self.download_source_code_thread.resSignal.connect(self.end_get_source_code)
                    self.download_source_code_thread.start()
            #软件解压如果有问题,那就手动解压
            else:
                # 以云端下载为准
                if os.path.exists(self.global_config['repo']) and not os.path.exists(name):
                    shutil.move(self.global_config['repo'], name)
                try:
                    config_check = get_config(f'{name}/{conf_path}')
                except:
                    self.show_info.set_show_text(f'提供的源代码或者云端下载的源代码有问题,压缩包名应该为"身份证照片识别.zip", 其内的文件夹名应为"{name}",如还有问题请联系作者')
                    self.show_info.show()
                    return
                new_version = config_check['version']
                if new_version == old_version:
                    self.show_info.set_show_text(f'已是最新版本,不需要更新')
                    self.show_info.show()
                    return
                self.end_get_source_code(name, zip_file_path, result_name, root_floader, new_version)
        # elif current_os == "Darwin":  # macOS
        else:
            self.show_info.set_show_text(f'此功能暂不支持在非windows系统上更新')
            self.show_info.show()

    def end_get_source_code(self, name, zip_file_path, result_name, root_floader, new_version):
        os.chdir(name)
        self.hide()
        QApplication.processEvents()
        shutil.copy(os.path.join('配置', 'new', 'main.spec'), './main.spec')
        shell_path = os.path.abspath(self.global_config['update_shell_path'])
        conda_env = self.global_config['conda_env_name']
        try:
            os.chmod(shell_path, 0o755)
        except:
            pass
        command = [
            "cmd",  # 调用 PowerShell
            "/c",  # 不加载用户配置文件,避免干扰
            shell_path,  # 指定脚本路径
            conda_env
        ]
        self.show_info.row_one.exit_button.hide()
        self.show_info.row_one.tip_label.setFixedSize(self.show_info.width() - 2 * self.show_info.shape.round_gap, self.show_info.row_one.tip_label.height())
        self.show_info.setWindowTitle('更新软件中')
        time_count = 1000
        self.update_timer = QTimer()
        self.only_once_flag = True
        self.update_timer.timeout.connect(lambda: self.end_pyinstaller(time_count, name, result_name, root_floader, new_version, zip_file_path))
        #不显示黑色terminal窗口
        if self.global_config['update_window']:
            self.pyinstaller_process = subprocess.Popen(command)
            self.show_info.set_show_text(f'正在更新中,不要关闭黑色窗口,如果软件在云空间,最好先关闭云空间同步,请耐心等待......')
        else:
            self.pyinstaller_process = subprocess.Popen(command, creationflags=0x08000000)
            self.show_info.set_show_text(f'正在更新中,如果软件在云空间,最好先关闭云空间同步,请耐心等待......')
        self.show_info.show()
        self.update_timer.start(time_count)

    def end_pyinstaller(self, time_count, name, save_name, root_floader, new_version, zip_file_path):
        wait_start_flag = False
        if self.pyinstaller_process.poll() is None:
            self.update_timer.start(time_count)  # 继续定时器
        else:
            wait_start_flag = True
        if wait_start_flag and self.only_once_flag:
            self.only_once_flag = False
            os.chdir(root_floader)
            write_config(recursive_update(get_config(os.path.join('配置', 'conf.yaml')), get_config(os.path.join(name, '配置', 'conf.yaml')), [('version')]), os.path.join(name, '配置', 'conf.yaml'))
            shutil.move(os.path.join(name, '配置'), os.path.join(name, 'dist', 'main', '配置'))
            if os.path.exists(zip_file_path):
                # send2trash(zip_file_path)
                shutil.move(zip_file_path, os.path.join(name, 'dist', 'main', '配置', zip_file_path))
            if not os.path.exists(os.path.join(name, 'dist', 'main', '_internal', '_tk_data')) and os.path.exists(os.path.join('_internal', '_tk_data')):
                shutil.copytree(os.path.join('_internal', '_tk_data'), os.path.join(name, 'dist', 'main', '_internal', '_tk_data'))
            time_new_str = get_data_str()
            f_name = f'{time_new_str}_{save_name}{new_version}' if os.path.exists(os.path.join(os.path.dirname(root_floader), f'{save_name}{new_version}')) else f'{save_name}{new_version}'
            shutil.move(os.path.join(name, 'dist', 'main'), os.path.join(os.path.dirname(root_floader), f_name))
            self.copy_threads = []  # 在类初始化时准备一个列表
            self.count_finished_copy = 0
            companys = self.global_config['companys']
            if len(companys) > 0:
                for i in companys:
                    if os.path.exists(i):
                        if self.global_config['stay_old']:
                            copy_thread = Download_Copy_Large(i, os.path.join(os.path.dirname(root_floader), f_name, i), name)
                            copy_thread.resSignal.connect(self.after_end)
                            copy_thread.start()
                            self.copy_threads.append(copy_thread)  # 保存引用
                        else:
                            shutil.move(f'{i}', os.path.join(os.path.dirname(root_floader), f_name, i))
            else:
                self.after_end('', name)

    def after_end(self, name):
        if len(self.copy_threads) != 0:
            # text = self.show_info.row_one.tip_label.toPlainText()
            # company_name = source.replace('_', ' ')
            # self.show_info.set_show_text(f'{text}\n{company_name}复制完成')
            # self.show_info.show()
            # QApplication.processEvents()
            self.count_finished_copy += 1
        if self.count_finished_copy == len(self.copy_threads):
            show_str = '更新完成\n现在可以关闭这个窗口打开新软件使用'
            try:
                shutil.rmtree(name)
            except:
                show_str += '\n请手动删除更新过程中产生的冗余文件.'
            self.show()
            self.show_info.setWindowTitle('更新完成')
            self.show_info.set_show_text(show_str)
            try:
                self.show_info.row_one.exit_button.hide()
            except:
                pass
            self.show_info.row_one.tip_label.setFixedSize(self.show_info.width() - 2 * self.show_info.shape.round_gap, self.show_info.row_one.tip_label.height())
            self.show_info.show()
            self.hide()
            self.setDisabled(True)

    def operate_on_moren(self):
        floader_path = './照片编辑结果'
        check = [os.path.join(floader_path, i) for i in os.listdir(floader_path)]
        paths = natsorted([i for i in check if os.path.isdir(i)])
        if len(paths) == 0:
            path_t = os.path.join(floader_path, get_data_str())
            os.makedirs(path_t, exist_ok=True)
        else:
            path_t = paths[-1]
        self.open_folder_dialog(path_t)

    def operate_on_moren_pic(self):
        floader_path = './照片放这里'
        need_to_cut_between_path = f'{floader_path}/横着中间截图'
        if os.path.exists(need_to_cut_between_path):
            cut_paths = os.listdir(need_to_cut_between_path)
            if '.DS_Store' in cut_paths:
                cut_paths.remove('.DS_Store')
            cut_paths = [i for i in cut_paths if i.rsplit('.', maxsplit=1)[-1] in self.formates[:-1]]
            if len(cut_paths) != 0:
                proportion = self.global_config['cut_proportion']
                unix_date = get_data_str()
                for index, i in enumerate(cut_paths):
                    split_image(os.path.join(need_to_cut_between_path, i),
                                os.path.join(floader_path, f'split_c_{unix_date}-{index * 2 + 1}'),
                                os.path.join(floader_path, f'split_c_{unix_date}-{index * 2 + 2}'),
                                proportion,
                                0)

        height_need_to_cut_between_path = f'{floader_path}/竖着中间截图'
        if os.path.exists(height_need_to_cut_between_path):
            cut_paths = os.listdir(height_need_to_cut_between_path)
            if '.DS_Store' in cut_paths:
                cut_paths.remove('.DS_Store')
            cut_paths = [i for i in cut_paths if i.rsplit('.', maxsplit=1)[-1] in self.formates[:-1]]
            if len(cut_paths) != 0:
                proportion = self.global_config['height_cut_proportion']
                unix_date = get_data_str()
                for index, i in enumerate(cut_paths):
                    split_image(os.path.join(height_need_to_cut_between_path, i),
                                os.path.join(floader_path, f'split_c_height_{unix_date}-{index * 2 + 1}'),
                                os.path.join(floader_path, f'split_c_height_{unix_date}-{index * 2 + 2}'),
                                proportion,
                                1)
        self.open_folder_dialog(floader_path)

    def fan_zhuan_jian(self):
        text = self.row_zero.pic_name_lineedit.text().replace(' ', '')
        if text:
            try:
                text = fan_to_jian(text)
            except:
                pass
            self.row_zero.pic_name_lineedit.setText(text)
        else:
            self.show_info.set_show_text(f'你还没有输入名字,或者名字为空!')
            self.show_info.show()
        self.row_zero.pic_name_lineedit.setFocus()

    def search_name(self):
        text = self.row_zero.pic_name_lineedit.text().replace(' ', '').strip()
        if text:
            searched = []
            #新制作照片里找
            searched_in_catch = find_in_catch_pic(text, './照片编辑结果', 2)
            if searched_in_catch != '':
                searched.append(os.path.dirname(searched_in_catch))
            #高频信息里面找
            cache_path = os.path.join('.', '模版', '高频照片')
            cache_names = os.listdir(cache_path)
            if text + '.info' in cache_names and text + '.png' in cache_names and text + '反.png' in cache_names:
                searched.append(cache_path)
            #cache里找
            searched_in_catch = find_in_catch_pic(text, './模版/缓存照片', 2)
            if searched_in_catch != '':
                searched.append(os.path.dirname(searched_in_catch))
            if len(searched) != 0:
                show_str = '\n'.join(searched)
                self.show_info.set_show_text(f'{text}信息已存在,照片和信息存在于:\n{show_str}')
                if self.row_one.open_text_checkbox.isChecked():
                    for i in searched:
                        open_floader(os.path.join(i, f'{text}.info'))
                if self.row_one.open_floader_checkbox.isChecked():
                    open_floader(searched[0], f'{text}.png')
            else:
                self.show_info.set_show_text(f'{text}信息不存在,需要编辑此人照片!如果是香港人名字且带繁体字,先点击繁体转简体再查询')
        else:
            self.show_info.set_show_text(f'你还没有输入名字,或者名字为空!')
        self.show_info.show()
        self.row_zero.pic_name_lineedit.setFocus()

    def open_excel(self):
        path = './模版/非身份证信息需求.xlsx'
        if os.path.exists(path):
            open_floader(path)
        else:
            self.show_info.set_show_text(f'{path} 不存在!')
            self.show_info.show()

    def change_moren(self):
        try:
            self.row_two.select_files_button.clicked.disconnect()
        except:
            pass
        if self.row_zero.select_newest_checkbox.isChecked():
            self.row_two.select_files_button.setText('确认制作')
            self.row_two.select_files_button.setToolTip('将制作的word默认保存到最新编辑结果文件夹中')
            self.row_two.select_files_button.clicked.connect(self.operate_on_moren)
        else:
            self.row_two.select_files_button.setText('选择保存路径')
            self.row_two.select_files_button.setToolTip('选择将制作的word与使用的照片和信息放到那个路径下')
            self.row_two.select_files_button.clicked.connect(lambda: self.open_folder_dialog())

    def change_moren_pic(self):
        try:
            self.row_two.select_files_button.clicked.disconnect()
        except:
            pass
        if self.row_one.pic_here_checkbox.isChecked():
            self.row_zero.file_type_combobox.setCurrentIndex(0)
            self.row_two.select_files_button.setText('确认制作')
            self.row_two.select_files_button.setToolTip('默认使用照片放这里的照片来编辑')
            self.row_two.select_files_button.clicked.connect(self.operate_on_moren_pic)
        else:
            self.row_two.select_files_button.setText('选择文件/文件夹')
            self.row_two.select_files_button.setToolTip('选择文件或者文件夹直接跳转开始编辑')
            self.row_two.select_files_button.clicked.connect(lambda: self.open_folder_dialog())

    def open_pic_floader(self):
        path = './照片放这里'
        open_floader(path)

    def init_black_button_timer(self):
        self.black_timer = QTimer()
        self.black_timer.setSingleShot(True)
        self.black_timer.timeout.connect(self.clear_photos)
        self.black_is_pressed = False

    def black_pressed(self):
        self.black_is_pressed = True
        self.black_timer.start(self.global_config['button_timer_duration'])

    def clear_photos(self):
        if self.black_is_pressed:
            self.black_is_pressed = False
            path = './照片放这里'
            if os.path.exists(path):
                try:
                    send2trash(path)
                except:
                    os.makedirs(f'{path}/横着中间截图', exist_ok=True)
                    os.makedirs(f'{path}/竖着中间截图', exist_ok=True)
                    self.show_info.set_show_text('“照片放这里”正在被其他应用占用,可能清空失败,再次单击打开这个文件检查是否被清空.未清空就手动清空')
                    self.show_info.show()
                    return
            os.makedirs(f'{path}/横着中间截图', exist_ok=True)
            os.makedirs(f'{path}/竖着中间截图', exist_ok=True)
            self.show_info.set_show_text('“照片放这里”文件夹已清空')
            self.show_info.show()

    def black_released(self):
        if self.black_is_pressed:
            self.black_is_pressed = False
            self.clear_photos()
            self.open_pic_floader()
            self.black_timer.stop()

    def init_open_newest_timer(self):
        self.open_newest_timer = QTimer()
        self.open_newest_timer.setSingleShot(True)
        self.open_newest_timer.timeout.connect(self.open_newest)
        self.open_newest_pressed_falg = False

    def open_newest_pressed(self):
        self.open_newest_pressed_falg = True
        self.open_newest_timer.start(self.global_config['button_timer_duration'])

    def open_newest(self):
        if self.open_newest_pressed_falg:
            self.open_newest_pressed_falg = False
            path = './照片编辑结果'
            if os.path.exists(path):
                try:
                    send2trash(path)
                except:
                    os.makedirs(path, exist_ok=True)
                    self.show_info.set_show_text('清空失败,你打开了“照片编辑结果”里的照片或者word文档,请先关闭打开的文件再次尝试,或者手动清空')
                    self.show_info.show()
                    return
            os.makedirs(path, exist_ok=True)
            self.show_info.set_show_text('“照片编辑结果”文件夹已清空')
            self.show_info.show()

    def open_newest_released(self):
        if self.open_newest_pressed_falg:
            self.open_newest_pressed_falg = False
            floader_path = './照片编辑结果'
            paths = natsorted(os.listdir(floader_path))
            if '.DS_Store' in paths:
                paths.remove('.DS_Store')
            paths = [os.path.join(floader_path, i) for i in paths]
            paths = [i for i in paths if os.path.isdir(i)]
            if len(paths) == 0:
                self.show_info.set_show_text('”照片编辑结果“文件夹内为空,请先编辑.')
                self.show_info.show()
            else:
                open_floader(paths[-1])

    def init_combbox_change_tips_timer(self):
        self.combbox_change_tips_timer = QTimer()
        self.combbox_change_tips_timer.setSingleShot(True)
        self.combbox_change_tips_timer.timeout.connect(self.change_tip)

    def change_company(self):
        company = self.row_company.company_combobox.currentText()
        self.global_config['company_name'] = company
        os.chdir(f'../{company}')

    def change_tip(self):
        self.show_info.hide()

    def change_height(self, height_shift):
        self.setFixedSize(self.width(), self.height() + height_shift)

    def change_config(self):
        self.set_config_window = Set_Config_Window(self.global_config)
        self.set_config_window.show()
        self.init_set_config_window_events()

    def ensure_change_config(self, forever_flag = False):
        global_config, flag = self.add_new_company(copy.deepcopy(self.set_config_window.global_config))
        if not forever_flag:
            forever_flag = flag
        #只有更改了才重启
        if self.global_config != global_config:
            self.refresh_main_window(global_config)
            if forever_flag:
                save_conf = copy.deepcopy(global_config)
                try:
                    del save_conf['company_name']
                except:
                    pass
                write_config(save_conf, '../配置/conf.yaml')
        # elif forever_flag:
        #     write_config(global_config, '../配置/conf.yaml')
        self.set_config_window.close()

    def add_new_company(self, global_config):
        company_name = re.sub(r'\s+', ' ', self.set_config_window.add_company_edit.text().strip())
        flag = False
        if company_name:
            floader_name = '_'.join(company_name.split(' '))
            if floader_name in global_config['companys']:
                self.show_info.set_show_text('添加的新公司已存在.')
            else:
                try:
                    floader_cache = os.getcwd()
                    new_floaders = ['照片编辑结果', '照片放这里/横着中间截图', '照片放这里/竖着中间截图', '模版/高频照片', '模版/缓存照片', '模版/excel备份']
                    os.chdir('..')
                    os.makedirs(floader_name, exist_ok=True)
                    for i in new_floaders:
                        os.makedirs(os.path.join(floader_name, i), exist_ok=True)
                    copy_company = self.set_config_window.copy_company_edit.currentText()
                    floaders = os.listdir(os.path.join(copy_company, '模版'))
                    for i in floaders:
                        floader_path = os.path.join(floader_name, '模版', i)
                        if not os.path.exists(floader_path):
                            if os.path.isdir(os.path.join(copy_company, '模版', i)):
                                shutil.copytree(os.path.join(copy_company, '模版', i), floader_path)
                            elif not i.endswith('error.log'):
                                shutil.copy(os.path.join(copy_company, '模版', i), floader_path)
                    #获取所有docx文件路径
                    doc_files = []
                    for dirpath, dirnames, filenames in os.walk(os.path.join(floader_name, '模版')):
                        for filename in filenames:
                            if filename.lower().endswith(('.doc', '.docx')):
                                full_path = os.path.join(dirpath, filename)
                                doc_files.append(full_path)
                    for i in doc_files:
                        doc, _ = replace_text_with_same_format(i, copy_company.replace('_', ' '), company_name)
                        doc.save(i)
                    global_config['companys'].append(floader_name)
                    global_config[f'{floader_name}_config'] = copy.deepcopy(global_config[f'{copy_company}_config'])
                    os.chdir(floader_cache)
                    self.show_info.set_show_text('新公司添加成功.')
                    flag = True
                except:
                    self.show_info.set_show_text('提供的公司名不符合文件夹命名标准,请更改.')
            self.show_info.show()
        return global_config, flag

    def init_set_config_window_events(self):
        self.set_config_window.ensure_button.clicked.connect(self.ensure_change_config)
        self.set_config_window.forever_ensure_button.clicked.connect(lambda: self.ensure_change_config(True))

    def change_searched_concat_mode(self):
        if self.row_one.searched_checkbox.isChecked():
            self.row_two.select_files_button.setText('开始')
            self.row_two.select_files_button.setToolTip('开始合并')
        else:
            self.row_two.select_files_button.setText('选择文件/文件夹')
            self.row_two.select_files_button.setToolTip('选择文件或者文件夹直接跳转开始编辑')

    def open_replace_window(self):
        self.replace_window = Replace_Select()
        self.replace_window.show()

    def init_events(self):
        self.init_black_button_timer()
        self.init_open_newest_timer()
        self.init_combbox_change_tips_timer()
        self.row_zero.exit_button.pressed.connect(self.black_pressed)
        self.row_zero.exit_button.released.connect(self.black_released)
        self.row_one.function_combobox.currentIndexChanged.connect(self.change_function_index)
        self.row_company.company_combobox.currentIndexChanged.connect(self.change_company)
        self.row_two.select_files_button.clicked.connect(self.operate_on_moren_pic)
        self.row_two.open_newest_button.pressed.connect(self.open_newest_pressed)
        self.row_two.open_newest_button.released.connect(self.open_newest_released)
        self.row_two.open_excel_button.clicked.connect(self.open_excel)
        self.row_zero.select_newest_checkbox.stateChanged.connect(self.change_moren)
        self.row_one.pic_here_checkbox.stateChanged.connect(self.change_moren_pic)
        self.row_catch.pic_name_lineedit.doubleClickedSignal.connect(self.change_height)
        self.row_company.confit_button.clicked.connect(self.change_config)
        self.row_one.searched_checkbox.clicked.connect(self.change_searched_concat_mode)
        self.row_zero.replace_button.clicked.connect(self.open_replace_window)