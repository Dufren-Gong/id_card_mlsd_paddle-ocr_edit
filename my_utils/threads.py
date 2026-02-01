from PyQt6 import QtCore
from my_utils.utils import download_zip, unzip_file
from my_utils.pdf_to_pic import convert_pdf_to_images
from my_utils.ocr_by_paddleocr import pic_to_str
from my_utils.mlsd_scan import square_four_lines, get_square_dots
import numpy as np
import os, shutil

class PDFToPicSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()

class Pdf_to_Pic_Thread(QtCore.QRunnable):  # 继承QThread
    def __init__(self, folder_path, save_path, pic_formate): # 从前端界面中传递参数到这个任务后台
        super().__init__()
        self.folder_path = folder_path
        self.pic_formate = pic_formate
        self.save_path = save_path
        self.signals = PDFToPicSignals()

    def run(self):  # 重写run  比较耗时的后台任务可以在这里运行
        convert_pdf_to_images(self.folder_path, self.save_path, self.pic_formate)
        self.signals.finished.emit()  # 任务完成后，发送信号

class OcrSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object, object, object)

class Get_Ocr(QtCore.QRunnable):
    def __init__(self, cv_img, ocr_model, path, pass_flag=False, scale=0.8, pic_shape = (856, 540), times = 1, pic_type='origin', info_checks = dict(), one_line_scale = 30, check_back=False): # 从前端界面中传递参数到这个任务后台
        super().__init__()
        self.cv_img = cv_img
        self.ocr_model = ocr_model
        self.path = path
        self.pass_flag = pass_flag
        self.scale = scale
        self.pic_shape = pic_shape
        self.pic_type = pic_type
        self.times = times
        self.info_checks = info_checks
        self.one_line_scale = one_line_scale
        self.check_back = check_back
        self.signals = OcrSignals()

    def run(self):  # 重写run  比较耗时的后台任务可以在这里运行
        catch, pic_info_dict = pic_to_str(self.cv_img, self.ocr_model, self.pass_flag, scale=self.scale, shape=self.pic_shape, times = self.times, pic_type = self.pic_type, info_checks = self.info_checks, one_line_scale = self.one_line_scale, check_back = self.check_back)
        self.signals.finished.emit(catch, pic_info_dict, self.path)  # 任务完成后，发送信号

class LDSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object, object, object, object, object)

class Get_line_detect(QtCore.QRunnable):
    def __init__(self, cv_pairs, pair_paths, scales, line_detect_model, model_large, params, max_t_arr, model_type, pic_shape, tiny_first_flag): # 从前端界面中传递参数到这个任务后台
        super().__init__()
        self.cv_pairs = cv_pairs
        self.pair_paths = pair_paths
        self.scales = scales
        self.line_detect_model = line_detect_model
        self.model_large = model_large
        self.params = params
        self.max_t_arr = max_t_arr
        self.model_type = model_type
        self.pic_shape = pic_shape
        self.tiny_first_flag = tiny_first_flag
        self.signals = LDSignals()

    def in_pic(self, pic_shape, points):
        final_point = []
        final_point.append([max(points[0][0], 0), max(points[0][1], 0)])
        final_point.append([min(points[1][0], pic_shape[1]), max(points[1][1], 0)])
        final_point.append([min(points[2][0], pic_shape[1]), min(points[2][1], pic_shape[0])])
        final_point.append([max(points[3][0], 0), min(points[3][1], pic_shape[0])])
        return np.array(final_point)

    def run(self):  # 重写run  比较耗时的后台任务可以在这里运行
        points = []
        max_flags = []
        for index, people in enumerate(self.cv_pairs):
            pic_path_this = self.pair_paths[index]
            if os.path.basename(pic_path_this).startswith('split_c_'):
                self.params['pic_remode'] = 1
            h, w, _ = people.shape
            if self.model_type == 'tiny':
                squares, array_score = get_square_dots(people, self.line_detect_model, max_t=self.max_t_arr[0], params=self.params)
                squares_lines, max_flag = square_four_lines(squares, array_score, (h, w), 0.1, self.pic_shape)
            elif self.model_type == 'large':
                squares, array_score = get_square_dots(people, self.model_large, max_t=self.max_t_arr[1], params=self.params)
                squares_lines, max_flag = square_four_lines(squares, array_score, (h, w), 0.1, self.pic_shape)
            elif self.model_type == 'all':
                if self.tiny_first_flag:
                    squares, array_score = get_square_dots(people, self.line_detect_model, max_t=self.max_t_arr[0], params=self.params)
                else:
                    squares, array_score = get_square_dots(people, self.model_large, max_t=self.max_t_arr[1], params=self.params)
                squares_lines, max_flag = square_four_lines(squares, array_score, (h, w), 0.1, self.pic_shape)
                if max_flag:
                    if self.tiny_first_flag:
                        squares, array_score = get_square_dots(people, self.model_large, max_t=self.max_t_arr[1], params=self.params)
                    else:
                        squares, array_score = get_square_dots(people, self.line_detect_model, max_t=self.max_t_arr[0], params=self.params)
                    squares_lines, max_flag = square_four_lines(squares, array_score, (h, w), 0.1, self.pic_shape)
            #重置mode
            self.params['pic_remode'] = 0
            squares_lines = sorted(squares_lines, key=lambda x:x[4], reverse=False)
            first_step = [i[:4] for i in squares_lines]
            second_step = [[j[0][0], j[0][1], j[2][0], j[2][1]] for j in first_step]
            final_point = self.in_pic((h, w), second_step[-1])
            points.append(final_point)
            max_flags.append(max_flag)
        self.signals.finished.emit(self.cv_pairs, self.pair_paths, points, max_flags, self.scales)  # 任务完成后，发送信号

class Download_Sourcecode(QtCore.QThread):
    resSignal = QtCore.pyqtSignal(object, object, object, object, object)  # 注册一个信号
    def __init__(self, global_config, name, zip_file_path, result_name, root_floader, new_version, just_download=False): # 从前端界面中传递参数到这个任务后台
        super().__init__()
        self.global_config = global_config
        self.name = name
        self.zip_file_path = zip_file_path
        self.result_name = result_name
        self.root_floader = root_floader
        self.new_version = new_version
        self.just_download = just_download

    def run(self):  # 重写run  比较耗时的后台任务可以在这里运行
        _ = download_zip(self.global_config, self.result_name)
        if not self.just_download:
            unzip_file(self.zip_file_path, '.')
            self.resSignal.emit(self.name, self.zip_file_path, self.result_name, self.root_floader, self.new_version)
        else:
            self.resSignal.emit(1, 1, 1, 1, 1)

class Download_Copy_Large(QtCore.QThread):
    resSignal = QtCore.pyqtSignal(object)  # 注册一个信号
    def __init__(self, source, target, name): # 从前端界面中传递参数到这个任务后台
        super().__init__()
        self.source = source
        self.target = target
        self.name = name

    def run(self):  # 重写run  比较耗时的后台任务可以在这里运行
        shutil.copytree(self.source, self.target)
        self.resSignal.emit(self.name)