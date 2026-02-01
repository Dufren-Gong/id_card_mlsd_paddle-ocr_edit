import os, cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon
from my_utils.utils import get_all_pic_path, cv_imread, get_mask, add_mask, cv_imwrite, pic_rotate_angle, cv_to_qpixmap, point_rotate_90, calculate_distance, get_internal_path, calc_no_line_number
from PyQt6.QtCore import Qt, QThreadPool
from uis.photo_gallery_ui.scroll_area_for_cut import Scroll_Area, ClickableLabel  # 导入 Scroll_Area 模块
from windows.show_info_window import Show_Info_Window
from windows.show_pic_window import Show_Pic_Window
from my_utils.threads import Get_line_detect
from my_utils.mlsd_scan import release_model, get_model
import numpy as np

class Cut_Pic(QMainWindow):
    def __init__(self, global_config, cut_save_floader, save_formate, id_shape, reopen_main_window, pre_next_step, show_info:Show_Info_Window=None):
        super().__init__()
        self.id_shape = id_shape
        self.global_config = global_config
        self.cut_save_floader = cut_save_floader
        self.save_formate = save_formate
        self.pre_next_step = pre_next_step
        self.reopen_main_window = reopen_main_window
        self.viewed = []
        self.show_info = show_info
        self.width_gap = 55
        self.height_gap = 40
        self.fixed_width = self.global_config['mlsd_conf']['small_pic_fixed_width']
        self.angle_rate = self.global_config['mlsd_conf']['angle_rate']
        self.zheng_fan_shift = self.global_config['mlsd_conf']['zheng_fan_shift']
        self.this_index = None
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(self.global_config['mlsd_conf']['max_threads'])
        screen_size = QApplication.primaryScreen().size()
        self.max_size = (int(screen_size.width()*0.8), int(screen_size.height()*0.8))
        self.setWindowTitle("点击确认所有之前，所有正面照在前，且摆正")
        self.setGeometry(0, 0, 800, 600)
        self.setWindowIcon(QIcon(get_internal_path('../files/icon/icon.ico')))
        # 创建主布局，水平布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)  # 控件之间的间距为10像素
        main_layout.setContentsMargins(10, 10, 10, 10)  # 布局的外边距为10像素
        self.scroll_area_width = self.fixed_width + 30
        # 创建 Scroll_Area 实例
        self.scroll_area = Scroll_Area(self.global_config, width_t=self.scroll_area_width, display_large_image_function=self.display_large_image)
        self.scroll_area.setFixedWidth = self.scroll_area_width
        # 创建 QLabel 用于显示大图
        self.large_image_label = Show_Pic_Window(show_info, global_config)
        self.large_image_label.points_updated.connect(self.handle_points_updated)
        main_layout = QHBoxLayout()

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

    def release(self):
        self.thread_pool = None
        self.line_detect_model = None
        self.model_large = None

    def closeEvent(self, event):
        if self.close_flag:
            self.reopen_main_window()
        if self.thread_pool != None:
            self.thread_pool.clear()
        self.deleteLater()
        self.close()

    def handle_points_updated(self, new_points):
        try:
            scale = self.scroll_area.labels[self.this_index].scale
            self.scroll_area.labels[self.this_index].moved_flag = True
            self.scroll_area.labels[self.this_index].max_flag = False
            self.scroll_area.labels[self.this_index].points = self.merge_scaled_dot(new_points, 1 / scale)
        except:
            pass

    def init_model_and_device(self):
        self.line_detect_model, self.model_large = get_model(self.global_config)
        gap = 2
        groups = int(len(self.photo_paths) / gap)
        params={'score': self.global_config['mlsd_conf']['score'],
                'outside_ratio': self.global_config['mlsd_conf']['outside_ratio'],
                'inside_ratio': self.global_config['mlsd_conf']['inside_ratio'],
                'w_overlap': self.global_config['mlsd_conf']['w_overlap'],
                'w_degree': self.global_config['mlsd_conf']['w_degree'],
                'w_length': self.global_config['mlsd_conf']['w_length'],
                'w_area': self.global_config['mlsd_conf']['w_area'],
                'w_center': self.global_config['mlsd_conf']['w_center'],
                'top_n': self.global_config['mlsd_conf']['top_n'],
                'pic_remode': 0,
                'duibidu_shift': self.global_config['mlsd_conf']['duibidu_shift']}
        max_t_arr = [self.global_config['mlsd_conf']['tiny_max_input_size'], self.global_config['mlsd_conf']['large_max_input_size']]
        for i in range(groups):
            pair = self.photo_paths[i * gap: (i + 1)*gap]
            cv_pairs = []
            scales = []
            for p in pair:
                cv_img = cv_imread(p)
                cv_pairs.append(cv_img)
                height, width, _ = cv_img.shape
                if width > self.max_size[0]:
                    width_scale = self.max_size[0] / width
                else:
                    width_scale = 1
                if height > self.max_size[1]:
                    height_scale = self.max_size[1] / height
                else:
                    height_scale = 1
                scale = min([width_scale, height_scale])
                scales.append(scale)
            line_detect_thread = Get_line_detect(cv_pairs,
                                                  pair,
                                                  scales, 
                                                  self.line_detect_model, 
                                                  self.model_large, 
                                                  params, 
                                                  max_t_arr, 
                                                  self.global_config['mlsd_conf']['model_type'], 
                                                  tuple(self.global_config['mlsd_conf']['pic_shape']), 
                                                  self.global_config['mlsd_conf']['tiny_first'])
            line_detect_thread.signals.finished.connect(self.end_line_detct)  # 把任务完成的信号与任务完成后处理的槽函数绑定
            self.thread_pool.start(line_detect_thread)

    def end_line_detct(self, cv_pairs, pair_paths, pair_points, max_flags, scales):
        self.scroll_area.add_photos(cv_pairs, pair_paths, pair_points, max_flags, scales)  # 向 Scroll_Area 添加照片
        if self.first_show_flag:
            self.first_show_flag = False
            if self.show_info != None:
                self.show_info.hide()
            self.show()
            QApplication.processEvents()
        if len(self.photo_paths) == len(self.scroll_area.labels):
            self.scroll_area.skip_button.setEnabled(True)
            release_model(self.line_detect_model, self.model_large)
            self.release()

    def load_photos(self, dirs):
        if isinstance(dirs, list):
            self.photo_paths = dirs
        else:
            self.photo_paths = get_all_pic_path(dirs)

    def merge_scaled_dot(self, points, scale):
        if len(points) == 4:
            points_temp = [[]] * 4
            points_temp[0] = [int(points[0][0] * scale), int(points[0][1] * scale)]
            points_temp[1] = [int(points[1][0] * scale), int(points[1][1] * scale)]
            points_temp[2] = [int(points[2][0] * scale), int(points[2][1] * scale)]
            points_temp[3] = [int(points[3][0] * scale), int(points[3][1] * scale)]
            return np.array(points_temp)
        else:
            return points

    def display_large_image(self, index, shou_flag = True, force_show_flag = False, new_scale_flag = False):
        if self.this_index != index or force_show_flag:
            self.large_image_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # 显示正常尺寸的图片
            self.this_index = index
            img = self.scroll_area.labels[index].img
            pixmap = cv_to_qpixmap(img)
            size = pixmap.size()
            width = size.width()
            height = size.height()
            if not new_scale_flag:
                scale = self.scroll_area.labels[index].scale
            else:
                if len(self.scroll_area.labels[index].points) != 0:
                    width_temp = width
                    height_temp = height
                else:
                    img_cache = self.scroll_area.labels[index].img_cache
                    height_temp, width_temp, _ = img_cache.shape
                if width_temp > self.max_size[0]:
                    width_scale = self.max_size[0] / width_temp
                else:
                    width_scale = 1
                if height_temp > self.max_size[1]:
                    height_scale = self.max_size[1] / height_temp
                else:
                    height_scale = 1
                scale_temp = min([width_scale, height_scale])
                if len(self.scroll_area.labels[index].points) != 0:
                    self.scroll_area.labels[index].scale = scale_temp
                    scale = scale_temp
                else:
                    self.scroll_area.labels[index].scale_cache = scale_temp
                    scale = 1
            width = int(width * scale)
            height = int(height * scale)
            self.large_image_label.change_size((height, width))  # 设置大图显示区域大小
            self.large_image_label.clear_content()
            show_points = self.scroll_area.labels[index].points
            self.large_image_label.set_points(self.merge_scaled_dot(show_points, scale), shou_flag)
            self.large_image_label.set_pic(pixmap.scaled(width, height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio))
            large_image_shape_round_gap = self.large_image_label.show_pic_shape.round_gap
            self.setFixedSize(self.scroll_area_width + width + large_image_shape_round_gap * 2 + self.width_gap, height + large_image_shape_round_gap * 2 + self.height_gap)
            if len(self.scroll_area.labels[self.this_index].points) == 0:
                self.scroll_area.confire_this_button.setText('下一张')
            else:
                self.scroll_area.confire_this_button.setText('确认截图')
            self.scroll_area.scroll_to_label(self.this_index)
            self.scroll_area.slider.setValue(self.scroll_area.labels[index].outside_color[0])

    def confirm_selection(self):
        self.scroll_area.confirem_button.setDisabled(True)
        try:
            if (len(self.scroll_area.labels) == len(self.viewed) and len(self.viewed) != 0):
                self.hide()
                self.show_info.set_show_text('正在保存照片，请稍等...')
                self.show_info.show()
                #强制执行上面的语句
                QApplication.processEvents()
                for label in self.scroll_area.labels:
                    index = label.index
                    points = label.points
                    cv_img = label.img
                    if len(points) != 0:
                        cv_img = self.reshape_image(cv_img, points)
                        mask = get_mask(self.angle_rate, cv_img.shape)
                        cv_img = add_mask(cv_img, mask, self.scroll_area.labels[self.this_index].outside_color)
                    cv_imwrite(cv_img, self.save_formate, os.path.join(self.cut_save_floader, f'{index}{self.save_formate}'))
                self.close_flag = False
                if self.thread_pool != None:
                    self.thread_pool.clear()
                self.close()
                self.pre_next_step()
            else:
                if len(self.viewed) == 0:
                    show_str = f'你还没有确认任何截图信息，或点击跳过所有检查按钮，确保调整好位置正面在前反面在后，并且调整好方向。'
                else:
                    compare = list(range(len(self.scroll_area.labels)))
                    no_check = list(set(compare) - set(self.viewed))
                    no_check = sorted(list(no_check), reverse=False)
                    str_t = ','.join([str(i + 1) for i in no_check])
                    show_str = f'第{str_t.strip()}张照片你还没有确认截图，或点击跳过检查按钮，按照现有区域截图，确保调整好位置正面在前反面在后，并且调整好方向。'
                self.show_info.set_show_text(show_str)
                self.show_info.show()
            self.scroll_area.confirem_button.setEnabled(True)
        except:
            self.scroll_area.confirem_button.setEnabled(True)

    def reshape_image(self, image, points):
        width = (calculate_distance(points[0], points[1]) + calculate_distance(points[2], points[3])) / 2
        height= (calculate_distance(points[2], points[1]) + calculate_distance(points[0], points[3])) / 2
        if width > height:
            id_shape = (max(self.id_shape), min(self.id_shape))
        else:
            id_shape = (min(self.id_shape), max(self.id_shape))
        # 定义目标四个点的位置
        dst_points = np.array([[0, 0], [id_shape[0], 0], [id_shape[0], id_shape[1]], [0, id_shape[1]]], dtype=np.float32)
        # 转换四个点的数据类型为 float32
        points = np.float32(points)
        # 计算透视变换矩阵
        matrix = cv2.getPerspectiveTransform(points, dst_points)
        # 进行透视变换，使用更高级的插值方法
        warped_image = cv2.warpPerspective(image, matrix, (id_shape[0], id_shape[1]), flags=cv2.INTER_CUBIC)
        return warped_image

    def skip_check(self):
        if self.this_index != None:
            this_index_catch = self.this_index
            compare = list(range(len(self.scroll_area.labels)))
            for i in compare:
                if i not in self.viewed:
                    self.this_index = i
                    if this_index_catch == i:
                        if len(self.scroll_area.labels[i].points) == 0:
                            self.comfire_this(False)
                        else:
                            self.comfire_this()
                    else:
                        self.comfire_this(False)
            self.this_index = this_index_catch
            self.scroll_area.scroll_to_label(self.this_index)

    def rotate(self, mode):
        if self.this_index != None:
            img_before = self.scroll_area.labels[self.this_index].img
            self.scroll_area.labels[self.this_index].img = pic_rotate_angle(img_before, mode)
            height, width, _ = img_before.shape
            center_point = [int(width / 2), int(height / 2)]
            center_new = [int(height / 2), int(width / 2)]
            center_shift = [new - old for new, old in zip(center_new, center_point)]
            point_before = self.scroll_area.labels[self.this_index].points
            new_point = []
            if len(point_before) != 0:
                #在第四象限，从原点最近的点起，顺时针排序
                for point in point_before:
                    rotated = point_rotate_90(point, center_point, not mode)
                    shifted = [new + old for new, old in zip(rotated, center_shift)]
                    new_point.append(shifted)
                if mode == 0:
                    new_point = [new_point[-1]] + new_point[:-1]
                else:
                    new_point = new_point[1:] + [new_point[0]]
            else:
                img_cache = self.scroll_area.labels[self.this_index].img_cache
                height_cache, width_cache, _ = img_cache.shape
                center_point_cache = [int(width_cache / 2), int(height_cache / 2)]
                center_new_cache = [int(height_cache / 2), int(width_cache / 2)]
                center_shift_new = [new - old for new, old in zip(center_new_cache, center_point_cache)]
                point_cache = self.scroll_area.labels[self.this_index].points_cache
                self.scroll_area.labels[self.this_index].img_cache = pic_rotate_angle(img_cache, mode)
                for point in point_cache:
                    rotated = point_rotate_90(point, center_point_cache, not mode)
                    shifted = [new + old for new, old in zip(rotated, center_shift_new)]
                    new_point.append(shifted)
                if mode == 0:
                    new_point = [new_point[-1]] + new_point[:-1]
                else:
                    new_point = new_point[1:] + [new_point[0]]
                self.scroll_area.labels[self.this_index].points_cache = np.array(new_point)
                new_point = []
            self.scroll_area.labels[self.this_index].points = np.array(new_point)
            shou_flag = not self.scroll_area.labels[self.this_index].moved_flag and not self.scroll_area.labels[self.this_index].max_flag
            self.display_large_image(self.this_index, shou_flag, True, True)
            shift = self.zheng_fan_shift * (self.this_index in self.viewed)
            fixed_width = self.fixed_width - shift
            pixmap = cv_to_qpixmap(self.scroll_area.labels[self.this_index].img)
            scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
            scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
            self.scroll_area.labels[self.this_index].setFixedSize(fixed_width + shift, scaled_height)  # 设置每张图片的固定宽度

    def read_cut_info(self, obj:ClickableLabel):
        index = obj.index
        photo_path = obj.photo_path
        points = obj.points
        points_cache = obj.points_cache
        scale = obj.scale
        scale_cache = obj.scale_cache
        img = obj.img
        img_cache = obj.img_cache
        moved_flag = obj.moved_flag
        max_flag = obj.max_flag
        outside_color = obj.outside_color
        return index, photo_path, points, points_cache, scale, scale_cache, img, img_cache, moved_flag, max_flag, outside_color

    def write_cut_info(self, obj:ClickableLabel, index, photo_path, points, points_cache, scale, scale_cache, img, img_cache, moved_flag, max_flag, outside_color):
        obj.index = index
        obj.photo_path = photo_path
        obj.points = points
        obj.points_cache = points_cache
        obj.scale = scale
        obj.scale_cache = scale_cache
        obj.img = img
        obj.img_cache = img_cache
        obj.moved_flag = moved_flag
        obj.max_flag = max_flag
        obj.outside_color = outside_color
        return obj

    def change_position(self, mode):
        if self.this_index != None:
            if mode == 0:
                shift = -1
            else:
                shift = 1
            if (self.this_index != 0 and mode == 0) or (self.this_index != len(self.scroll_area.labels) - 1 and mode == 1):
                #信息互换
                _, photo_path, points, points_cache, scale, scale_cache, img, img_cache, moved_flag, max_flag, outside_color = self.read_cut_info(self.scroll_area.labels[self.this_index])
                _, photo_path1, points1, points_cache1, scale1, scale_cache1, img1, img_cache1, moved_flag1, max_flag1, outside_color1 = self.read_cut_info(self.scroll_area.labels[self.this_index + shift])
                self.scroll_area.labels[self.this_index] = self.write_cut_info(self.scroll_area.labels[self.this_index], self.this_index, photo_path1, points1, points_cache1, scale1, scale_cache1, img1, img_cache1, moved_flag1, max_flag1, outside_color1)
                self.scroll_area.labels[self.this_index + shift] = self.write_cut_info(self.scroll_area.labels[self.this_index + shift], self.this_index + shift, photo_path, points, points_cache, scale, scale_cache, img, img_cache, moved_flag, max_flag, outside_color)
                shift_t = self.zheng_fan_shift * (self.this_index in self.viewed)
                fixed_width = self.fixed_width - shift_t
                pixmap = cv_to_qpixmap(self.scroll_area.labels[self.this_index + shift].img)
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index + shift].setPixmap(scaled_pixmap)
                self.scroll_area.labels[self.this_index + shift].setFixedSize(fixed_width + shift_t, scaled_height)  # 设置每张图片的固定宽度

                shift_t = self.zheng_fan_shift * ((self.this_index + shift) in self.viewed)
                fixed_width = self.fixed_width - shift_t
                pixmap = cv_to_qpixmap(self.scroll_area.labels[self.this_index].img)
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
                self.scroll_area.labels[self.this_index].setFixedSize(fixed_width + shift_t, scaled_height)  # 设置每张图片的固定宽度
                if self.this_index in self.viewed and self.this_index + shift not in self.viewed:
                    self.viewed.append(self.this_index + shift)
                    self.viewed.remove(self.this_index)
                elif self.this_index not in self.viewed and self.this_index + shift in self.viewed:
                    self.viewed.remove(self.this_index + shift)
                    self.viewed.append(self.this_index)
                self.this_index += shift
                self.scroll_area.scroll_to_label(self.this_index)

    def comfire_this(self, change_pic_flag = True):
        if self.this_index != None:
            next_flag = True
            if len(self.scroll_area.labels[self.this_index].points) != 0:
                next_flag = False
                if self.this_index not in self.viewed:
                    self.viewed.append(self.this_index)
                points = self.scroll_area.labels[self.this_index].points
                self.scroll_area.labels[self.this_index].points_cache = points
                self.scroll_area.labels[self.this_index].points = np.array([])
                self.large_image_label.selected_point = None
                self.large_image_label.selected_middle_point = None
                cv_img = self.scroll_area.labels[self.this_index].img
                self.scroll_area.labels[self.this_index].img_cache = cv_img
                cv_img = self.reshape_image(cv_img, points)
                mask = get_mask(self.angle_rate, cv_img.shape)
                cv_img = add_mask(cv_img, mask, self.scroll_area.labels[self.this_index].outside_color)
                self.scroll_area.labels[self.this_index].img = cv_img
                scale = self.scroll_area.labels[self.this_index].scale
                self.scroll_area.labels[self.this_index].scale_cache = scale
                self.scroll_area.labels[self.this_index].scale = 1

                #显示小图
                shift = self.zheng_fan_shift * (self.this_index in self.viewed)
                fixed_width = self.fixed_width - shift
                pixmap = cv_to_qpixmap(self.scroll_area.labels[self.this_index].img)
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
                self.scroll_area.labels[self.this_index].setFixedSize(fixed_width + shift, scaled_height)  # 设置每张图片的固定宽度

            if change_pic_flag:
                if self.this_index != len(self.scroll_area.labels) - 1 and next_flag:
                    shou_flag = not self.scroll_area.labels[self.this_index + 1].moved_flag and not self.scroll_area.labels[self.this_index + 1].max_flag
                    self.display_large_image(self.this_index + 1, shou_flag)
                else:
                    #显示大图
                    pixmap = cv_to_qpixmap(self.scroll_area.labels[self.this_index].img)
                    size = pixmap.size()
                    width = size.width()
                    height = size.height()
                    self.large_image_label.change_size((height, width))  # 设置大图显示区域大小
                    self.large_image_label.clear_content()
                    self.large_image_label.set_points(np.array([]))
                    self.large_image_label.selected_point = None
                    self.large_image_label.selected_middle_point = None
                    self.large_image_label.set_pic(pixmap.scaled(width, height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio))
                    large_image_shape_round_gap = self.large_image_label.show_pic_shape.round_gap
                    self.setFixedSize(self.scroll_area_width + width + large_image_shape_round_gap * 2 + self.width_gap, height + large_image_shape_round_gap * 2 + self.height_gap)
                    self.scroll_area.confire_this_button.setText('下一张')
                    self.scroll_area.scroll_to_label(self.this_index)
             
    def previous(self):
        if self.this_index != None:
            if self.this_index in self.viewed:
                self.viewed.remove(self.this_index)
            if len(self.scroll_area.labels[self.this_index].points) == 0:
                points = self.scroll_area.labels[self.this_index].points = self.scroll_area.labels[self.this_index].points_cache
                self.scroll_area.labels[self.this_index].points_cache = np.array([])
                img = self.scroll_area.labels[self.this_index].img = self.scroll_area.labels[self.this_index].img_cache
                self.scroll_area.labels[self.this_index].img_cache = []
                scale = self.scroll_area.labels[self.this_index].scale = self.scroll_area.labels[self.this_index].scale_cache
                self.scroll_area.labels[self.this_index].scale_cache = 1

                #显示小图
                shift = self.zheng_fan_shift * (self.this_index in self.viewed)
                fixed_width = self.fixed_width - shift
                pixmap = cv_to_qpixmap(img)
                scaled_height = int(pixmap.height() * fixed_width / pixmap.width())  # 使用 int() 确保高度是整数
                scaled_pixmap = pixmap.scaled(fixed_width, scaled_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.scroll_area.labels[self.this_index].setPixmap(scaled_pixmap)
                self.scroll_area.labels[self.this_index].setFixedSize(fixed_width + shift, scaled_height)  # 设置每张图片的固定宽度

                #显示大图
                pixmap = cv_to_qpixmap(img)
                size = pixmap.size()
                width = size.width()
                height = size.height()
                width = int(width * scale)
                height = int(height * scale)
                self.large_image_label.change_size((height, width))  # 设置大图显示区域大小
                self.large_image_label.clear_content()
                shou_flag = not self.scroll_area.labels[self.this_index].moved_flag and not self.scroll_area.labels[self.this_index].max_flag
                self.large_image_label.set_points(self.merge_scaled_dot(points, scale), shou_flag)
                self.large_image_label.set_pic(pixmap.scaled(width, height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio))
                large_image_shape_round_gap = self.large_image_label.show_pic_shape.round_gap
                self.setFixedSize(self.scroll_area_width + width + large_image_shape_round_gap * 2 + self.width_gap, height + large_image_shape_round_gap * 2 + self.height_gap)
                self.scroll_area.confire_this_button.setText('确认截图')
                self.scroll_area.scroll_to_label(self.this_index)

    def change_outside_color(self):
        if self.this_index != None:
            value = self.scroll_area.slider.value()
            value = calc_no_line_number(0, 50, 255, 3, value)
            color_change = (value, value, value)
            self.scroll_area.labels[self.this_index].outside_color = color_change
            if self.this_index in self.viewed:
                points = self.scroll_area.labels[self.this_index].points_cache
                self.scroll_area.labels[self.this_index].points = points
                cv_img = self.scroll_area.labels[self.this_index].img_cache
                self.scroll_area.labels[self.this_index].img = cv_img
                self.comfire_this()

    def init_event(self):
        self.scroll_area.skip_button.clicked.connect(self.skip_check)
        self.scroll_area.lift_rotate_button.clicked.connect(lambda: self.rotate(1))
        self.scroll_area.right_rotate_button.clicked.connect(lambda: self.rotate(0))
        self.scroll_area.up_button.clicked.connect(lambda: self.change_position(0))
        self.scroll_area.down_button.clicked.connect(lambda: self.change_position(1))
        self.scroll_area.confire_this_button.clicked.connect(lambda: self.comfire_this(True))
        self.scroll_area.previous_button.clicked.connect(self.previous)
        self.scroll_area.confirem_button.clicked.connect(self.confirm_selection)
        self.scroll_area.slider.sliderReleased.connect(self.change_outside_color)
