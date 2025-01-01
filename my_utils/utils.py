from datetime import datetime, timedelta
import os, math, json, sys, base64
import shutil, requests
# import PIL
# import PIL.Image
# import PIL.ImageEnhance
from PyQt6.QtGui import QImage, QPixmap
from natsort import natsorted
import platform
import cv2, copy
import numpy as np
from pathlib import Path
from ruamel.yaml import YAML
from send2trash import send2trash

def rgb_to_gray_with_three_channels(image):
    # 将 RGB 图像转换为灰度图像 (单通道)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 将单通道灰度图像复制为 3 个通道
    gray_3_channels = cv2.merge([gray, gray, gray])
    return gray_3_channels

def get_config(config_path = './模版/配置和记录/conf.yaml'):
    # 初始化 YAML 处理器
    yaml = YAML()
    yaml.preserve_quotes = True  # 保留引号（如果 YAML 中有引号）
    with open(config_path, 'r', encoding='utf-8') as file:
        global_config = yaml.load(file)
    return global_config

#用下面这两个函数可以使用cv读取含有中文路径的文件
def cv_imread(file_path):
    # Read image as a byte array with np.fromfile
    image_array = np.fromfile(file_path, dtype=np.uint8)
    # Decode image using cv2.imdecode
    cv_img = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
    return cv_img

def find_in_catch_pic(name):
    floader = './模版/缓存照片'
    #从最新的开始索引
    catch_pic_paths = natsorted(os.listdir(floader), reverse=True)
    if '.DS_Store' in catch_pic_paths:
        catch_pic_paths.remove('.DS_Store')
    for i in catch_pic_paths:
        search = os.path.join(floader, i)
        cache_path = os.path.join(search, name)
        if os.path.exists(cache_path + '.info') and os.path.exists(cache_path + '.png') and os.path.exists(cache_path + '反.png'):
            return cache_path
    return ''

def delete_specific_files_and_folders(target_dir, del_dirname = None, del_filename = None):#, global_config = None):
    if del_dirname != None and del_filename != None:
        for root, dirs, files in os.walk(target_dir, topdown=False):
            # 删除 __pycache__ 文件夹
            if del_dirname != None:
                for dir_name in dirs:
                    if dir_name == del_dirname:
                        dir_path = os.path.join(root, dir_name)
                        shutil.rmtree(dir_path)  # 删除整个文件夹

            if del_filename != None:
                # 删除 .DS_Store 文件
                for file_name in files:
                    if file_name == del_filename:
                        file_path = os.path.join(root, file_name)
                        os.remove(file_path)  # 删除文件
    #将该文件夹隐藏
    path = './_internal'
    if os.path.exists(path):
        os.system(f'attrib +h "{path}"')
    # if global_config != None:
    #     path = './_internal'
    #     if global_config['del_packges_config']['del_flag'] and os.path.exists(path):
    #         packges = global_config['del_packges_config']['del_packges']
    #         if len(packges) != 0:
    #             for packge in packges:
    #                 path_t = os.path.join(path, packge)
    #                 if os.path.exists(path_t):
    #                     shutil.rmtree(path_t)

def get_internal_path(path:str):
    # 获取程序的资源文件路径
    if getattr(sys, 'frozen', False):  # 检查是否在打包后的模式下
        # 如果是打包后的程序，资源文件解压到 sys._MEIPASS 临时目录
        path_split = path.lstrip('./').rstrip('/')
        return os.path.join(sys._MEIPASS, path_split)
    else:
        return path

def check_catch_pic(catch_days):
    check_path = './模版/缓存照片'
    if catch_days != 0:
        day_pics = os.listdir(check_path)
        if '.DS_Store' in day_pics:
            day_pics.remove('.DS_Store')
        catch_days_floader = get_past_dates(catch_days)
        del_days = [i for i in day_pics if i not in catch_days_floader]
        if len(del_days) != 0:
            for i in del_days:
                send2trash(os.path.join(check_path, i))
        today_floader = os.path.join(check_path, catch_days_floader[0])
    else:
        catch_days_floader = get_past_dates(1)
        today_floader = os.path.join(check_path, catch_days_floader[0])
    os.makedirs(today_floader, exist_ok=True)
    return today_floader

def change_three_channel(cv_img):
    if cv_img is not None:
        if len(cv_img.shape) == 3:
            if cv_img.shape[2] == 4:  # 如果是 RGBA
                cv_temp = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2BGR)
                return cv_temp
            elif cv_img.shape[2] == 1:  # 如果是单通道灰度图
                cv_temp = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2BGR)
                return cv_temp
            else:
                return cv_img
        elif len(cv_img.shape) == 2:
            cv_temp = np.stack([cv_img] * 3, axis=-1)  # 在最后一维重复 3 次形成 RGB 格式
            return cv_temp
    return cv_img

def cv_imwrite(image, file_type, save_path):
    cv2.imencode(ext=file_type, img=image)[1].tofile(save_path)

def get_data_str():
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d-%H-%M-%S")
    return formatted_now

def get_past_dates(n):
    today = datetime.today()  # 获取今天的日期
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, n+0)]
    return dates

def open_floader(path):
    path = Path(path)
    current_os = platform.system()
    if current_os == "Windows":
        os.startfile(path)  # Windows特定的方法
    elif current_os == "Darwin":  # macOS
        os.system(f"open {os.path.abspath(path)}")
    elif current_os == "Linux":
        os.system(f"xdg-open {os.path.abspath(path)}")

def unzip_file(zip_path, extract_path):
    shutil.unpack_archive(zip_path, extract_path)

def get_all_pic_path(floader_path):
    file_paths = []
    # 遍历文件夹及子文件夹
    for root, _, files in os.walk(floader_path):
        for file in files:
            # 获取完整的文件路径
            if file != '.DS_Store':
                file_paths.append(os.path.join(root, file))
    return natsorted(file_paths)

def get_pic_info(info_file_path: str, pic_path):
    with open(info_file_path, 'r', encoding='utf-8') as reader:
        lines = reader.readlines()
    reader.close()
    info = []
    for line in lines:
        line = json.loads(line.strip())
        if line['path'] == pic_path:
            info = line['info']
            break
    return info

def add_mask(image, mask):
    assert image.shape == mask.shape

    # 将mask之内的区域设置为白色
    white_background = np.full_like(image, 255, dtype=np.uint8)
    white_area = ~cv2.bitwise_and(white_background, mask)

    # 将原图与反转后的掩码相结合，保持mask之外的原始内容
    original_area = cv2.bitwise_and(image, mask)

    # 合成最终图像
    rounded_image = cv2.add(white_area, original_area)
    return rounded_image

def get_mask(corner_radius, mask_shape):
    # 创建一个带有圆角的黑色掩码
    mask_shape = (mask_shape[1], mask_shape[0], mask_shape[2])
    mask = np.zeros(mask_shape, dtype=np.uint8)
    rows, cols, _ = mask_shape
    # 绘制矩形区域
    mask = cv2.rectangle(mask, (corner_radius, corner_radius), (cols-corner_radius, rows-corner_radius), (255, 255, 255), thickness=-1)
    mask = cv2.rectangle(mask, (corner_radius, 0), (cols-corner_radius, corner_radius), (255, 255, 255), thickness=-1)
    mask = cv2.rectangle(mask, (corner_radius, rows-corner_radius), (cols-corner_radius, rows), (255, 255, 255), thickness=-1)
    mask = cv2.rectangle(mask, (0, corner_radius), (corner_radius, rows-corner_radius), (255, 255, 255), thickness=-1)
    mask = cv2.rectangle(mask, (cols-corner_radius, corner_radius), (cols, rows-corner_radius), (255, 255, 255), thickness=-1)
    # 圆角处理
    mask = cv2.circle(mask, (corner_radius, corner_radius), corner_radius, (255, 255, 255), thickness=-1)
    mask = cv2.circle(mask, (cols-corner_radius, corner_radius), corner_radius, (255, 255, 255), thickness=-1)
    mask = cv2.circle(mask, (corner_radius, rows-corner_radius), corner_radius, (255, 255, 255), thickness=-1)
    mask = cv2.circle(mask, (cols-corner_radius, rows-corner_radius), corner_radius, (255, 255, 255), thickness=-1)
    mask = cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE)
    return mask

def cv_to_qimage(cv_img):
    try:
        height, width, _ = cv_img.shape
    except:
        height, width = cv_img.shape
    bytes_per_line = 3 * width
    # 将 BGR 转换为 RGB（Qt 使用 RGB，OpenCV 使用 BGR）
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    qimage = QImage(cv_img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    return qimage

def cv_to_qpixmap(cv_img):
    qimage = cv_to_qimage(cv_img)
    qpixmap = QPixmap.fromImage(qimage)
    return qpixmap

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def point_rotate_90(point1, point_center, mode):
    """
    计算点 B(x2, y2) 围绕点 A(x1, y1) 旋转 90 度后的坐标。

    :param x1: A 点的 x 坐标
    :param y1: A 点的 y 坐标
    :param x2: B 点的 x 坐标
    :param y2: B 点的 y 坐标
    :param mode: 旋转模式，0 表示顺时针旋转，1 表示逆时针旋转
    :return: 旋转后的点 B 的新坐标 (x2', y2')
    """
    # 平移坐标系
    x1, y1 = point_center[0], point_center[1]
    x2, y2 = point1[0], point1[1]
    x_prime = x2 - x1
    y_prime = y2 - y1

    if mode == 0:
        # 顺时针旋转 90 度
        x_double_prime = y_prime
        y_double_prime = -x_prime
    elif mode == 1:
        # 逆时针旋转 90 度
        x_double_prime = -y_prime
        y_double_prime = x_prime

    # 还原坐标系
    x2_new = x_double_prime + x1
    y2_new = y_double_prime + y1

    return [x2_new, y2_new]

def pic_rotate_angle(image, mode):
    if mode:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image

def add_edge(image_or, mask_angle, edge_ipx, edge_color, add_towards):
    image = copy.deepcopy(image_or)
    shift = 1
    height, width, _ = image.shape
    if 2 in add_towards:
        draw_fan(image, (width - mask_angle, mask_angle), mask_angle-edge_ipx, mask_angle, 270, 360, edge_color, thickness=1)
    if 4 in add_towards:
        draw_fan(image, (width - mask_angle, height - mask_angle), mask_angle-edge_ipx, mask_angle, 0, 90, edge_color, thickness=1)
    if 6 in add_towards:
        draw_fan(image, (mask_angle, height - mask_angle), mask_angle-edge_ipx, mask_angle, 90, 180, edge_color, thickness=1)
    if 8 in add_towards:
        draw_fan(image, (mask_angle, mask_angle), mask_angle-edge_ipx, mask_angle, 180, 270, edge_color, thickness=1)
    if edge_ipx != 1:
        if 1 in add_towards:
            cv2.rectangle(image, (mask_angle, 0), (width - mask_angle , edge_ipx), edge_color, thickness=-1)
        if 3 in add_towards:
            cv2.rectangle(image, (width - edge_ipx - shift, mask_angle), (width - shift, height - mask_angle), edge_color, thickness=-1)
        if 5 in add_towards:
            cv2.rectangle(image, (mask_angle, height - edge_ipx - shift), (width - mask_angle, height - shift), edge_color, thickness=-1)
        if 7 in add_towards:
            cv2.rectangle(image, (0, mask_angle), (edge_ipx, height - mask_angle), edge_color, thickness=-1)
    else:
        if 1 in add_towards:
            cv2.line(image, (mask_angle , 0), (width - mask_angle , 0), edge_color, 1)
        if 3 in add_towards:
            cv2.line(image, (width - shift, mask_angle), (width - shift, height - mask_angle), edge_color, 1)
        if 5 in add_towards:
            cv2.line(image, (mask_angle, height - shift), (width - mask_angle, height - shift), edge_color, 1)
        if 7 in add_towards:
            cv2.line(image, (0, mask_angle), (0, height - mask_angle), edge_color, 1)
    return image

def draw_fan(image, center, inner_radius, outer_radius, start_angle, end_angle, color, thickness=1):
    """
    在图像上绘制一个扇形区域。

    参数:
    - image: 输入图像
    - center: 圆心坐标 (x, y)
    - inner_radius: 内半径
    - outer_radius: 外半径
    - start_angle: 起始角度（度数）
    - end_angle: 结束角度（度数）
    - color: 扇形的颜色
    - thickness: 扇形的厚度 (-1 为填充)
    """
    # 定义角度范围
    if inner_radius < 0:
        inner_radius = 0
    angles = np.linspace(start_angle, end_angle, num=100)
    # 计算内半径上的点
    inner_points = [(int(center[0] + inner_radius * np.cos(np.deg2rad(angle))),
                     int(center[1] + inner_radius * np.sin(np.deg2rad(angle))))
                    for angle in angles]
    # 计算外半径上的点
    outer_points = [(int(center[0] + outer_radius * np.cos(np.deg2rad(angle))),
                     int(center[1] + outer_radius * np.sin(np.deg2rad(angle))))
                    for angle in angles]
    # 合并外半径和内半径上的点
    points = np.array(outer_points + inner_points[::-1], dtype=np.int32)
    # 使用 fillPoly 绘制扇形区域
    cv2.fillPoly(image, [points], color)
    return image

# def calculate_brightness(image):
#     """
#     计算图片的平均亮度
#     """
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#     brightness = hsv[:, :, 2].mean()  # V 通道的均值
#     return brightness

# def adjust_brightness(image, target_brightness):
#     """
#     调整图片的亮度，使其接近目标亮度
#     """
#     current_brightness = calculate_brightness(image)
#     brightness_ratio = target_brightness / current_brightness
#     # 调整 V 通道
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#     hsv = hsv.astype(np.float32)
#     hsv[:, :, 2] = np.clip(hsv[:, :, 2] * brightness_ratio, 0, 255)
#     hsv = hsv.astype(np.uint8)
#     adjusted_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
#     return adjusted_image

def download_zip(global_config, name, files = []):
    owner = global_config['owner']
    repo = global_config['repo']
    access_token = global_config['access_token']
    ref = global_config['ref']
    if files == []:
        tip = 'zipball'
    zip_url = f'https://gitee.com/api/v5/repos/{owner}/{repo}/{tip}?access_token={access_token}&ref={ref}'
    try:
        response = requests.get(zip_url, stream=True)
        if response.status_code == 200:
            with open(f"./{name}.zip", "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return True
        else:
            return f"下载失败，状态码：{response.status_code}\n详情：{response.text}"
    except Exception as e:
        return f"下载过程中出错：{e}"
    
def download_single_file(global_config, path_in_cloud, to_path):
    owner = global_config['owner']
    repo = global_config['repo']
    access_token = global_config['access_token']
    ref = global_config['ref']

    # 构建 API URL
    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{path_in_cloud}?access_token={access_token}&ref={ref}"

    # 请求文件内容
    response = requests.get(url)

    if response.status_code == 200:
        file_info = response.json()
        file_content = base64.b64decode(file_info['content'])  # 文件内容是 Base64 编码的
        # 保存到本地
        print("当前工作目录：", os.getcwd())
        with open(to_path, "wb") as file:
            file.write(file_content)
        return True
    else:
        print(f"文件下载失败，状态码：{response.status_code}, 错误信息：{response.text}")