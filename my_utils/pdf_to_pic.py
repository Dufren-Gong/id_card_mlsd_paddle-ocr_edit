from fitz import open as fitzopen
from fitz import Matrix as fitzMatrix
from my_utils.utils import get_data_str
from multiprocessing import Pool, cpu_count
import os

def process_page(args):
    time_str = get_data_str()
    pdf_path, page_number, extist_nums, resolution, output_folder, pic_format, color_mode = args
    # 打开 PDF 文件
    pdf_document = fitzopen(pdf_path)
    page = pdf_document[page_number]

    # 获取页面的原始大小（以点为单位）
    zoom_x = resolution / page.rect.width
    zoom_y = resolution / page.rect.height
    zoom = min(zoom_x, zoom_y)

    # 创建一个矩阵来应用缩放和抗锯齿
    mat = fitzMatrix(zoom, zoom)

    # 将 PDF 页面转换为图片
    pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=color_mode)

    # 定义输出图片的路径
    output_path = os.path.join(output_folder, f"{time_str}_page_{page_number + 1 + extist_nums}.{pic_format}")

    # 保存图片
    pix.save(output_path)

    # 关闭 PDF 文件
    pdf_document.close()

def convert_pdf_to_images(pdf_path, save_path, pic_format, resolution=2048, color_mode='rgb'):
    # 打开 PDF 文件
    extist_nums = len(os.listdir(save_path))
    pdf_document = fitzopen(pdf_path)
    num_pages = len(pdf_document)
    pdf_document.close()

    # 准备参数列表
    args = [(pdf_path, page_number, extist_nums, resolution, save_path, pic_format, color_mode) for page_number in range(num_pages)]

    # 使用多进程来处理每个页面
    with Pool(processes=cpu_count()) as pool:
        pool.map(process_page, args)