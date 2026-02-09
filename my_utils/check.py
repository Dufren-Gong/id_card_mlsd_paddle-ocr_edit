import re
from datetime import datetime
import pandas as pd
from my_utils.Traditional_to_Simplified_Chinese import fan_to_jian
from my_utils.utils import get_config, get_beijing_date

config = get_config()
moren_pay = config['moren_pay']
moren_buy = config['moren_buy']
annual_fee = config['moren_annual_fee']
max_cash = config['max_cash']
try:
    overall_days = int(config['tolerate_days'])
    if overall_days <= 0:
        overall_days = 30
except:
    overall_days = 30
check_back_flag = config['check_back']
real_date = get_beijing_date()

ethnic_groups = [
    "汉族", "壮族", "满族", "回族", "苗族", "维吾尔族", "土家族", "彝族", "蒙古族", "藏族", 
    "布依族", "侗族", "瑶族", "朝鲜族", "白族", "哈尼族", "哈萨克族", "黎族", "傣族", 
    "畲族", "傈僳族", "仡佬族", "东乡族", "高山族", "拉祜族", "水族", "佤族", "纳西族", 
    "羌族", "土族", "仫佬族", "锡伯族", "柯尔克孜族", "景颇族", "达斡尔族", "撒拉族", 
    "毛南族", "裕固族", "保安族", "阿昌族", "普米族", "塔吉克族", "怒族", "乌孜别克族", 
    "俄罗斯族", "鄂温克族", "德昂族", "鄂伦春族", "独龙族", "基诺族", "塔塔尔族", "赫哲族", 
    "珞巴族", "门巴族"
]

sex_group = ['男', '女']

def trans_to_str_and_strip(str_t:str, trans_str:str=''):
    str_t = re.sub(r'\s+', trans_str, str(str_t))
    return str_t

def is_chinese(str_t:str, mode:str='内地'):
    return bool(re.fullmatch(r'[\u4e00-\u9fff\u00b7]+', str_t))

def check_name(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        str_t = trans_to_str_and_strip(str_t)
        #匹配中文和少民中间的·
        if is_chinese(str_t) and 1 < len(str_t):
            if mode == '香港':
                str_t = fan_to_jian(str_t)
            return str_t
    return None

def check_sex(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        str_t = trans_to_str_and_strip(str_t).rstrip('性')
        if str_t in sex_group:
            return str_t
    return None

def check_nation(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        str_t = trans_to_str_and_strip(str_t).rstrip('族')
        if str_t + '族' in ethnic_groups:
            return str_t
    return None

def check_birth(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        birth = str_t
        passed_flag = False
        if '年' in birth and '月' in birth and '日' in birth:
            birth_info = re.sub(r'[年月日]', ' ', birth).split(' ')
            if len(birth_info) == 4 and birth_info[3] == '' and (0 < len(birth_info[2]) <= 2) and (0 < len(birth_info[1]) <= 2) and len(birth_info[0]) == 4:
                birth_info = birth_info[:-1]
                passed_flag = True
        else:
            birth_info = birth.split('-')
            if len(birth_info) == 3 and (0 < len(birth_info[0]) <= 2) and (0 < len(birth_info[1]) <= 2) and len(birth_info[2]) == 4:
                birth_info = list(reversed(birth_info))
                passed_flag = True
        if passed_flag:
            if birth_info[1][0] == "0":
                birth_info[1] = birth_info[1][1:]
            if birth_info[2][0] == "0":
                birth_info[2] = birth_info[2][1:]
            try:
                year, month, day = map(int, birth_info)
                datetime(year, month, day)
            except:
                return None
            if 1910 < eval(birth_info[0]) < 2070:
                birth = birth_info[0] + "年" + birth_info[1] + "月" + birth_info[2] + "日"
                return birth
    return None

def check_open_date(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        data = trans_to_str_and_strip(str_t, ' ').strip()
        data_info = []
        if '年' in data and '月' in data and ('日' in data or '号' in data):
            data_info = re.sub(r'[年月日号]', ' ', data).split(' ')
        else:
            gap = data.translate(str.maketrans('', '', '0123456789'))
            if len(gap) == 2 and gap[0] == gap[1]:
                data_info = data.split(gap[0])
        if data_info != []:
            if len(data_info) == 3 and len(data_info[2]) == 4:
                data_info = list(reversed(data_info))
            str_temp = data_info[0] + '年' + data_info[1] + '月' + data_info[2] + '日'
            return check_birth(str_temp)
    return None

def check_address(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        str_t = trans_to_str_and_strip(str_t)
        if not bool(re.fullmatch(r'[A-Za-z0-9,.-]+', str_t)) and len(str_t) > 5:
            return str_t
            # return remove_first_char_if_symbol_or_digit(str_t)
    return None

def check_id(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        str_t = re.sub(r'（', '(', re.sub(r'）', ')', trans_to_str_and_strip(str_t).upper()))
        if '(' in str_t and ')' in str_t:
            if len(str_t) == 10:
                str_t = re.sub(r'（', '(', re.sub(r'）', ')', str_t))
                if str_t[0].isalpha() and str_t[-3] == '(' and (str_t[-2].isalpha() or str_t[-2].isdigit()) and str_t[-1] == ')' and bool(re.fullmatch(r'[0-9]+', str_t[1:7])):
                    return str_t
        else:
            if len(str_t) == 18:
                if (str_t[-1] == 'X' and bool(re.fullmatch(r'[0-9]+', str_t[:-1]))) or bool(re.fullmatch(r'[0-9]+', str_t)):
                    return str_t
    return None

def check_aviable_data(str_t:str, mode:str='内地'):
    if check_back_flag:
        if not pd.isna(str_t) and str_t != None and str_t != '':
            data = trans_to_str_and_strip(str_t, ' ').strip()
            if data == "长期":
                return data
            # 基本校验
            elif len(data) != 8 or not data.isdigit():
                return None
            try:
                expiry_date = datetime.strptime(data, "%Y%m%d").date()
            except ValueError:
                return None
            today = datetime.strptime(real_date, "%Y%m%d").date()
            delta_days = (expiry_date - today).days
            if delta_days >= overall_days:
                return delta_days
            elif 0 < delta_days < overall_days:
                return [delta_days]
            else:
                return '3'
    else:
        return '1'

card_info_check = dict(
    姓名=check_name,
    性别=check_sex,
    民族=check_nation,
    生日=check_open_date,
    住址=check_address,
    卡号=check_id,
    有效期=check_aviable_data
)

def check_phone_number(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        telephone = re.sub(r'\s+', '', str(str_t)).strip()
        telephone = re.sub(r'[＋]+', '+', telephone)
        if '+' in telephone and len(telephone) >= 11:
            if telephone[4] != ' ' and len(telephone) == 12:
                telephone = telephone[:4] + ' ' + telephone[4:]
            if len(telephone) == 13:
                telephone_temp = re.sub(r'[+\s]', '', telephone)
                if bool(re.fullmatch(r'[0-9]+', telephone_temp)):
                    return telephone
        else:
            telephone = trans_to_str_and_strip(telephone)
            if len(telephone) == 11 and bool(re.fullmatch(r'[0-9]+', telephone)):
                return telephone
    return None

def check_cash(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        if bool(re.fullmatch(r'[0]+', str_t)):
            cash = '0'
        else:
            cash = trans_to_str_and_strip(str_t).lstrip('0')
        if bool(re.fullmatch(r'[0-9.]+', cash)):
            try:
                cash = int(eval(cash))
                if cash >= 0 and cash <= max_cash:
                    return str(cash)
                else:
                    return None
            except:
                return None
    return None

def check_sail_card_id(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        sail_card_id = trans_to_str_and_strip(str_t)
        if bool(re.fullmatch(r'[0-9]+', sail_card_id)):
            if len(sail_card_id) == 8:
                return str(sail_card_id)
    return None

def check_sail_id(str_t:str, mode:str='内地'):
    if not pd.isna(str_t) and str_t != None and str_t != '':
        sail_id = trans_to_str_and_strip(str_t)
        if len(sail_id) == 12 and bool(re.fullmatch(r'[A-Za-z]+', sail_id[:4])) and bool(re.fullmatch(r'[A-Za-z0-9]+', sail_id[4:])):
                return sail_id.upper()
    return None

excel_info_check = dict(
    姓名=check_name,
    电话=check_phone_number,
    金额=check_cash,
    日期=check_open_date,
    经销商卡号=check_sail_card_id,
    货单号=check_sail_id,
    住址=check_address
)
