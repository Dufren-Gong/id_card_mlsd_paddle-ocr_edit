#pip install -U opencc-python-reimplemented
import opencc

def fan_to_jian(text):
    if isinstance(text, str):
        converter = opencc.OpenCC('t2s')  # 使用内置的简易配置
        simplified_text = converter.convert(text)
        return simplified_text
    else:
        return text