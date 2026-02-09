from my_utils.operate_excel import People_Info, Pair
from my_utils.operate_word import number_to_chinese
import shutil, os

def get_name_id_str(obj:People_Info):
    if obj.native == "香港":
        return f"{obj.name}(香港永久性居民身份证号码：{obj.id})"
    else:
        return f"{obj.name}(公民身份证号码：{obj.id})"
    
def get_name_id_st_without_kuohao(obj:People_Info):
    if obj.native == "香港":
        return f"{obj.name}，香港永久性居民身份证号码：{obj.id}。"
    else:
        return f"{obj.name}，公民身份证号码：{obj.id}。"

def get_name_sex_regin_birth_address_id_telephone(obj:People_Info, mode=''):
    if obj.native == "香港":
        return_str = f"{obj.name}，{obj.sex}，{obj.birth}出生，住址：{obj.address}，香港永久性居民身份证号码：{obj.id}，联系电话：{obj.telephone}"
    else:
        return_str = f"{obj.name}，{obj.sex}，{obj.regin}族，{obj.birth}出生，住址：{obj.address}，公民身份证号码：{obj.id}，联系电话：{obj.telephone}"
    if mode == 'id':
        return_str += f'，独立经销商卡号：{obj.sail_card_id}'
    return return_str + '。'

def page_two(pair:Pair):
    client_str = get_name_id_str(pair.client)
    entrusted_str = get_name_id_str(pair.entrusted)
    return client_str, entrusted_str

def page_three(pair:Pair, mode=''):
    client_str = get_name_sex_regin_birth_address_id_telephone(pair.client, mode)
    entrusted_str = get_name_sex_regin_birth_address_id_telephone(pair.entrusted, mode)
    return client_str, entrusted_str

def page_five(pair:Pair):
    client_str = get_name_id_st_without_kuohao(pair.client)
    entrusted_str = get_name_id_st_without_kuohao(pair.entrusted)
    return client_str, entrusted_str 

def page_six(pair:Pair):
    client_str = get_name_sex_regin_birth_address_id_telephone(pair.client)
    entrusted_str = get_name_sex_regin_birth_address_id_telephone(pair.entrusted)
    client_str = client_str.rsplit("联系电话", maxsplit=1)[0][:-1] + '。'
    entrusted_str = entrusted_str.rsplit("联系电话", maxsplit=1)[0][:-1] + '。'
    return client_str, entrusted_str  

def get_sub_arr(kaidan_pair:Pair, mode = ''):
    changes = []
    client_str, entrusted_str = page_two(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = page_three(kaidan_pair, mode)
    changes.extend([client_str, entrusted_str])
    pay = kaidan_pair.client.pay
    pay_ch = number_to_chinese(pay)
    changes.extend([pay, pay_ch])
    annual_fee = kaidan_pair.client.annual_fee
    annual_fee_ch = number_to_chinese(annual_fee)
    changes.extend([annual_fee, annual_fee_ch])
    buy = kaidan_pair.client.buy
    buy_ch = number_to_chinese(buy)
    changes.extend([buy, buy_ch])
    extract = kaidan_pair.client.extract
    extract_ch = number_to_chinese(extract)
    changes.extend([extract, extract_ch])
    changes.extend([annual_fee, annual_fee_ch])
    client_str, entrusted_str = page_five(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.extend([kaidan_pair.entrusted.name, kaidan_pair.client.name])
    changes.extend([kaidan_pair.client.name, kaidan_pair.entrusted.name])
    client_str, entrusted_str = page_six(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    return changes

def move_pic(kaidan_pair:Pair, folder_path, target_path, pic_num=2):
    names = os.listdir(folder_path)
    all_names = [kaidan_pair.client.name, kaidan_pair.entrusted.name]
    if pic_num == 3:
        all_names.append(kaidan_pair.beiweituo.name)
    for name in all_names:
        names_tmep = [i for i in names if name in i]
        for this_name in names_tmep:
            shutil.copy(os.path.join(folder_path, this_name), os.path.join(target_path, this_name))
