from docx import Document
import os, shutil
from my_utils.operate_excel import Pair
from docx.shared import Inches
from PIL import Image

def copy_template(mode, base_path, name_concat, count, sub = None):
    template_name = ['两个内地人模版', '一港一内地模版']
    if sub != None:
        docx_name = name_concat + '_' + mode + '_' + sub + '.docx'
    else:
        docx_name = name_concat + '_' + mode + '.docx'
    name = template_name[int(bool(count))]
    if sub == None:
        kaidan_template_path = f'模版/{mode}/{name}.docx'
    else:
        kaidan_template_path = f'模版/{mode}/{name}/{sub}.docx'
    kaidan_base = os.path.join(base_path, mode, name_concat)
    os.makedirs(kaidan_base, exist_ok=True)
    kaidan_path = os.path.join(kaidan_base, docx_name)
    if os.path.exists(kaidan_path):
        os.remove(kaidan_path)
    shutil.copy(kaidan_template_path, kaidan_path)
    return kaidan_path

def number_to_chinese(s):
    s_duizhao = {
        '0':"零",'1':"壹",'2':"贰",'3':"叁",'4':"肆",
        '5':"伍",'6':"陆",'7':"柒",'8':"捌",'9':"玖"
    }
    #小数点前最大到千亿 可继续增加
    if len(s) == 1:
        return s_duizhao[s] + '元'
    else:
        s_danwei = {
            0:'',1:'拾',2:'佰',3:'仟',4:'万',8:'亿'
        }
        re_re = ""
        if '.' in s :
            s_1 = s[0:s.find('.')]
            s_2 = s[s.find('.')+1:]
            flag_1 = 0
            s_1 = s_1[::-1]

            for i in s_1:
                if flag_1 != 0 and flag_1 % 4 == 0:
                    re_re += s_danwei[flag_1]
                if i != '0':
                    re_re += s_danwei[flag_1 % 4]
                re_re += s_duizhao[i]
                flag_1 += 1
            re_re = re_re[::-1]
            while re_re.endswith('零') and len(re_re)>1:
                re_re = re_re[:-1]
            # 中文数字没有连续的零
            while "零零" in re_re:
                re_re = re_re.replace("零零", "零")
            re_re += '点'
            for i in s_2:
                re_re += s_duizhao[i]
        else:
            s_1 = s
            s_1 = s_1[::-1]
            flag_1 = 0

            for i in s_1:
                if flag_1 != 0 and flag_1 % 4 == 0:
                    re_re += s_danwei[flag_1]
                if i != '0':
                    re_re += s_danwei[flag_1 % 4]
                re_re += s_duizhao[i]
                flag_1 += 1
            re_re = re_re[::-1]
            while re_re.endswith('零') and len(re_re)>1:
                re_re = re_re[:-1]
            # 中文数字没有连续的零
            while "零零" in re_re:
                re_re = re_re.replace("零零", "零")

        if re_re[1] == '十' and re_re[0] == '一':
            re_re = re_re[1:]
    return re_re + '元'

def replace_text_with_same_format(file_path, placeholder, replacements):
    replacement_index = 0
    doc = Document(file_path)

    def replace_in_runs(runs):
        nonlocal replacement_index
        for run in runs:
            while placeholder in run.text and replacement_index < len(replacements):
                # 找到占位符的位置
                pos = run.text.find(placeholder)
                # 分割文本
                before = run.text[:pos]
                after = run.text[pos + len(placeholder):]
                # 替换文本，保持格式
                run.text = before + replacements[replacement_index] + after
                replacement_index += 1

    # 处理文档中的每个段落
    for paragraph in doc.paragraphs:
        replace_in_runs(paragraph.runs)

    # 处理文档中的表格
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_in_runs(paragraph.runs)
    return doc

def get_num_base(path, num=1):
    for i in range(num):
        path = os.path.dirname(path)
    return path

def get_image_paths(pairs:Pair, kaidan_path):
    pics = []
    base_path = get_num_base(kaidan_path, 3)
    client_name = pairs.client.name
    entrusted_name = pairs.entrusted.name
    pics_temp = os.listdir(base_path)
    pics_temp = [i for i in pics_temp if not i.endswith('.info')]
    if '.DS_Store' in pics_temp:
        pics_temp.remove('.DS_Store')
    for k in pics_temp:
        if k.split('.')[0] == client_name:
            pics.append(k)
        elif k.split('.')[0] == entrusted_name:
            pics.append(k)
        if len(pics) == 2:
            break
    pics = [f"{client_name}.png", f"{client_name}反.png", f"{entrusted_name}.png", f"{entrusted_name}反.png"]
    return [os.path.join(base_path, pic) for pic in pics]

def replace_pic(doc, pairs, num, kaidan_path, position, num_spaces, scale = 1.0):
    image_paths = get_image_paths(pairs, kaidan_path)
    image_paths = image_paths[2*position:2*(position + 1)]
    # 计算目标段落的索引
    # 计算目标段落的索引
    # 计算目标段落的索引
    target_index = len(doc.paragraphs) - num
    
    # 确保文档至少有三个段落
    if target_index < 0:
        raise ValueError("文档段落不足三个，无法在倒数第三段插入图片。")
    
    # 在目标段落之后创建一个新段落用于插入图片
    paragraph = doc.paragraphs[target_index]
    new_paragraph = paragraph.insert_paragraph_before()  # 插入在目标段落之前
    
    # 在同一个段落内插入多个图片和空格
    for i, image_path in enumerate(image_paths):
        # 打开图片以获取其原始尺寸
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            # 按比例计算新的宽度和高度
            scaled_width = original_width * scale
            scaled_height = original_height * scale
        
        # 转换尺寸到英寸（像素到英寸的转换因子通常是 96, 可根据实际情况调整）
        width_inches = scaled_width / 96
        height_inches = scaled_height / 96

        run = new_paragraph.add_run()
        # 插入图片，设置宽度和高度以保持比例
        run.add_picture(image_path, width=Inches(width_inches), height=Inches(height_inches))

        # 插入空格（除了最后一个图片之后）
        if i < len(image_paths) - 1:
            space_run = new_paragraph.add_run(' ' * num_spaces)
        
    # 将新段落移动到目标段落的后面
    paragraph._element.addnext(new_paragraph._element)
    return doc