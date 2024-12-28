from my_utils.operate_excel import Pair
import each_types.kaidan as kaidan

def get_sub_arr_buka(kaidan_pair:Pair):
    changes = []
    client_str, entrusted_str = kaidan.page_two(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    client_str, entrusted_str = kaidan.page_three(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.append(kaidan_pair.client.sail_card_id)
    changes.append(kaidan_pair.client.sail_id)
    changes.append(kaidan_pair.entrusted.sail_card_id)
    client_str, entrusted_str = kaidan.page_five(kaidan_pair)
    changes.extend([client_str, entrusted_str])
    changes.extend([kaidan_pair.entrusted.name, kaidan_pair.client.name])
    return changes