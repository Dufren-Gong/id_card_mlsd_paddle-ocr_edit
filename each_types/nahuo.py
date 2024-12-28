from my_utils.operate_excel import People_Info, Pair
from my_utils.operate_word import number_to_chinese
import each_types.kaidan as kaidan

def get_sail_id_str(obj:People_Info):
    return f"{int(obj.sail_card_id)}"

def page_three(pair:Pair):
    client_str = get_sail_id_str(pair.client)
    entrusted_str = get_sail_id_str(pair.entrusted)
    return client_str, entrusted_str

def get_sub_arr(kaidan_pair:Pair):
    changes = []
    client_str, entrusted_str = kaidan.page_two(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = page_three(kaidan_pair)
    changes.extend([client_str, kaidan_pair.client.sail_id, entrusted_str])
    extract = kaidan_pair.client.extract
    extract_ch = number_to_chinese(extract)
    changes.extend([extract, extract_ch])
    client_str, entrusted_str = kaidan.page_five(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.extend([kaidan_pair.entrusted.name, kaidan_pair.client.name])
    changes.extend([kaidan_pair.client.name, kaidan_pair.entrusted.name])
    client_str, entrusted_str = kaidan.page_six(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    return changes

