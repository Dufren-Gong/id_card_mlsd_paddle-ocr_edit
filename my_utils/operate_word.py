from docx import Document
import os, shutil
from my_utils.operate_excel import Pair
from docx.shared import Inches
from PIL import Image
from pathlib import Path

#提取照片
def extract_images_from_docx(docx_path, output_folder):
    # 创建输出文件夹，如果不存在的话
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开docx文件
    doc = Document(docx_path)

    # 初始化图片计数器
    image_count = 0

    # 遍历文档中的所有段落和图形
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_count += 1
            # 获取图片数据
            image = rel.target_part.blob
            # 获取图片格式
            extension = rel.target_part.content_type.split('/')[-1]
            # 保存图片
            image_filename = os.path.join(output_folder, f'image_{image_count}.{extension}')
            with open(image_filename, 'wb') as img_file:
                img_file.write(image)

    # print(f'提取完成，共提取了 {image_count} 张图片。')

def copy_template(mode, base_path, name_concat, count, sub = None, in_floader=False, template_sub_path = []):
    template_name = ['两个内地人模版', '一港一内地模版']
    if sub != None:
        docx_name = name_concat + '_' + mode + '_' + sub + '.docx'
    else:
        docx_name = name_concat + '_' + mode + '.docx'
    name = template_name[int(bool(count))]
    if sub == None:
        kaidan_template_path = Path(f'模版/{mode}/{name}.docx')
    else:
        kaidan_template_path = Path(f'模版/{mode}/{name}/{sub}.docx')
    if len(template_sub_path) != 0:
        kaidan_template_path = kaidan_template_path.parent / Path(*template_sub_path) / kaidan_template_path.name
    if in_floader:
        kaidan_base = os.path.join(base_path, mode, name_concat)
    else:
        kaidan_base = os.path.join(base_path, mode)
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

def count_placeholder_occurrences(file_path, placeholder):
    count = 0
    doc = Document(file_path)

    def count_in_runs(runs):
        nonlocal count
        for run in runs:
            # run.text 中可能出现多次 placeholder，使用 str.count 统计
            count += run.text.count(placeholder)

    # 统计段落中的占位符
    for paragraph in doc.paragraphs:
        count_in_runs(paragraph.runs)

    # 统计表格中的占位符
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    count_in_runs(paragraph.runs)

    return count

def replace_text_with_same_format(file_path, placeholder, replacements):
    replacement_index = 0
    all_count = 0
    doc = Document(file_path)

    def replace_in_runs(runs):
        nonlocal all_count
        nonlocal replacement_index
        if not isinstance(replacements, str):
            for run in runs:
                while placeholder in run.text and replacement_index < len(replacements):
                    all_count += 1
                    # 找到占位符的位置
                    pos = run.text.find(placeholder)
                    # 分割文本
                    before = run.text[:pos]
                    after = run.text[pos + len(placeholder):]
                    # 替换文本，保持格式
                    run.text = before + replacements[replacement_index] + after
                    replacement_index += 1
        else:
            for run in runs:
                while placeholder in run.text:
                    all_count += 1
                    # 找到占位符的位置
                    pos = run.text.find(placeholder)
                    # 分割文本
                    before = run.text[:pos]
                    after = run.text[pos + len(placeholder):]
                    # 替换文本，保持格式
                    run.text = before + replacements + after

    # 处理文档中的每个段落
    for paragraph in doc.paragraphs:
        replace_in_runs(paragraph.runs)

    # 处理文档中的表格
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_in_runs(paragraph.runs)
    return doc, all_count

def get_num_base(path, num=1):
    for i in range(num):
        path = os.path.dirname(path)
    return path

def get_image_paths(pairs:Pair, kaidan_path, in_folder_flag):
    pics = []
    base_path = get_num_base(kaidan_path, 2 + int(in_folder_flag))
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

def replace_pic(doc, pairs, num, kaidan_path, position, num_spaces, scale = 1.0, in_folder_flag = True):
    image_paths = get_image_paths(pairs, kaidan_path, in_folder_flag)
    image_paths = image_paths[2*position:2*(position + 1)]
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