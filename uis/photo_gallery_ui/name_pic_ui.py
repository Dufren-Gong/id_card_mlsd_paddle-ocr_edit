import os, cv2, shutil, json, copy
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLineEdit, QPlainTextEdit
from PyQt6.QtGui import QIcon
from my_utils.utils import get_all_pic_path, cv_to_qpixmap, cv_imread, cv_imwrite, rgb_to_gray_with_three_channels, check_catch_pic, get_internal_path, add_edge #, calculate_brightness, adjust_brightness
from PyQt6.QtCore import Qt, QThreadPool, QTimer
from uis.photo_gallery_ui.scroll_area import Scroll_Area, ClickableLabel  # 导入 Scroll_Area 模块
from windows.show_info_window import Show_Info_Window
from windows.show_pic_window_for_name import Show_Pic_Window
from my_utils.threads import Get_Ocr
from my_utils.ocr_by_paddleocr import clear_gpu_cache, get_ocr_model
from my_utils import check
from uis.function_and_info_ui import names as card_info_key_check
import numpy as np
from PIL.ImageEnhance import Brightness as PILImageEnhanceBrightness
from PIL.ImageEnhance import Contrast as PILImageEnhanceContrast
from PIL.Image import fromarray as PILImagefromarray
from send2trash import send2trash

class Name_Pic(QMainWindow):
    def __init__(self, global_config, cut_save_floader, save_formate, id_shape, reopen_main_window, show_info:Show_Info_Window = None):
        super().__init__()
        self.this_index = None
        self.info_change_flag = False
        self.id_shape = id_shape
        self.global_config = global_config
        self.cut_save_floader = cut_save_floader
        self.save_formate = save_formate
        self.reopen_main_window = reopen_main_window
        self.show_info = show_info
        self.checked = []
        self.width_gap = 70
        self.height_gap = 60
        self.angle_rate = self.global_config['mlsd_conf']['angle_rate']
        self.fixed_width = self.global_config['paddleocr_conf']['small_pic_fixed_width']
        self.address_front_check = self.global_config['paddleocr_conf']['color']['check_front_strs']
        self.address_check = self.global_config['paddleocr_conf']['color']['check_total_strs']
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(self.global_config['paddleocr_conf']['max_threads'])
        screen_size = QApplication.primaryScreen().size()
        self.max_size = (int(screen_size.width()*0.8), int(screen_size.height()*0.8))
        self.liangdu_origin = True
        self.gaopin_path = './模版/高频照片'
        self.setWindowTitle("照片信息编辑")
        self.setGeometry(0, 0, 800, 600)
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        self.position_mode = self.global_config['paddleocr_conf']['defalut_position_mode']
        self.position_mode_text = ['默认原位', '默认移动']
        self.previous_nation = '未知'
        # 创建主布局，水平布局
        main_layout = QHBoxLayout()

        main_layout.setSpacing(20)  # 控件之间的间距为10像素
        main_layout.setContentsMargins(10, 10, 10, 10)  # 布局的外边距为10像素
        self.scroll_area_width = self.fixed_width + 30

        # 创建 QLabel 用于显示大图
        self.large_image_label = Show_Pic_Window(show_info, global_config, init_edge_color=copy.copy(self.global_config['paddleocr_conf']['edge_color']), height_gap=self.height_gap)
        self.large_image_label.row_six.all_moved_button.setText(self.position_mode_text[not self.position_mode])

        # 创建 Scroll_Area 实例
        self.scroll_area = Scroll_Area(width_t=self.scroll_area_width, 
                                       display_large_image_function=self.display_large_image,
                                       init_edge_ipx=copy.copy(self.global_config['paddleocr_conf']['edge_ipx']),
                                       init_edge_color=self.get_color_tuple(copy.copy(self.global_config['paddleocr_conf']['edge_color'])))   

        # 将 Scroll_Area 和 QLabel 添加到主布局
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.large_image_label)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 创建一个中心窗口部件并设置布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.init_event()
        self.first_show_flag = True
        self.close_flag = True
        self.obj_index = [
            self.large_image_label.row_one.pic_name_lineedit,
            self.large_image_label.row_two.pic_name_lineedit,
            self.large_image_label.row_two.two_pic_name_lineedit,
            self.large_image_label.row_four.pic_name_lineedit,
            self.large_image_label.row_five.pic_name_lineedit,
            self.large_image_label.row_six.pic_name_lineedit,
            self.large_image_label.row_six_seven.pic_name_lineedit
            ]
        self.display_flag = True

    def get_color_tuple(self, color):
        index = self.large_image_label.row_four.colors.index(color)
        return tuple([index * 50] * 3)

    def release(self):
        self.thread_pool = None
        del self.ocr_model
        self.ocr_model = None

    def init_model_and_device(self):
        self.ocr_model = get_ocr_model(self.global_config)
        gap = 2
        groups = int(len(self.photo_paths) / gap)
        cut_shape = self.global_config['paddleocr_conf']['screen_correct']
        for i in range(groups):
            index = i * gap
            path = self.photo_paths[index]
            cv_img = cv_imread(path)
            if self.global_config['check_back']:
                img_back = cv_imread(self.photo_paths[index + 1])
                h, w = img_back.shape[:2]
                # 纵向拼接
                cv_img = cv2.vconcat([img_back[int(h * cut_shape[2]) : int(h * cut_shape[3]), int(w * cut_shape[4]) : int(w * cut_shape[5])], cv_img[int(h * cut_shape[0]) : int(h * cut_shape[1]), int(w * cut_shape[6]) : int(w * cut_shape[7])]])
            ocr_thread = Get_Ocr(cv_img, self.ocr_model, path, scale=copy.copy(self.global_config['paddleocr_conf']['scale']), 
                                 pic_shape=tuple(self.global_config['mlsd_conf']['pic_shape']), 
                                 times=self.global_config['paddleocr_conf']['times'], 
                                 pic_type=self.global_config['paddleocr_conf']['ocr_pic_type'],
                                 info_checks=self.global_config['paddleocr_conf']['info_checks'],
                                 one_line_scale=self.global_config['paddleocr_conf']['one_line_scale'],
                                 check_back=self.global_config['check_back'])
            ocr_thread.signals.finished.connect(self.end_ocr)  # 把任务完成的信号与任务完成后处理的槽函数绑定
            self.thread_pool.start(ocr_thread)

    def end_ocr(self, catch, pic_info_dict, path):
        self.scroll_area.add_photos_for_name(path, catch, pic_info_dict)  # 向 Scroll_Area 添加照片
        if self.first_show_flag:
            self.first_show_flag = False
            self.show()
            QApplication.processEvents()
            if self.show_info != None:
                self.show_info.hide()
        if len(self.photo_paths) == len(self.scroll_area.labels):
            self.large_image_label.row_three.skip_button.setEnabled(True)
            self.large_image_label.row_three.black_button.setEnabled(True)
            self.release()
            clear_gpu_cache()

    def load_photos(self, dirs):
        if isinstance(dirs, list):
            self.photo_paths = dirs
        else:
            self.photo_paths = get_all_pic_path(dirs)

    def shwo_red_or_black(self, str_t, obj):
        if str_t == None:
            str_t = '未识别出来'
        if isinstance(obj, QLineEdit):
            if obj.moved_flag:
                if obj.space_flag:
                    str_t = '\u2009'.join(str_t.replace(' ', '').replace('\u2009', ''))
                if obj.data_flag:
                    if '年' in str_t and '月' in str_t and '日' in str_t:
                        str_t = str_t.replace('年', '*').replace('月', '*').replace('日', '*')
                        info = str_t.split('*')
                        if len(info) == 4:
                            str_t = [info[0]] + ['年'] + [info[1]] + ['月'] + [info[2]] + ['日']
                            str_t = ' '.join(str_t)
            obj.setText(str_t)
        elif isinstance(obj, QPlainTextEdit):
            obj.setPlainText(str_t)

    def change_info(self):
        catch = self.scroll_area.labels[self.this_index].info
        for key_index in range(len(card_info_key_check)):
            self.shwo_red_or_black(catch[key_index], self.obj_index[key_index])

    def display_large_image(self, photo_path, index):
        if index != self.this_index:
            self.display_flag = True
            self.large_image_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # 显示正常尺寸的图片
            self.this_index = index
            mode = self.scroll_area.labels[self.this_index].add_to_gaopin
            if mode:
                self.large_image_label.row_three.match_liangdu_button.setText("取消加入高频")
                self.large_image_label.row_three.match_liangdu_button.setToolTip('取消将这组照片和信息添加到高频信息里')
            else:
                self.large_image_label.row_three.match_liangdu_button.setText("加入高频")
                self.large_image_label.row_three.match_liangdu_button.setToolTip('将这组照片和信息添加到高频信息里')
            img = self.scroll_area.labels[self.this_index].img
            borders = self.scroll_area.labels[self.this_index].borders
            color = self.scroll_area.labels[self.this_index].edge_color
            if len(borders) != 0:
                img_border = add_edge(img, 
                                      self.angle_rate,
                                      self.scroll_area.labels[self.this_index].edge_ipx,
                                      color,
                                      borders)
            else:
                img_border = img
            self.large_image_label.row_four.border_color_combobox.setCurrentIndex(int(color[0] / 50))
            pixmap = cv_to_qpixmap(img_border)
            size = pixmap.size()
            width = size.width()
            height = size.height()
            self.large_image_label.change_size((height + self.height_gap, width + self.width_gap))  # 设置大图显示区域大小
            self.large_image_label.clear_content()
            self.large_image_label.set_pic(pixmap)
            large_image_shape_round_gap = self.large_image_label.show_pic_shape.round_gap
            self.setFixedSize(self.scroll_area_width + width + large_image_shape_round_gap * 2 + self.width_gap + self.large_image_label.shape.width, height + self.height_gap)
            catch = self.scroll_area.labels[index].info
            pic_info_dict = self.scroll_area.labels[index].print
            if catch[0] == None:
                pic_name = os.path.basename(photo_path)
            else:
                pic_name = catch[0] + self.save_formate
            if self.this_index % 2 == 0:
                self.large_image_label.row_zero.pic_name_lineedit.setText(pic_name)
                self.large_image_label.row_one.pic_name_lineedit.setReadOnly(False)
                self.large_image_label.row_two.pic_name_lineedit.setReadOnly(False)
                self.large_image_label.row_four.pic_name_lineedit.setReadOnly(False)
                self.large_image_label.row_four.rigin_combobox.setEnabled(True)
                self.large_image_label.row_two.change_button.setEnabled(True)
                # self.large_image_label.row_six.all_moved_button.setEnabled(True)
                if catch[7] != '香港':
                    self.large_image_label.row_two.two_pic_name_lineedit.setReadOnly(False)
                    self.large_image_label.row_five.pic_name_lineedit.setReadOnly(False)
                else:
                    self.large_image_label.row_two.two_pic_name_lineedit.setReadOnly(True)
                    self.large_image_label.row_five.pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_six.pic_name_lineedit.setReadOnly(False)
                self.large_image_label.row_nine.comfire_info_button.setEnabled(True)
            else:
                pic_name = pic_name.rsplit('.', maxsplit=1)[0]
                if catch[0] != None:
                    self.large_image_label.row_zero.pic_name_lineedit.setText(pic_name + '反' + self.save_formate)
                else:
                    self.large_image_label.row_zero.pic_name_lineedit.setText(pic_name + self.save_formate)
                self.large_image_label.row_one.pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_two.pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_two.two_pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_four.pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_five.pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_four.rigin_combobox.setDisabled(True)
                self.large_image_label.row_six.pic_name_lineedit.setReadOnly(True)
                self.large_image_label.row_nine.comfire_info_button.setDisabled(True)
                self.large_image_label.row_two.change_button.setDisabled(True)
                # self.large_image_label.row_six.all_moved_button.setDisabled(True)
            self.change_info()
            self.large_image_label.row_seven.pic_name_lineedit.setPlainText('\n'.join(pic_info_dict))
            self.large_image_label.row_four.rigin_combobox.setCurrentText(self.scroll_area.labels[self.this_index].info[7])
            self.scroll_area.scroll_to_label(self.this_index)
            self.display_flag = False
            self.move_to_moren_position(self.scroll_area.labels[index].info[7])

    def confirm_selection(self):
        self.large_image_label.row_eight.confire_all_button.setDisabled(True)
        try:
            if len(self.scroll_area.labels) == len(self.checked) * 2 and len(self.checked) != 0:
                self.hide()
                self.show_info.set_show_text('正在保存照片，请稍等...')
                self.show_info.show()
                #强制执行上面的语句
                QApplication.processEvents()
                catch_days = self.global_config['catch_days']
                if not (isinstance(catch_days, int) and catch_days >= 0):
                    catch_days == 0
                today_floader = check_catch_pic(catch_days)
                for index, label in enumerate(self.scroll_area.labels):
                    catch = label.info
                    if index % 2 == 1 or catch[0] == '未识别出来':
                        continue
                    name = catch[0]
                    image = label.img
                    borders = self.scroll_area.labels[index].borders
                    if len(borders) != 0:
                        img_border = add_edge(image, 
                                            self.angle_rate,
                                            label.edge_ipx,
                                            label.edge_color,
                                            borders)
                    else:
                        img_border = image
                    cv_imwrite(img_border, self.save_formate, os.path.join(self.cut_save_floader, f'{name}{self.save_formate}'))
                    shutil.copy(os.path.join(self.cut_save_floader, f'{name}{self.save_formate}'),
                                os.path.join(today_floader, f'{name}{self.save_formate}'))
                    image_back = self.scroll_area.labels[index + 1].img
                    borders = self.scroll_area.labels[index + 1].borders
                    if len(borders) != 0:
                        img_border = add_edge(image_back, 
                                            self.angle_rate,
                                            self.scroll_area.labels[index + 1].edge_ipx,
                                            self.scroll_area.labels[index + 1].edge_color,
                                            borders)
                    else:
                        img_border = image_back
                    cv_imwrite(img_border, self.save_formate, os.path.join(self.cut_save_floader, f'{name}反{self.save_formate}'))
                    shutil.copy(os.path.join(self.cut_save_floader, f'{name}反{self.save_formate}'),
                                os.path.join(today_floader, f'{name}反{self.save_formate}'))
                    #检查未识别出来nation的人的地址和民族
                    if catch[2] == '无' and catch[4] == '无' and catch[7] != '香港':
                        catch[7] = '香港'
                    birth = check.card_info_check['生日'](catch[3])
                    if birth == None:
                        birth = catch[3]
                    if catch[7] != "香港":
                        nation = check.card_info_check['民族'](catch[2])
                        if nation == None:
                            nation = catch[2]
                        temp_dict = dict(
                            姓名 = catch[0],
                            性别 = catch[1],
                            民族 = nation,
                            出生日期 = birth,
                            住址 = catch[4],
                            身份证号码 = catch[5],
                            有效期 = catch[6],
                            籍贯 = catch[7]
                        )
                    else:
                        temp_dict = dict(
                            姓名 = catch[0],
                            性别 = catch[1],
                            出生日期 = birth,
                            身份证号码 = catch[5],
                            有效期 = catch[6],
                            籍贯 = catch[7]
                        )
                    with open(os.path.join(self.cut_save_floader, f'{name}.info'), 'w', encoding='utf-8') as writer:
                        line = json.dumps(temp_dict, ensure_ascii=False) + '\n'
                        writer.write(line)
                    shutil.copy(os.path.join(self.cut_save_floader, f'{name}.info'),
                                os.path.join(today_floader, f'{name}.info'))
                    gaopin_mode = self.scroll_area.labels[index].add_to_gaopin
                    if gaopin_mode:
                        shutil.copy(os.path.join(self.cut_save_floader, f'{name}{self.save_formate}'),
                                    os.path.join(self.gaopin_path, f'{name}{self.save_formate}'))
                        shutil.copy(os.path.join(self.cut_save_floader, f'{name}反{self.save_formate}'),
                                    os.path.join(self.gaopin_path, f'{name}反{self.save_formate}'))
                        shutil.copy(os.path.join(self.cut_save_floader, f'{name}.info'),
                                    os.path.join(self.gaopin_path, f'{name}.info'))
                if os.path.exists(os.path.join(self.cut_save_floader, '截图后')):
                    send2trash(os.path.join(self.cut_save_floader, '截图后'))
                self.reopen_main_window()
                duration = self.global_config['show_tip_timer_duration']
                if duration > 0:
                    self.show_info.set_show_text('照片编辑完成')
                    self.show_info.show()
                    self.combbox_change_tips_timer.start(duration)
                self.close_flag = False
                if self.thread_pool != None:
                    self.thread_pool.clear()
                if duration <= 0:
                    self.close()
            else:
                if len(self.checked) == 0:
                    show_str = f'还没确认任何正面图片的确认文字按钮，或者点击跳过检查，你需要确认全部正面照片文字信息才可以结束。'
                else:
                    compare = list(range(len(self.scroll_area.labels)))
                    compare = [i for i in compare if i % 2 == 0]
                    compare = [int(i/2) for i in compare]
                    check_t = [int(i/2) for i in self.checked]
                    no_check = list(set(compare) - set(check_t))
                    no_check = sorted(list(no_check), reverse=False)
                    str_t = ','.join([str(i + 1) for i in no_check])
                    show_str = f'第{str_t}组照片的正面还没点击确认文字按钮，需要全部确认信息，或点击跳过检查按钮。'
                self.show_info.set_show_text(show_str)
                self.show_info.show()
            self.large_image_label.row_eight.confire_all_button.setEnabled(True)
        except:
            self.large_image_label.row_eight.confire_all_button.setEnabled(True)

    def function_confire(self):
        if self.this_index != None:
            if self.this_index not in self.checked:
                self.checked.append(self.this_index)
            if self.this_index != len(self.scroll_area.labels) - 2:
                self.display_large_image(self.scroll_area.labels[self.this_index + 2].photo_path, self.this_index + 2)
                self.change_info()

    def change_liangdu_and_duibidu(self, change_mode, crase_mode):
        if self.this_index != None:
            liangdu_gep = 0.05
            duibidu_gap = 0.1
            pic_path = self.scroll_area.labels[self.this_index].photo_path
            liangdu_shift = self.scroll_area.labels[self.this_index].liangdu_shift
            duibidu_shift = self.scroll_area.labels[self.this_index].duibidu_shift
            image = cv_imread(pic_path)
            if change_mode == 0:
                if crase_mode == 0:
                    liangdu_shift += liangdu_gep
                else:
                    if liangdu_shift > liangdu_gep:
                        liangdu_shift -= liangdu_gep
            else:
                if crase_mode == 0:
                    duibidu_shift += duibidu_gap
                else:
                    if duibidu_shift > duibidu_gap:
                        duibidu_shift -= duibidu_gap
            self.scroll_area.labels[self.this_index].liangdu_shift = liangdu_shift
            self.scroll_area.labels[self.this_index].duibidu_shift = duibidu_shift
            if liangdu_shift != 1.0 or duibidu_shift != 1.0:
                #转换为PIL格式
                image = PILImagefromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                if liangdu_shift != 1.0:
                    self.liangdu_origin = True
                    enhancer_liangdu = PILImageEnhanceBrightness(image)
                    image = enhancer_liangdu.enhance(liangdu_shift)
                if duibidu_shift != 1.0:
                    enhancer = PILImageEnhanceContrast(image)
                    image = enhancer.enhance(duibidu_shift)
                # 转回 OpenCV 格式（numpy 数组）
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            if not self.scroll_area.labels[self.this_index].color:
                image = rgb_to_gray_with_three_channels(image)
            self.scroll_area.labels[self.this_index].img = image
            borders = self.scroll_area.labels[self.this_index].borders
            if len(borders) != 0:
                img_border = add_edge(image, 
                                      self.angle_rate,
                                      self.scroll_area.labels[self.this_index].edge_ipx,
                                      self.scroll_area.labels[self.this_index].edge_color,
                                      borders)
            else:
                img_border = image
            pixmap = cv_to_qpixmap(img_border)
            #显示大图
            self.large_image_label.set_pic(pixmap)
            self.large_image_label.update()
            #显示小图
            fixed_width = self.fixed_width
            scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
            scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
            self.scroll_area.scroll_to_label(self.this_index)

    def change_text(self, index):
        cue = card_info_key_check[index]
        if self.this_index != None:
            if self.this_index % 2 == 0:
                obj_now = self.obj_index[index]
                if isinstance(obj_now, QLineEdit):
                    text_now = obj_now.text().replace(' ', '').replace('\u2009', '').replace('\n', '')
                    type_t = 'QLineEdit'
                elif isinstance(obj_now, QPlainTextEdit):
                    type_t = 'QPlainTextEdit'
                    text_now = obj_now.toPlainText().replace(' ', '').replace('\u2009', '').replace('\n', '')
                self.scroll_area.labels[self.this_index].info[index] = text_now
                self.scroll_area.labels[self.this_index + 1].info[index] = text_now
                if cue == '姓名':
                    self.large_image_label.row_zero.pic_name_lineedit.setText(text_now + self.save_formate)
                if text_now == "未" or text_now == '未识别出来':
                    if not self.global_config['check_back'] and cue == '有效期':
                        self.large_image_label.row_six_seven.pic_name_lineedit.setText('未开启日期检查，若无问题请跳过')
                        color = self.global_config['paddleocr_conf']['color']['check']
                    else:
                        color = self.global_config['paddleocr_conf']['color']['error']
                else:
                    if text_now != '无':
                        text = check.card_info_check[cue](text_now, self.scroll_area.labels[self.this_index].info[7])
                    else:
                        text = text_now
                    if text != None or text == '无':
                        #背景花纹可能检测为‘上’，变为检查颜色，注意检查
                        if cue == '住址':
                            if text.lstrip()[0] in self.address_front_check or any(m in text for m in self.address_check):
                                color = self.global_config['paddleocr_conf']['color']['check']
                            else:
                                color = self.global_config['paddleocr_conf']['color']['right']
                        elif cue == '有效期':
                            if isinstance(text, list):
                                self.large_image_label.row_six_seven.pic_name_lineedit.setText('有效期剩' + str(text[0]) + '天')
                                color = self.global_config['paddleocr_conf']['color']['error']
                            elif text == '1':
                                self.large_image_label.row_six_seven.pic_name_lineedit.setText('未开启日期检查，若无问题请跳过')
                                color = self.global_config['paddleocr_conf']['color']['check']
                            elif text == '3':
                                self.large_image_label.row_six_seven.pic_name_lineedit.setText('身份证已过期！')
                                color = self.global_config['paddleocr_conf']['color']['error']
                            else:
                                color = self.global_config['paddleocr_conf']['color']['right']
                        else:
                            color = self.global_config['paddleocr_conf']['color']['right']
                    else:
                        color = self.global_config['paddleocr_conf']['color']['error']
                if obj_now.moved_flag:
                    obj_now.setStyleSheet(f'{type_t}{{background-color: rgba(255, 255, 255, 0);border: none;color:{color};}}QToolTip{{background-color: white;color: black;border: 1px solid black;font-size: 12px;}}')
                else:
                    obj_now.setStyleSheet(f"{type_t}{{border-width: 1px;border-style: solid;border-color: black;background-color:white;color: {color};}}QToolTip{{background-color: white;color: black;border: 1px solid black;font-size: 12px;}}")

    def confire_all(self):
        if self.this_index != None:
            compare = list(range(len(self.scroll_area.labels)))
            checked_all = [i for i in compare if i % 2 == 0]
            for i in checked_all:
                if i not in self.checked:
                    self.checked.append(i)

    def closeEvent(self, event):
        if self.close_flag:
            self.reopen_main_window()
        if self.thread_pool != None:
            self.thread_pool.clear()
        self.deleteLater()
        self.close()

    def black_short_press(self):
        if self.this_index != None:
            if self.this_index != None:
                self.scroll_area.labels[self.this_index].color = not self.scroll_area.labels[self.this_index].color
                photo_path = self.scroll_area.labels[self.this_index].photo_path
                image = cv_imread(photo_path)
                liangdu_shift = self.scroll_area.labels[self.this_index].liangdu_shift
                duibidu_shift = self.scroll_area.labels[self.this_index].duibidu_shift
                if liangdu_shift != 1.0 or duibidu_shift != 1.0:
                    #转换为PIL格式
                    image = PILImagefromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    if liangdu_shift != 1.0:
                        self.liangdu_origin = True
                        enhancer_liangdu = PILImageEnhanceBrightness(image)
                        image = enhancer_liangdu.enhance(liangdu_shift)
                    if duibidu_shift != 1.0:
                        enhancer = PILImageEnhanceContrast(image)
                        image = enhancer.enhance(duibidu_shift)
                    # 转回 OpenCV 格式（numpy 数组）
                    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                if not self.scroll_area.labels[self.this_index].color:
                    image = rgb_to_gray_with_three_channels(image)
                self.scroll_area.labels[self.this_index].img = image
                borders = self.scroll_area.labels[self.this_index].borders
                if len(borders) != 0:
                    img_border = add_edge(image, 
                                      self.angle_rate,
                                      self.scroll_area.labels[self.this_index].edge_ipx,
                                      self.scroll_area.labels[self.this_index].edge_color,
                                        borders)
                else:
                    img_border = image
                pixmap = cv_to_qpixmap(img_border)
                #显示大图
                self.large_image_label.set_pic(pixmap)
                self.large_image_label.update()
                #显示小图
                fixed_width = self.fixed_width
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
                self.scroll_area.scroll_to_label(self.this_index)

    def black_long_press(self):
        if self.this_index != None:
            if self.black_is_pressed:
                self.black_is_pressed = False
                color_flag = True
                for label in self.scroll_area.labels:
                    if label.color:
                        color_flag = False
                        break
                for index, label in enumerate(self.scroll_area.labels):
                    color_before = label.color
                    label.color = color_flag
                    if color_flag != color_before:
                        liangdu_shift = label.liangdu_shift
                        duibidu_shift = label.duibidu_shift
                        image = cv_imread(label.photo_path)
                        if liangdu_shift != 1.0 or duibidu_shift != 1.0:
                            #转换为PIL格式
                            image = PILImagefromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                            if liangdu_shift != 1.0:
                                self.liangdu_origin = True
                                enhancer_liangdu = PILImageEnhanceBrightness(image)
                                image = enhancer_liangdu.enhance(liangdu_shift)
                            if duibidu_shift != 1.0:
                                enhancer = PILImageEnhanceContrast(image)
                                image = enhancer.enhance(duibidu_shift)
                            # 转回 OpenCV 格式（numpy 数组）
                            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                        if not color_flag:
                            image = rgb_to_gray_with_three_channels(image)
                        label.img = image
                        borders = label.borders
                        if len(borders) != 0:
                            img_border = add_edge(image, 
                                      self.angle_rate,
                                      label.edge_ipx,
                                      label.edge_color,
                                                borders)
                        else:
                            img_border = image
                        pixmap = cv_to_qpixmap(img_border)
                        #显示小图
                        fixed_width = self.fixed_width
                        scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                        scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                        self.scroll_area.labels[index].setPixmap(scaled_pixmap)
                        if index == self.this_index:
                            #显示大图
                            self.large_image_label.set_pic(pixmap)
                            self.large_image_label.update()
                self.scroll_area.scroll_to_label(self.this_index)

    def init_black_button_timer(self):
        self.black_timer = QTimer()
        self.black_timer.setSingleShot(True)
        self.black_timer.timeout.connect(self.black_long_press)
        self.black_is_pressed = False

    def black_pressed(self):
        self.black_is_pressed = True
        self.black_timer.start(self.global_config['button_timer_duration'])

    def black_released(self):
        if self.black_is_pressed:
            self.black_is_pressed = False
            self.black_short_press()
            self.black_timer.stop()

    def change_save_to_gaopin_mode(self):
        if self.this_index != None:
            mode = self.scroll_area.labels[self.this_index].add_to_gaopin
            self.scroll_area.labels[self.this_index].add_to_gaopin = not mode
            if self.this_index % 2 == 0:
                self.scroll_area.labels[self.this_index + 1].add_to_gaopin = not mode
            else:
                self.scroll_area.labels[self.this_index - 1].add_to_gaopin = not mode
            if not mode:
                self.large_image_label.row_three.match_liangdu_button.setText("取消加入高频")
                self.large_image_label.row_three.match_liangdu_button.setToolTip('取消将这组照片和信息添加到高频信息里')
            else:
                self.large_image_label.row_three.match_liangdu_button.setText("加入高频")
                self.large_image_label.row_three.match_liangdu_button.setToolTip('将这组照片和信息添加到高频信息里')

    def init_combbox_change_tips_timer(self):
        self.combbox_change_tips_timer = QTimer()
        self.combbox_change_tips_timer.setSingleShot(True)
        self.combbox_change_tips_timer.timeout.connect(self.change_tip)

    def change_tip(self):
        self.show_info.hide()
        self.close()

    def change_borders(self, mode):
        if self.this_index != None:
            now_borders = copy.deepcopy(self.scroll_area.labels[self.this_index].borders)
            if mode != 9:
                if mode in now_borders:
                    now_borders.remove(mode)
                else:
                    now_borders.append(mode)
                self.scroll_area.labels[self.this_index].borders = now_borders
            else:
                if len(now_borders) != 8:
                    self.scroll_area.labels[self.this_index].borders = list(range(1, 9))
                else:
                    self.scroll_area.labels[self.this_index].borders = []
            now_borders = self.scroll_area.labels[self.this_index].borders
            if len(now_borders) != 0:
                image = self.scroll_area.labels[self.this_index].img
                img_border = add_edge(image, 
                                      self.angle_rate,
                                      self.scroll_area.labels[self.this_index].edge_ipx,
                                      self.scroll_area.labels[self.this_index].edge_color,
                                        now_borders)
            else:
                img_border = self.scroll_area.labels[self.this_index].img
            pixmap = cv_to_qpixmap(img_border)
            #显示大图
            self.large_image_label.set_pic(pixmap)
            self.large_image_label.update()
            #显示小图
            fixed_width = self.fixed_width
            scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
            scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
            self.scroll_area.scroll_to_label(self.this_index)

    def change_edge_ipx(self, mode):
        if self.this_index != None:
            ipx_or = self.scroll_area.labels[self.this_index].edge_ipx
            if mode == 0:
                ipx = min(ipx_or + 1, self.angle_rate)
            else:
                ipx = max(ipx_or - 1, 1)
            now_borders = self.scroll_area.labels[self.this_index].borders
            if len(now_borders) != 0 and ipx_or != ipx:
                self.scroll_area.labels[self.this_index].edge_ipx = ipx
                image = self.scroll_area.labels[self.this_index].img
                img_border = add_edge(image, 
                                      self.angle_rate,
                                      ipx,
                                      self.scroll_area.labels[self.this_index].edge_color,
                                      now_borders)
                pixmap = cv_to_qpixmap(img_border)
                #显示大图
                self.large_image_label.set_pic(pixmap)
                self.large_image_label.update()
                #显示小图
                fixed_width = self.fixed_width
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
                self.scroll_area.scroll_to_label(self.this_index)

    def change_edge_color(self):
        if self.this_index != None and not self.display_flag:
            index = self.large_image_label.row_four.border_color_combobox.currentIndex()
            color = tuple([index * 50] * 3)
            self.scroll_area.labels[self.this_index].edge_color = color
            now_borders = self.scroll_area.labels[self.this_index].borders
            if len(now_borders) != 0:
                image = self.scroll_area.labels[self.this_index].img
                img_border = add_edge(image, 
                                      self.angle_rate,
                                      self.scroll_area.labels[self.this_index].edge_ipx,
                                      color,
                                      now_borders)
                pixmap = cv_to_qpixmap(img_border)
                #显示大图
                self.large_image_label.set_pic(pixmap)
                self.large_image_label.update()
                #显示小图
                fixed_width = self.fixed_width
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
                self.scroll_area.scroll_to_label(self.this_index)

    def move_to_moren_position(self, mode = 0):
        if self.this_index % 2 == 0:
            if self.position_mode:
                if mode != self.previous_nation:
                    change_nation_flag = True
                    self.previous_nation = mode
                else:
                    change_nation_flag = False
                if mode == '香港':
                    mode = 2
                elif mode == '内地':
                    mode = 1
            else:
                change_nation_flag = True
                mode = 0
        else:
            change_nation_flag = True
            mode = 0
        for obj in self.obj_index:
            if not obj.moved_flag or change_nation_flag:
                obj.change_pos(mode)

    def change_moren_position_mode(self):
        self.position_mode = int(not self.position_mode)
        self.large_image_label.row_six.all_moved_button.setText(self.position_mode_text[not self.position_mode])
        self.move_to_moren_position(self.scroll_area.labels[self.this_index].info[7])

    def change_regin(self):
        if self.this_index % 2 == 0:
            regin = self.large_image_label.row_four.rigin_combobox.currentText()
            self.scroll_area.labels[self.this_index].info[7] = regin
            self.scroll_area.labels[self.this_index + 1].info[7] = regin
            if regin == '香港':
                mode = 2
            elif regin == '内地':
                mode = 1
            for obj in self.obj_index:
                if obj.moved_flag or self.position_mode:
                    obj.change_pos(mode)

    def read_cut_info(self, obj:ClickableLabel):
        index = obj.index
        photo_path = obj.photo_path
        img = obj.img
        liangdu_shift = obj.liangdu_shift
        duibidu_shift = obj.duibidu_shift
        color = obj.color
        edge_ipx = obj.edge_ipx
        add_to_gaopin = obj.add_to_gaopin
        borders = obj.borders
        edge_color = obj.edge_color
        return index, photo_path, img, liangdu_shift, duibidu_shift, color, edge_ipx, add_to_gaopin, borders, edge_color

    def write_cut_info(self, obj:ClickableLabel, index, photo_path, img, liangdu_shift, duibidu_shift, color, edge_ipx, add_to_gaopin, borders, edge_color):
        obj.index = index
        obj.photo_path = photo_path
        obj.img = img
        obj.liangdu_shift = liangdu_shift
        obj.duibidu_shift = duibidu_shift
        obj.color = color
        obj.edge_ipx = edge_ipx
        obj.add_to_gaopin = add_to_gaopin
        obj.borders = borders
        obj.edge_color = edge_color
        return obj

    def change_pic_position(self):
        if self.this_index != None:
            self.large_image_label.row_two.change_button.setDisabled(True)
            self.first_index = int(self.this_index / 2 ) * 2
            temp_path = self.photo_paths[self.first_index + 1]
            temp_path_back = self.photo_paths[self.first_index]
            cut_shape = self.global_config['paddleocr_conf']['screen_correct']
            self.photo_paths[self.first_index + 1] = self.photo_paths[self.first_index]
            self.photo_paths[self.first_index] = temp_path
            if self.first_index in self.checked:
                self.checked.remove(self.first_index)
            _, photo_path, img, liangdu_shift, duibidu_shift, color, edge_ipx, add_to_gaopin, borders, edge_color = self.read_cut_info(self.scroll_area.labels[self.first_index])
            _, photo_path1, img1, liangdu_shift1, duibidu_shift1, color1, edge_ipx1, add_to_gaopin1, borders1, edge_color1 = self.read_cut_info(self.scroll_area.labels[self.first_index + 1])
            self.scroll_area.labels[self.first_index] = self.write_cut_info(self.scroll_area.labels[self.first_index], self.first_index, photo_path1, img1, liangdu_shift1, duibidu_shift1, color1, edge_ipx1, add_to_gaopin1, borders1, edge_color1)
            self.scroll_area.labels[self.first_index + 1] = self.write_cut_info(self.scroll_area.labels[self.first_index + 1], self.first_index + 1, photo_path, img, liangdu_shift, duibidu_shift, color, edge_ipx, add_to_gaopin, borders, edge_color)
            
            for index in [self.first_index, self.first_index + 1]:
                show_borders = self.scroll_area.labels[index].borders
                if len(show_borders) != 0:
                    img_border = add_edge(self.scroll_area.labels[index].img, 
                                            self.angle_rate,
                                            self.scroll_area.labels[index].edge_ipx,
                                            self.scroll_area.labels[index].edge_color,
                                            show_borders)
                else:
                    img_border = self.scroll_area.labels[index].img
                pixmap = cv_to_qpixmap(img_border)
                #显示大图
                if index == self.first_index:
                    self.large_image_label.set_pic(pixmap)
                    self.large_image_label.update()
                #显示小图
                fixed_width = self.fixed_width
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[index].setPixmap(scaled_pixmap)
                self.scroll_area.scroll_to_label(index)

            self.large_image_label.row_four.border_color_combobox.setCurrentIndex(int(edge_color1[0] / 50))
            self.ocr_model = get_ocr_model(self.global_config)
            self.thread_pool = QThreadPool.globalInstance()
            self.thread_pool.setMaxThreadCount(self.global_config['paddleocr_conf']['max_threads'])
            img = cv_imread(temp_path)
            h, w = img.shape[:2]
            ocr_thread = Get_Ocr(cv2.vconcat([cv_imread(temp_path_back)[int(h * cut_shape[2]) : int(h * cut_shape[3]), int(w * cut_shape[4]) : int(w * cut_shape[5])], img[int(h * cut_shape[0]) : int(h * cut_shape[1]), int(w * cut_shape[6]) : int(w * cut_shape[7])]]),
                                    self.ocr_model, temp_path, scale=copy.copy(self.global_config['paddleocr_conf']['scale']), 
                                    pic_shape=tuple(self.global_config['mlsd_conf']['pic_shape']), 
                                    times=self.global_config['paddleocr_conf']['times'], 
                                    pic_type=self.global_config['paddleocr_conf']['ocr_pic_type'],
                                    info_checks=self.global_config['paddleocr_conf']['info_checks'],
                                    one_line_scale=self.global_config['paddleocr_conf']['one_line_scale'],
                                    check_back=self.global_config['check_back'])
            ocr_thread.signals.finished.connect(self.single_end_ocr)  # 把任务完成的信号与任务完成后处理的槽函数绑定
            self.thread_pool.start(ocr_thread)

    def single_end_ocr(self, catch, pic_info_dict, _):
        for index in [self.first_index, self.first_index + 1]:
            self.scroll_area.labels[index].info = catch
            self.scroll_area.labels[index].print = pic_info_dict
        self.change_info()
        regin = catch[7]
        if regin == '香港':
            self.large_image_label.row_four.rigin_combobox.setCurrentText('香港')
        elif regin == '内地':
            self.large_image_label.row_four.rigin_combobox.setCurrentText('内地')
        self.release()
        clear_gpu_cache()
        self.large_image_label.row_two.change_button.setEnabled(True)

    def disable_add_border(self):
        self.large_image_label.row_zero.border_width_plus_button.hide()
        self.large_image_label.row_zero.border_up_left_button.hide()
        self.large_image_label.row_zero.border_up_button.hide()
        self.large_image_label.row_zero.border_up_right_button.hide()
        self.large_image_label.row_one.border_width_minues_pushbutton.hide()
        self.large_image_label.row_one.border_left_button.hide()
        self.large_image_label.row_one.border_right_button.hide()
        self.large_image_label.row_one.border_all_pushbutton.hide()
        self.large_image_label.row_two.border_down_left_button.hide()
        self.large_image_label.row_two.border_down_button.hide()
        self.large_image_label.row_two.border_down_right_button.hide()
        self.large_image_label.row_four.border_color_combobox.hide()
        self.large_image_label.row_zero.enable_border_button.show()

    def enable_add_border(self):
        self.large_image_label.row_zero.enable_border_button.hide()
        self.large_image_label.row_zero.border_width_plus_button.show()
        self.large_image_label.row_zero.border_up_left_button.show()
        self.large_image_label.row_zero.border_up_button.show()
        self.large_image_label.row_zero.border_up_right_button.show()
        self.large_image_label.row_one.border_width_minues_pushbutton.show()
        self.large_image_label.row_one.border_left_button.show()
        self.large_image_label.row_one.border_right_button.show()
        self.large_image_label.row_one.border_all_pushbutton.show()
        self.large_image_label.row_two.border_down_left_button.show()
        self.large_image_label.row_two.border_down_button.show()
        self.large_image_label.row_two.border_down_right_button.show()
        self.large_image_label.row_four.border_color_combobox.show()

    def init_event(self):
        self.init_black_button_timer()
        self.init_combbox_change_tips_timer()
        self.large_image_label.row_nine.comfire_info_button.clicked.connect(self.function_confire)
        self.large_image_label.row_eight.liangdu_plus_button.clicked.connect(lambda: self.change_liangdu_and_duibidu(0, 0))
        self.large_image_label.row_nine.liangdu_minues_button.clicked.connect(lambda: self.change_liangdu_and_duibidu(0, 1))
        self.large_image_label.row_eight.duibidu_plus_button.clicked.connect(lambda: self.change_liangdu_and_duibidu(1, 0))
        self.large_image_label.row_nine.duibidu_minues_button.clicked.connect(lambda: self.change_liangdu_and_duibidu(1, 1))
        self.large_image_label.row_one.pic_name_lineedit.textChanged.connect(lambda: self.change_text(0))
        self.large_image_label.row_two.pic_name_lineedit.textChanged.connect(lambda: self.change_text(1))
        self.large_image_label.row_two.two_pic_name_lineedit.textChanged.connect(lambda: self.change_text(2))
        self.large_image_label.row_four.pic_name_lineedit.textChanged.connect(lambda: self.change_text(3))
        self.large_image_label.row_five.pic_name_lineedit.textChanged.connect(lambda: self.change_text(4))
        self.large_image_label.row_six.pic_name_lineedit.textChanged.connect(lambda: self.change_text(5))
        self.large_image_label.row_six_seven.pic_name_lineedit.textChanged.connect(lambda: self.change_text(6))
        self.large_image_label.row_eight.confire_all_button.clicked.connect(self.confirm_selection)
        self.large_image_label.row_three.black_button.pressed.connect(self.black_pressed)
        self.large_image_label.row_three.black_button.released.connect(self.black_released)
        self.large_image_label.row_three.skip_button.clicked.connect(self.confire_all)
        self.large_image_label.row_three.match_liangdu_button.clicked.connect(self.change_save_to_gaopin_mode)
        self.large_image_label.row_zero.border_up_left_button.clicked.connect(lambda: self.change_borders(8))
        self.large_image_label.row_zero.border_up_button.clicked.connect(lambda: self.change_borders(1))
        self.large_image_label.row_zero.border_up_right_button.clicked.connect(lambda: self.change_borders(2))
        self.large_image_label.row_one.border_left_button.clicked.connect(lambda: self.change_borders(7))
        # self.large_image_label.row_one.border_all_pushbutton.clicked.connect(lambda: self.change_borders(9))
        self.large_image_label.row_one.border_right_button.clicked.connect(lambda: self.change_borders(3))
        self.large_image_label.row_two.border_down_left_button.clicked.connect(lambda: self.change_borders(6))
        self.large_image_label.row_two.border_down_button.clicked.connect(lambda: self.change_borders(5))
        self.large_image_label.row_two.border_down_right_button.clicked.connect(lambda: self.change_borders(4))
        self.large_image_label.row_zero.border_width_plus_button.clicked.connect(lambda: self.change_edge_ipx(0))
        self.large_image_label.row_one.border_all_pushbutton.clicked.connect(self.disable_add_border)
        self.large_image_label.row_zero.enable_border_button.clicked.connect(self.enable_add_border)
        self.large_image_label.row_one.border_width_minues_pushbutton.clicked.connect(lambda: self.change_edge_ipx(1))
        self.large_image_label.row_four.border_color_combobox.currentIndexChanged.connect(self.change_edge_color)
        self.large_image_label.row_four.rigin_combobox.currentIndexChanged.connect(self.change_regin)
        self.large_image_label.row_six.all_moved_button.clicked.connect(self.change_moren_position_mode)
        self.large_image_label.row_two.change_button.clicked.connect(self.change_pic_position)
