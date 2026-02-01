from my_utils.operate_excel import Pair
from my_utils.operate_word import number_to_chinese
import each_types.kaidan as kaidan

def get_sub_arr_nianfei(kaidan_pair:Pair):
    changes = []
    client_str, entrusted_str = kaidan.page_two(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.append(kaidan_pair.client.sail_card_id)
    annual_fee = kaidan_pair.client.annual_fee
    annual_fee_ch = number_to_chinese(annual_fee)
    changes.extend([annual_fee, annual_fee_ch])
    changes.append(kaidan_pair.entrusted.sail_card_id)
    client_str, entrusted_str = kaidan.page_five(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.extend([kaidan_pair.entrusted.name, kaidan_pair.client.name])
    changes.extend([kaidan_pair.client.name, kaidan_pair.entrusted.name])
    client_str, entrusted_str = kaidan.page_six(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.extend([annual_fee, annual_fee_ch])
    return changes