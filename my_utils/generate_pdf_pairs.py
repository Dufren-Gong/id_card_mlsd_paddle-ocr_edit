import re
from pathlib import Path
from typing import List, Union
from PIL import Image

# ===== 先做 hashlib 兼容补丁，再导入 reportlab =====
import hashlib

_original_md5 = hashlib.md5

def _safe_md5(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _original_md5(*args, **kwargs)

hashlib.md5 = _safe_md5

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def natural_sort_key(s: str):
    """
    自然排序，例如 img2.jpg 会排在 img10.jpg 前面
    """
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', s)
    ]


def get_image_files(folder_path: Union[str, List[str]]) -> List[Path]:
    """
    获取图片文件并按自然排序返回

    参数：
        folder_path:
            1. str: 文件夹路径，读取该文件夹下所有图片
            2. List[str]: 路径字符串列表，判断每个路径是否为存在的图片文件

    返回：
        满足条件的 Path 列表
    """
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

    if isinstance(folder_path, str):
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return []

        files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in exts
        ]

    elif isinstance(folder_path, list):
        files = [
            Path(p) for p in folder_path
            if isinstance(p, str)
            and Path(p).is_file()
            and Path(p).suffix.lower() in exts
        ]
    else:
        return []

    files.sort(key=lambda x: natural_sort_key(x.name))
    return files


def images_to_paired_pdfs(folder_path: Union[str, List[str]],
                          save_path: str,
                          image_gap: float,
                          width_ratio: float,
                          reserve: bool):
    """
    将图片按每两张一组生成 PDF

    参数：
        folder_path:
            1. str: 文件夹路径
            2. List[str]: 图片路径列表
        save_path: 输出文件夹
        image_gap: 上下两张图片的间隔（point）
        width_ratio: 图片宽度占 PDF 宽度比例
        reserve: 是否上下顺序对调
    """
    if not (0 < width_ratio <= 1):
        return "照片占pdf宽度必须在 (0, 1] 之间"

    image_files = get_image_files(folder_path)

    if len(image_files) == 0:
        return "没有找到图片文件"

    if len(image_files) % 2 != 0:
        return "图片数量不是偶数，无法两两配对"

    output_dir = Path(save_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_width, pdf_height = A4
    target_width = pdf_width * width_ratio

    for i in range(0, len(image_files), 2):
        front_img_path = image_files[i]
        back_img_path = image_files[i + 1]

        with Image.open(front_img_path) as img1:
            w1, h1 = img1.size

        with Image.open(back_img_path) as img2:
            w2, h2 = img2.size

        display_h1 = target_width * h1 / w1
        display_h2 = target_width * h2 / w2

        total_height = display_h1 + image_gap + display_h2
        start_y = (pdf_height + total_height) / 2

        x1 = (pdf_width - target_width) / 2
        y1 = start_y - display_h1

        x2 = (pdf_width - target_width) / 2
        y2 = y1 - image_gap - display_h2

        pdf_name = f"{i // 2 + 1:04d}.pdf"
        pdf_path = output_dir / pdf_name

        c = canvas.Canvas(str(pdf_path), pagesize=A4)

        if reserve:
            c.drawImage(
                str(back_img_path),
                x1, y1,
                width=target_width,
                height=display_h1,
                preserveAspectRatio=True,
                mask='auto'
            )
            c.drawImage(
                str(front_img_path),
                x2, y2,
                width=target_width,
                height=display_h2,
                preserveAspectRatio=True,
                mask='auto'
            )
        else:
            c.drawImage(
                str(front_img_path),
                x1, y1,
                width=target_width,
                height=display_h1,
                preserveAspectRatio=True,
                mask='auto'
            )
            c.drawImage(
                str(back_img_path),
                x2, y2,
                width=target_width,
                height=display_h2,
                preserveAspectRatio=True,
                mask='auto'
            )

        c.save()

    return f"处理完成，共生成 {len(image_files) // 2} 个PDF到最新处理结果中。"