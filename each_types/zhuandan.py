from my_utils.operate_excel import Pair
from my_utils.operate_word import number_to_chinese
import each_types.kaidan as kaidan
import copy

def get_gap_flag(data_str, before, after):
    data_str = data_str.strip().replace(' ', '')
    gap = [2023, 6, 30]
    info1 = data_str.split('年')
    year = eval(info1[0].replace(' ', '').lstrip('0'))
    if year > gap[0]:
        return after
    elif year == gap[0]:
        info2 = info1[1].split('月')
        yue = eval(info2[0].replace(' ', '').lstrip('0'))
        if yue > gap[1]:
            return after
        elif yue == gap[1]:
            ri = eval(info2[1].rstrip('日').replace(' ', '').lstrip('0'))
            if ri == gap[2]:
                return after
    return before

def get_sub_arr_zhuanrang(kaidan_pair:Pair, before, after):
    changes = []
    client_str, entrusted_str = kaidan.page_two(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    left_money = kaidan_pair.client.left_money
    left_money_ch = number_to_chinese(left_money)
    changes.extend([left_money, left_money_ch])
    changes.append(kaidan_pair.client.sail_id)
    changes.append(kaidan_pair.client.sail_card_id)
    changes.append(kaidan_pair.client.open_date)
    gap = get_gap_flag(kaidan_pair.client.open_date, before, after)
    changes.append(gap)
    annual_fee = kaidan_pair.client.annual_fee
    annual_fee_ch = number_to_chinese(annual_fee)
    changes.extend([annual_fee, annual_fee_ch])
    changes.extend([kaidan_pair.client.name, kaidan_pair.entrusted.name])
    changes.append(kaidan_pair.client.name)
    changes.append(kaidan_pair.client.sail_card_id)
    changes.append(kaidan_pair.client.id)
    changes.extend([kaidan_pair.client.name, kaidan_pair.entrusted.name])
    client_str, entrusted_str = kaidan.page_six(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.append(kaidan_pair.client.open_date)
    changes.append(gap)
    return changes, kaidan_pair

def get_sub_arr_shouquan(kaidan_pair:Pair, company_id):
    changes = []
    temp = copy.deepcopy(kaidan_pair)
    temp.swap_client_and_entrusted()
    temp.swap_entrusted_and_beiweituo()
    client_str, entrusted_str = kaidan.page_two(temp)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(temp)
    changes.extend([client_str, entrusted_str])
    if company_id == 'SIBELLAC_HOLDINGS_LIMITED':
        changes.append(temp.client.name)
    elif company_id == 'BASTION':
        changes.append(temp.beiweituo.name)
    changes.append(temp.beiweituo.sail_card_id)
    changes.append(temp.beiweituo.sail_id)
    client_str, entrusted_str = kaidan.page_five(temp)
    changes.extend([client_str, entrusted_str])
    changes.extend([temp.entrusted.name, temp.client.name])
    changes.extend([temp.client.name, temp.entrusted.name])
    client_str, entrusted_str = kaidan.page_six(temp)
    changes.extend([client_str, entrusted_str])
    return changes, temp

def get_sub_arr_nianfei(kaidan_pair:Pair):
    changes = []
    temp = copy.deepcopy(kaidan_pair)
    temp.swap_entrusted_and_beiweituo()
    client_str, entrusted_str = kaidan.page_two(temp)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(temp)
    changes.extend([client_str, entrusted_str])
    changes.append(temp.client.sail_card_id)
    annual_fee = temp.client.annual_fee
    annual_fee_ch = number_to_chinese(annual_fee)
    changes.extend([annual_fee, annual_fee_ch])
    changes.append(temp.entrusted.sail_card_id)
    client_str, entrusted_str = kaidan.page_five(temp)
    changes.extend([client_str, entrusted_str])
    changes.extend([temp.entrusted.name, temp.client.name])
    changes.extend([temp.client.name, temp.entrusted.name])
    client_str, entrusted_str = kaidan.page_six(temp)
    changes.extend([client_str, entrusted_str])
    changes.extend([annual_fee, annual_fee_ch])
    return changes, temp
