import os
# os.environ['FLAGS_use_cuda_allocator'] = '0'
from cv2 import resize as cv2resize
from cv2 import INTER_AREA as cv2INTER_AREA
import re, gc, os
from onnxocr.onnx_paddleocr import ONNXPaddleOcr
from my_utils.utils import rgb_to_gray_with_three_channels, change_three_channel
from datetime import datetime
import string

def remove_first_char_if_symbol_or_digit(input_str):
    # 检查第一个字符是否是符号或者阿拉伯数字
    if input_str and (input_str[0] in string.punctuation or input_str[0].isdigit()):
        # 删除第一个字符
        return input_str[1:]
    return input_str

def clear_gpu_cache():
    gc.collect()

def get_ocr_model(global_config):
    pwd = os.getcwd()
    os.chdir('..')
    use_angle_cls = global_config['paddleocr_conf']['use_cls']
    if global_config['paddleocr_conf']['device'] == 'gpu':
        try:
            model = ONNXPaddleOcr(use_angle_cls=use_angle_cls, use_gpu=True)
        except:
            model = None
    else:
        model = ONNXPaddleOcr(use_angle_cls=use_angle_cls, use_gpu=False)
    os.chdir(pwd)
    return model

def check_nation(texts):
    nation = '内地'
    line = texts[0]
    if '香港' in line or '永久' in line or '證' in line:
        nation = '香港'
    return nation

def get_catch(texts, nation, catch, info_checks, check_back):
    if nation == '内地':
        if catch == None:
            catch = [None] * 7
        catch = get_infos(texts, catch, info_checks, check_back)
    elif nation == '香港':
        if catch == None:
            catch = [None, None, "无", None, "无", None, '无']
        catch = get_infos_hk(texts, catch)
    return catch

def sort_boxes_by_line(boxes, threshold=10):
    all_lines = boxes[0]
    sort_by_y = sorted(all_lines, key=lambda x: x[0][2][1])
    infos = []
    this_line = []
    lengths = len(sort_by_y)
    compare_y = sort_by_y[0][0][0][1]
    for line_index in range(lengths):
        this_y = sort_by_y[line_index][0][0][1]
        if abs(this_y - compare_y) <= threshold:
            this_line.append(sort_by_y[line_index])
        else:
            infos.append(this_line)
            this_line = [sort_by_y[line_index]]
        if line_index == lengths - 1:
            infos.append(this_line)
        compare_y = this_y
    temp = []
    for line in infos:
        line = sorted(line, key=lambda x: x[0][0][0])
        line = [i[1][0].strip().replace(' ', '') for i in line]
        temp.append(line)
    return [''.join(i) for i in temp]

def pic_to_str(image, ocr, pass_flag=False, shape = (856, 540), scale = 0.8, times = 1, pic_type='origin', info_checks = dict(), one_line_scale = 30, check_back = False):
    if pass_flag:
        return ['None'] * 8, ['error']
    if scale > 1.0:
        scale = 1.0
    # img_temp = cv2resize(change_three_channel(image), (int(shape[0] * scale), int(shape[1] * scale)), interpolation=cv2INTER_AREA)
    if scale != 1.0:
        img_origin = cv2resize(change_three_channel(image), (int(shape[0] * scale), int(shape[1] * scale)), interpolation=cv2INTER_AREA)
    else:
        img_origin = change_three_channel(image)
    if pic_type == 'origin':
        img_temp = img_origin
        next = 'grey'
    else:
        img_temp = rgb_to_gray_with_three_channels(img_origin)
        next = 'origin'
    catch = None
    texts = []
    nation = None
    length1 = 0
    results = ocr.ocr(img_temp)
    if results != [None] and results != [[]]:
        texts = sort_boxes_by_line(results, shape[1] / one_line_scale)
        nation = check_nation(texts)
        catch = get_catch(texts, nation, catch, info_checks, check_back)
    if times == 2:
        if next == 'origin':
            img_temp = img_origin
        else:
            img_temp = rgb_to_gray_with_three_channels(img_origin)
        texts1 = []
        length2 = 0
        results = ocr.ocr(img_temp)
        if results != [None] and results != [[]]:
            texts = sort_boxes_by_line(results, shape[1] / one_line_scale)
            if nation != "香港":
                nation = check_nation(texts1)
            catch = get_catch(texts1, nation, catch, info_checks, check_back)
    if nation == None:
        nation = '内地'
    if catch != None:
        catch.append(nation)
        if catch[5] != None:
            catch[5] = catch[5].upper()
        if times == 2:
            t = [(length1, texts), (length2, texts1)]
            t = sorted(t, key=lambda x: x[0])
            t = t[-1][-1]
            return catch, t
        else:
            return catch, texts
    else:
        return [None] * 7 + ['未识别出来'], ['']

def remove_digits_and_letters(input_string, no_num = False):
    if not no_num:
        # 使用正则表达式匹配并替换数字和字母
        return re.sub(r'[a-zA-Z0-9\W_]', '', input_string)
    else:
        # 使用正则表达式匹配并替换数字和字母
        return re.sub(r'[a-zA-Z\W_]', '', input_string)

def get_infos(infos, catch, info_checks, check_back):
    name_checks = info_checks['name_checks']
    nation_checks = info_checks['nation_checks']
    sex_checks = info_checks['sex_checks']
    birth_checks = info_checks['birth_checks']
    address_checks = info_checks['address_checks']
    deadline_chinese_checks = info_checks['deadline_checks']['chinese_checks']
    dealline_symble_checks = info_checks['deadline_checks']['symble_checks']
    changqi_checks = info_checks['deadline_checks']['changqi_checks']
    for index, line in enumerate(infos):
        line = line.strip()
        if any(m in line for m in name_checks):
            for m in name_checks:
                if m in line:
                    name = line.split(m)[-1].replace(' ', '')
                    name = remove_digits_and_letters(name)
                    break
            if name != '':
                try:
                    name_2 = infos[index + 1].strip().replace(' ', '')
                    if (any(m in line for m in sex_checks) or any(m in line for m in nation_checks)) and index != 0:
                        name_2 = infos[index - 1].strip().replace(' ', '')
                    name_2 = remove_digits_and_letters(name_2)
                    if len(name_2) == 1 and not bool(re.fullmatch(r'[A-Za-z0-9]+', name_2)):
                        name += name_2
                except:
                    pass
                if not bool(re.fullmatch(r'[A-Za-z0-9]+', name)):
                    if catch[0] == None or (catch[0] != None and len(catch[0]) < len(name)):
                        catch[0] = name
            else:
                try:
                    name = infos[index + 1].strip().replace(' ', '')
                    name = remove_digits_and_letters(name)
                    if ('性别' in name or bool(re.fullmatch(r'[A-Za-z0-9]+', name))) and index != 0:
                        name = infos[index - 1].strip().replace(' ', '')
                    else:
                        try:
                            name_2 = infos[index + 2].strip().replace(' ', '')
                            name_2 = remove_digits_and_letters(name_2)
                            if len(name_2) == 1 and not bool(re.fullmatch(r'[A-Za-z0-9]+', name_2)):
                                name += name_2
                        except:
                            pass
                    if not bool(re.fullmatch(r'[A-Za-z0-9]+', name)):
                        if catch[0] == None or (catch[0] != None and len(catch[0]) < len(name)):
                            catch[0] = name
                except:
                    pass
            continue
        if any(m in line for m in sex_checks):
            if catch[0] == None:
                if index != 0:
                    name = infos[index - 1].strip().replace(' ', '')
                    name = remove_digits_and_letters(name)
                    if len(name) > 1 and not bool(re.fullmatch(r'[A-Za-z0-9]+', name)):
                        catch[0] = name
                    else:
                        if index >=2:
                            name = infos[index - 2].strip().replace(' ', '')
                            name = remove_digits_and_letters(name)
                            if len(name) > 1 and not bool(re.fullmatch(r'[A-Za-z0-9]+', name)):
                                catch[0] = name
            for m in sex_checks:
                if m in line:
                    sex = line.split(m)[-1].replace(' ', '')
                    break
            for nation_check in nation_checks:
                if nation_check in line:
                    sex = sex.split(nation_check)[0]
                    sex = remove_digits_and_letters(sex)
                    break
            if sex != '':
                if not bool(re.fullmatch(r'[A-Za-z0-9]+', sex)):
                    if catch[1] == None or (catch[1] != None and len(catch[1]) > len(sex)):
                        catch[1] = sex
            else:
                try:
                    sex = infos[index + 1].strip().replace(' ', '')
                    sex = remove_digits_and_letters(sex)
                    if not bool(re.fullmatch(r'[A-Za-z0-9]+', sex)):
                        if catch[1] == None or (catch[1] != None and len(catch[1]) > len(sex)):
                            catch[1] = sex
                except:
                    pass
        if any(m in line for m in nation_checks):
            for m in nation_checks:
                if m in line:
                    nation = line.split(m)[-1].replace(' ', '')
                    nation = remove_digits_and_letters(nation)
                    break
            if nation != '':
                if not bool(re.fullmatch(r'[A-Za-z0-9]+', nation)):
                    if catch[2] == None or (catch[2] != None and len(catch[2]) > len(nation)):
                        catch[2] = nation
            else:
                try:
                    nation = infos[index + 1].strip().replace(' ', '')
                    nation = remove_digits_and_letters(nation)
                    if not bool(re.fullmatch(r'[A-Za-z0-9]+', nation)):
                        if catch[2] == None or (catch[2] != None and len(catch[2]) > len(nation)):
                            catch[2] = nation
                except:
                    pass
        if any(m in line for m in birth_checks) and (('年' in line and '月' in line) or ('年' in line and '日' in line) or ('月' in line and '日' in line)):
            for m in birth_checks:
                if m in line:
                    birth = line.split(m)[-1]
                    birth = remove_digits_and_letters(birth, True)
                    break
            if birth != '' and bool(re.fullmatch(r'[0-9]+', birth.replace('年', '').replace('月', '').replace('日', ''))):
                if catch[3] == None:
                    catch[3] = birth
                elif len(birth) > len(catch[3]):
                    catch[3] = birth
            else:
                try:
                    birth = infos[index + 1].strip()
                    birth = remove_digits_and_letters(birth, True)
                    if ('年' in birth and '月' in birth) or ('年' in birth and '日' in birth) or ('月' in birth and '日' in birth) and bool(re.fullmatch(r'[0-9]+', birth.replace('年', '').replace('月', '').replace('日', ''))):
                        if catch[3] == None:
                            catch[3] = birth
                        elif len(birth) > len(catch[3]):
                            catch[3] = birth
                except:
                    pass
            continue
        #优先级顺序
        if any(m in line for m in address_checks):
            for i in address_checks:
                if i in line:
                    location = line.split(i)[-1]
                    if '中国' in location:
                        info_a = location.rsplit('中国', maxsplit = 1)
                        if len(info_a[-1]) <= 5 and len(info_a[0]) != '':
                            location = info_a[0]
                    if location.endswith('china'):
                        location = location.rstrip('china')
                    elif location.endswith('CHINA'):
                        location = location.rstrip('CHINA')
                    break
            t = index + 1
            for i in range(3):
                try:
                    next = infos[t + i].strip().replace(' ', '')
                    if '身份' not in next and '号码' not in next and '公民' not in next and len(re.findall(r'\d', next)) < 12 and (not bool(re.fullmatch(r'[A-Za-z0-9]+', next)) or bool(re.fullmatch(r'[0-9]+', next))):
                        if '中国' in next:
                            info_a = next.rsplit('中国', maxsplit = 1)
                            if len(info_a[-1]) <= 5 and len(info_a[0]) != '':
                                next = info_a[0]
                        if next.endswith('china'):
                            next = next.rstrip('china')
                        elif next.endswith('CHINA'):
                            next = next.rstrip('CHINA')
                        if len(next) != 0:
                            location += next
                except:
                    pass
            location = remove_first_char_if_symbol_or_digit(location)
            if catch[4] == None:
                catch[4] = location
            else:
                if len(location) <= len(catch[4]) and len(location) > 5:
                    catch[4] = location
            continue
        if ('身份' in line or '号码' in line or '公民' in line) and catch[5] == None:
            if line[-1].upper() == 'X':
                add = 'X'
            else:
                add = ''
            number = ''.join(re.findall(r'\d', line))
            if number == '':
                if index != len(infos) - 1:
                    next = infos[index + 1]
                    if next[-1].upper == 'X':
                        add = 'X'
                    else:
                        add = ''
                    next = ''.join(re.findall(r'\d', next))
                    if next.isdigit():
                        final = next + add
                        #前面多出一位
                        if len(final) == 19:
                            bir_check = final[7:15]
                            try:
                                datetime(bir_check[:4], bir_check[4:6], bir_check[6:])
                                final = final[1:]
                            except:
                                pass
                        catch[5] = final
            else:
                final = number + add
                #前面多出一位
                if len(final) == 19:
                    bir_check = final[7:15]
                    try:
                        datetime(int(bir_check[:4]), int(bir_check[4:6]), int(bir_check[6:]))
                        final = final[1:]
                    except:
                        pass
                catch[5] = final
        #如果需要检查背面的话
        if check_back:
            if any(m in line for m in changqi_checks):
                catch[6] = '长期'
            elif any(m in line for m in deadline_chinese_checks):
                for m in dealline_symble_checks:
                    if m in line:
                        deadline = re.sub(r"\D", "", line.strip().split(m)[-1])
                        break
                if deadline != '':
                    if catch[6] == None and len(deadline) == 8:
                        try:
                            datetime(int(deadline[:4]), int(deadline[4:6]), int(deadline[6:]))
                            catch[6] = deadline
                        except:
                            pass
    return catch

def is_all_chinese(string):
    for char in string:
        # 检查每个字符是否在中文范围内
        if not ('\u4e00' <= char <= '\u9fff' or
                '\u3400' <= char <= '\u4DBF' or
                '\u20000' <= char <= '\u2A6DF' or
                '\u2A700' <= char <= '\u2B73F' or
                '\u2B740' <= char <= '\u2B81F' or
                '\u2B820' <= char <= '\u2CEAF'):
            return False
    return True

def get_infos_hk(infos, catch):
    for index, line in enumerate(infos):
        if (index == 0 and ('香港' in line or '永久' in line or '居民' in line or '身份' in line)) or index == 1:
            continue
        line = line.strip().replace(' ', '')
        if index == 2:
            if not is_all_chinese(line):
                match = re.search(r'[a-zA-Z]', line)
                if match:
                    line = line.split(match.group(0), maxsplit = 1)[0]  # 返回找到的第一个英文字母
            if catch[0] == None:
                catch[0] = line
            else:
                if len(line) > len(catch[0]):
                    catch[0] = line
            continue
        if "出生" in line or '日期' in line:
            next = infos[index + 1]
            if "男" in next:
                if catch[1] == None:
                    catch[1] = '男'
                if catch[3] == None:
                    catch[3] = next.split('男')[0]
            elif "女" in next:
                if catch[1] == None:
                    catch[1] = '女'
                if catch[3] == None:
                    catch[3] = next.split('女')[0]
            else:
                if '-' in next and list(next).count('-') == 2:
                    if catch[3] == None:
                        catch[3] = next.strip()
                    try:
                        next = infos[index + 2]
                    except:
                        next = ''
                    if "男" in next:
                        if catch[1] == None:
                            catch[1] = '男'
                    elif "女" in next:
                        if catch[1] == None:
                            catch[1] = '女'
            continue
        if ('(' in line or ')' in line or '（' in line or '（' in line) and (list(line).count('-') == 2 or list(line).count('-') == 0):
            line = line.replace('（', '(').replace('）', ')')
            if '-' in line:
                line = line.split('-')[-1]
                match = re.search(r'[a-zA-Z]', line)
                if match:
                    line = match.group(0) + line.split(match.group(0), maxsplit = 1)[1]  # 返回找到的第一个英文字母
            if catch[5] == None:
                catch[5] = line
            else:
                if len(line) > len(catch[5]):
                    catch[5] = line
    return catch