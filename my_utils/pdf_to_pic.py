import os
import fitz
from my_utils.utils import get_data_str

def convert_pdf_to_images(pdf_paths, save_path, pic_format, resolution=2048, color_mode='rgb'):
    """
    单进程稳定版 PDF 转图片

    参数：
        pdf_paths: str 或 list[str]
            单个 PDF 路径，或 PDF 路径列表
        save_path: str
            图片输出目录
        pic_format: str
            输出图片格式，例如 'png'、'jpg'
        resolution: int
            输出图片的目标边长基准，默认 1600，更均衡
        color_mode: str
            fitz 的 colorspace，常用 'rgb'、'gray'
    """
    if isinstance(pdf_paths, str):
        pdf_path_arr = [pdf_paths]
    else:
        pdf_path_arr = list(pdf_paths)

    if not pdf_path_arr:
        return "未提供 PDF 路径"

    os.makedirs(save_path, exist_ok=True)

    # 只调用一次，避免每页重复生成时间戳
    time_str = get_data_str()

    for pdf_id, pdf_path in enumerate(pdf_path_arr):
        if not os.path.isfile(pdf_path):
            continue

        pdf_document = fitz.open(pdf_path)
        try:
            num_pages = len(pdf_document)

            for page_number in range(num_pages):
                page = pdf_document[page_number]

                # 以页面宽高为基准，按较短缩放比例控制输出尺寸
                zoom_x = resolution / page.rect.width
                zoom_y = resolution / page.rect.height
                zoom = min(zoom_x, zoom_y)

                # 防止极端情况下缩放过小或过大
                zoom = max(0.5, min(zoom, 4.0))

                mat = fitz.Matrix(zoom, zoom)

                pix = page.get_pixmap(
                    matrix=mat,
                    alpha=False,
                    colorspace=color_mode
                )

                output_path = os.path.join(
                    save_path,
                    f"{pdf_id}_page_{page_number + 1}_{time_str}.{pic_format}"
                )

                pix.save(output_path)
        finally:
            pdf_document.close()

    return ""