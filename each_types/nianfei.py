from my_utils.operate_excel import Pair
from my_utils.operate_word import number_to_chinese
import each_types.kaidan as kaidan
import each_types.zhuandan as zhuandan

def get_sub_arr_nianfei(kaidan_pair:Pair):
    changes = []
    client_company_flag, entrusted_company_flag, client_company_name, entrusted_company_name = zhuandan.get_company_flag(kaidan_pair)
    client_str, entrusted_str = kaidan.page_two(kaidan_pair, client_company_flag, entrusted_company_flag)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(kaidan_pair, client_company_flag=client_company_flag, entrusted_company_flag=entrusted_company_flag)
    changes.extend([client_str, entrusted_str])
    changes.append(kaidan_pair.client.sail_card_id)
    annual_fee = kaidan_pair.client.annual_fee
    annual_fee_ch = number_to_chinese(annual_fee)
    changes.extend([annual_fee, annual_fee_ch])
    changes.append(kaidan_pair.client.name)
    changes.append(kaidan_pair.entrusted.sail_card_id)
    client_str, entrusted_str = kaidan.page_five(kaidan_pair, client_company_flag, entrusted_company_flag)
    changes.extend([client_str, entrusted_str])
    changes.extend([kaidan_pair.entrusted.name if not entrusted_company_flag else entrusted_company_name, kaidan_pair.client.name if not client_company_flag else client_company_name])
    changes.extend([kaidan_pair.client.name if not client_company_flag else client_company_name, kaidan_pair.entrusted.name if not entrusted_company_flag else entrusted_company_name])
    client_str, entrusted_str = kaidan.page_six(kaidan_pair, client_company_flag, entrusted_company_flag)
    changes.extend([client_str, entrusted_str])
    changes.extend([annual_fee, annual_fee_ch])
    return changes