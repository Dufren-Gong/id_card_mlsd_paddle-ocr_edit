import sys, gc, os, cv2
import math
import onnxruntime as ort
import numpy as np
from my_utils.utils import change_three_channel, get_internal_path
from my_utils.mlsd_utils import pred_squares, distance
from PIL.ImageEnhance import Contrast as PILImageEnhanceContrast
from PIL.Image import fromarray as PILImagefromarray

def release_model(model, model_large):
    # 删除模型
    try:
        del model
    except:
        pass
    try:
        del model_large
    except:
        pass

    gc.collect()

def get_model(global_config):
    pwd = os.getcwd()
    os.chdir('..')
    # 使用 'cuda:1' 表示使用第二块 GPU（因为索引从 0 开始）
    device = global_config['mlsd_conf']['device']
    if device != 'cpu':
        providers = ['CUDAExecutionProvider']  # GPU执行提供者
    else:
        providers = ['CPUExecutionProvider']  # CPU执行提供者
    model_type = global_config['mlsd_conf']['model_type']
    if model_type == 'tiny' or model_type == 'all':
        tiny_model_path = get_internal_path(global_config['mlsd_conf']['tiny_model_path'])
        try:
            tiny_model = ort.InferenceSession(tiny_model_path, providers=providers)
        except:
            tiny_model = ort.InferenceSession(tiny_model_path, providers=['CPUExecutionProvider'])
        if model_type == 'tiny':
            large_model = None
    if model_type == 'large' or model_type == 'all':
        large_model_path = get_internal_path(global_config['mlsd_conf']['large_model_path'])
        try:
            large_model = ort.InferenceSession(large_model_path, providers=providers)
        except:
            large_model = ort.InferenceSession(large_model_path, providers=['CPUExecutionProvider'])
        if model_type == 'large':
            tiny_model = None
    os.chdir(pwd)
    return tiny_model, large_model

# def closest_power_of_two(n):
#     i = 1
#     while(i * 2 <= n):
#         i *= 2
#     return i

def closest_shape(n):
    n = int(n / 32)
    power = 32 * n
    return power

# def get_square_dots(src, model, max_t=1024,
#                         params={'score': 0.1,
#                          'outside_ratio': 0.28,
#                          'inside_ratio': 0.45,
#                          'w_overlap': 1.0,
#                          'w_degree': 1.95,
#                          'w_length': 0.0,
#                          'w_area': 1.86,
#                          'w_center': 0.14}):
#     src_temp = change_three_channel(src)
#     _, squares, array_score, _ = pred_squares(src_temp, model, params=params)
#     return squares, array_score

def get_square_dots(src, model, max_t=1024,
                        params={'score': 0.1,
                         'outside_ratio': 0.28,
                         'inside_ratio': 0.45,
                         'w_overlap': 1.0,
                         'w_degree': 1.95,
                         'w_length': 0.0,
                         'w_area': 1.86,
                         'w_center': 0.14,
                         'top_n': 50,
                         'pic_remode': 0,
                         'duibidu_shift': 1.0}):
    max_t = min(max_t, 1024)
    src_temp = change_three_channel(src)
    #增强对比度
    pic_remode = params['pic_remode']
    if pic_remode == 1:
        duibidu_shift = params['duibidu_shift']
        if duibidu_shift != 1.0:
            src_temp = PILImagefromarray(cv2.cvtColor(src_temp, cv2.COLOR_BGR2RGB))
            enhancer = PILImageEnhanceContrast(src_temp)
            src_temp = enhancer.enhance(duibidu_shift)
            src_temp = cv2.cvtColor(np.array(src_temp), cv2.COLOR_RGB2BGR)
    height, width, _ = src.shape
    min_length = min(height, width)
    min_pow = closest_shape(min_length)
    min_pow = min(min_pow, max_t)
    min_pow = max(min_pow, 512)
    try:
        _, squares, array_score, _ = pred_squares(src_temp, model, input_shape=[min_pow] * 2, params=params)
        if len(squares) == 0:
            if min_pow > 768:
                try:
                    _, squares, array_score, _ = pred_squares(src_temp, model, input_shape=[768] * 2, params=params)
                    if len(squares) == 0:
                        _, squares, array_score, _ = pred_squares(src_temp, model, params=params)
                except:
                    _, squares, array_score, _ = pred_squares(src_temp, model, params=params)
            elif min_pow > 512:
                _, squares, array_score, _ = pred_squares(src_temp, model, params=params)
    except:
        if min_pow > 768:
            try:
                _, squares, array_score, _ = pred_squares(src_temp, model, input_shape=[768] * 2, params=params)
            except:
                _, squares, array_score, _ = pred_squares(src_temp, model, params=params)
        elif min_pow > 512:
            _, squares, array_score, _ = pred_squares(src_temp, model, params=params)
    return squares, array_score

def square_four_lines(squares, array_score, shape, area_tolerance, pic_shape):
    max_flag = False
    h, w = shape
    if len(squares) != 0:
        square_lines = []
        length_s = len(squares)
        max = h * w
        min = area_tolerance * h * w
        for index, square in enumerate(squares):
            area = calculate_area(square[0][0], square[0][1], square[1][0], square[1][1], square[2][0], square[2][1], square[3][0], square[3][1])
            if area <= min or area >= max:
                continue
            if length_s > 1:
                total_score, _, _ = score_quadrilateral(square[0][0], square[0][1], square[1][0], square[1][1], square[2][0], square[2][1], square[3][0], square[3][1], pic_shape)
            else:
                total_score = 1
            total_score += array_score[index] / 3
            square_line = []
            square_line.append([square[0], square[1]])
            square_line.append([square[1], square[2]])
            square_line.append([square[2], square[3]])
            square_line.append([square[3], square[0]])
            square_line.append(float(round(total_score, 3)))
            square_lines.append(square_line)
        if len(square_lines) == 0:
            square_lines = [[[[0, 0], [w, 0]], [[w, 0], [w, h]], [[w, h], [0, h]], [[0, h], [0, 0]], 1]]
            max_flag = True
        return square_lines, max_flag
    else:
        return [[[[0, 0], [w, 0]], [[w, 0], [w, h]], [[w, h], [0, h]], [[0, h], [0, 0]], 1]], True

def get_line_info_tuple(lines):
    lines_tuple = []
    for line in lines:
        lines_tuple.append([(line[0], line[1]), (line[2], line[3])])
    return lines_tuple

def calculate_area(x1, y1, x2, y2, x3, y3, x4, y4):
    area = 0.5 * abs(x1*y2 + x2*y3 + x3*y4 + x4*y1 - y1*x2 - y2*x3 - y3*x4 - y4*x1)
    return area

def calculate_angle(x1, y1, x2, y2, x3, y3):
    # 向量 (x2, y2) -> (x1, y1) 和 (x2, y2) -> (x3, y3) 的角度
    v1x, v1y = x1 - x2, y1 - y2
    v2x, v2y = x3 - x2, y3 - y2
    dot_product = v1x * v2x + v1y * v2y
    magnitude1 = math.sqrt(v1x**2 + v1y**2)
    magnitude2 = math.sqrt(v2x**2 + v2y**2)
    # 检查是否有零向量
    if magnitude1 == 0 or magnitude2 == 0:
        return 0  # 或者选择其他合适的返回值

    cos_angle = dot_product / (magnitude1 * magnitude2)

    # 确保 cos_angle 在 [-1, 1] 范围内
    cos_angle = max(-1, min(1, cos_angle))
    angle = math.acos(cos_angle) * 180 / math.pi  # 转换为角度
    return abs(angle) / 90

def map_value_using_gaussian(input_value, target=856/540, sigma=0.2):
    # 计算高斯函数值
    exponent = -((input_value - target) ** 2) / (2 * sigma ** 2)
    output_value = math.exp(exponent)

    # 确保输出值在 0 到 1 之间
    return output_value

def calculate_aspect_ratio(x1, y1, x2, y2, x3, y3, x4, y4, pic_shape):
    side_lengths = [
        distance((x1, y1), (x2, y2)),
        distance((x2, y2), (x3, y3)),
        distance((x3, y3), (x4, y4)),
        distance((x4, y4), (x1, y1)),
    ]
    target = pic_shape[0] / pic_shape[1]
    temp1 = map_value_using_gaussian(side_lengths[0] / side_lengths[1] if side_lengths[1] != 0 else sys.maxsize, target=target)
    temp2 = map_value_using_gaussian(side_lengths[0] / side_lengths[3] if side_lengths[3] != 0 else sys.maxsize, target=target)
    temp3 = map_value_using_gaussian(side_lengths[2] / side_lengths[1] if side_lengths[1] != 0 else sys.maxsize, target=target)
    temp4 = map_value_using_gaussian(side_lengths[2] / side_lengths[3] if side_lengths[3] != 0 else sys.maxsize, target=target)
    return (temp1 + temp2 + temp3 + temp4) / 4

def score_quadrilateral(x1, y1, x2, y2, x3, y3, x4, y4, pic_shape):
    angles = [
        calculate_angle(x1, y1, x2, y2, x3, y3),
        calculate_angle(x2, y2, x3, y3, x4, y4),
        calculate_angle(x3, y3, x4, y4, x1, y1),
        calculate_angle(x4, y4, x1, y1, x2, y2)
    ]
    aspect_ratio = calculate_aspect_ratio(x1, y1, x2, y2, x3, y3, x4, y4, pic_shape)
    
    # 评分
    angle_scores = [map_value_using_gaussian(angle, 1) for angle in angles]

    # 综合评分
    angle_score = sum(angle_scores) / 4
    total_score =  angle_score + aspect_ratio
    return total_score, angles, aspect_ratio

# def extract_and_warp_image(img, points, output_size=(540, 856)):
#     if not isinstance(points, np.ndarray):
#         points = np.array(points, dtype='float32')
#     reserve_flag = False
#     if distance(points[0], points[1]) < distance(points[1], points[2]):
#         output_size = output_size[::-1]
#     # 定义目标图像的四个角点
#     target_points = np.array([
#         [0, 0],
#         [output_size[1] - 1, 0],
#         [output_size[1] - 1, output_size[0] - 1],
#         [0, output_size[0] - 1]
#     ], dtype="float32")

#     # 计算透视变换矩阵
#     M = cv2.getPerspectiveTransform(points, target_points)
    
#     # 应用透视变换
#     warped = cv2.warpPerspective(img, M, (output_size[1], output_size[0]))
#     if reserve_flag:
#         warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
#     return warped

# def main():
#     #[large, tiny]
#     model_type = 'large'
#     model = get_model(model_type)
#     original_pic_floader = './1'
#     merged_pic_floader = f'./merged_{model_type}'
#     cut_pic_floader = f'./cuted_{model_type}'
#     os.makedirs(merged_pic_floader, exist_ok=True)
#     os.makedirs(cut_pic_floader, exist_ok=True)
#     original_pic_names = os.listdir(original_pic_floader)
#     if '.DS_Store' in original_pic_names:
#         original_pic_names.remove('.DS_Store')
#     start = datetime.now()
#     for pic_name in original_pic_names:
#         pic_path = os.path.join(original_pic_floader, pic_name)
#         squares, img = get_square_dots(pic_path, model)
#         h, w, _ = img.shape
#         squares_lines = square_four_lines(squares, (h, w), 0.2)
#         squares_lines = sorted(squares_lines, key=lambda x:x[4], reverse=False)
#         final_square = squares_lines[-1][:4]
#         draw_lines_on_pic(copy.deepcopy(img), final_square, os.path.join(merged_pic_floader, pic_name))
#         cuted = extract_and_warp_image(copy.deepcopy(img), [final_square[0][0], final_square[0][1], final_square[2][0], final_square[2][1]])
#         cv2.imwrite(os.path.join(cut_pic_floader, pic_name), cuted)
#     end = datetime.now()

# if __name__ == "__main__":
#     main()