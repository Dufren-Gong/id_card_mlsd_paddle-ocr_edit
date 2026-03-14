import re, tempfile, os
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
                          reserve: bool,
                          black_flag: bool,
                          result_mode: int):
    """
    将图片按每两张一组生成 PDF 或 图片

    参数：
        folder_path:
            1. str: 文件夹路径
            2. List[str]: 图片路径列表
        save_path: 输出文件夹
        image_gap: 上下两张图片的间隔（point）
        width_ratio: 图片宽度占 A4 页面宽度比例
        reserve: 是否上下顺序对调
        black_flag: 是否转为黑白照片
        result_mode:
            0 -> 生成 PDF
            1 -> 生成图片（A4白底排版图）
    """
    if not (0 < width_ratio <= 1):
        return "照片占宽度比例必须在 (0, 1] 之间"

    if result_mode not in (0, 1):
        return "result_mode 参数错误，0 表示生成PDF，1 表示生成图片"

    image_files = get_image_files(folder_path)

    if len(image_files) == 0:
        return "没有找到图片文件"

    if len(image_files) % 2 != 0:
        return "图片数量不是偶数，无法两两配对"

    output_dir = Path(save_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # PDF坐标系下的A4尺寸（单位：point）
    pdf_width, pdf_height = A4
    target_width = pdf_width * width_ratio

    # 图片输出时，按 A4 @300DPI 生成
    dpi = 300
    scale = dpi / 72.0
    img_page_width = int(round(pdf_width * scale))
    img_page_height = int(round(pdf_height * scale))

    def load_image(img_path):
        """加载图片，并根据 black_flag 决定是否转黑白"""
        img = Image.open(img_path)
        if black_flag:
            img = img.convert("L")
        else:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
        return img

    def resize_keep_ratio(pil_img, target_w_px):
        """按目标宽度缩放，保持比例"""
        w, h = pil_img.size
        target_h_px = int(round(target_w_px * h / w))
        return pil_img.resize((target_w_px, target_h_px), Image.Resampling.LANCZOS)

    try:
        for i in range(0, len(image_files), 2):
            front_img_path = image_files[i]
            back_img_path = image_files[i + 1]

            img1 = load_image(front_img_path)
            img2 = load_image(back_img_path)

            # 计算原始显示高度（基于PDF point）
            w1, h1 = img1.size
            w2, h2 = img2.size

            display_h1 = target_width * h1 / w1
            display_h2 = target_width * h2 / w2

            total_height = display_h1 + image_gap + display_h2
            start_y = (pdf_height + total_height) / 2

            x1 = (pdf_width - target_width) / 2
            y1 = start_y - display_h1

            x2 = (pdf_width - target_width) / 2
            y2 = y1 - image_gap - display_h2

            base_name = f"{i // 2 + 1:04d}"

            if result_mode == 0:
                # -------- 生成 PDF --------
                pdf_path = output_dir / f"{base_name}.pdf"
                c = canvas.Canvas(str(pdf_path), pagesize=A4)

                if reserve:
                    top_path = str(back_img_path)
                    bottom_path = str(front_img_path)
                    top_h = display_h1
                    bottom_h = display_h2
                else:
                    top_path = str(front_img_path)
                    bottom_path = str(back_img_path)
                    top_h = display_h1
                    bottom_h = display_h2

                # 如果 black_flag=True，PDF模式下仍然建议走临时文件，
                # 因为 reportlab.drawImage 更适合传文件路径
                if black_flag:
                    import tempfile

                    temp_paths = []
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp1, \
                             tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp2:

                            if reserve:
                                img2.save(tmp1.name)
                                img1.save(tmp2.name)
                            else:
                                img1.save(tmp1.name)
                                img2.save(tmp2.name)

                            temp_paths.extend([tmp1.name, tmp2.name])

                            c.drawImage(
                                tmp1.name,
                                x1, y1,
                                width=target_width,
                                height=top_h,
                                preserveAspectRatio=True,
                                mask='auto'
                            )
                            c.drawImage(
                                tmp2.name,
                                x2, y2,
                                width=target_width,
                                height=bottom_h,
                                preserveAspectRatio=True,
                                mask='auto'
                            )
                    finally:
                        for p in temp_paths:
                            try:
                                os.remove(p)
                            except Exception:
                                pass
                else:
                    c.drawImage(
                        top_path,
                        x1, y1,
                        width=target_width,
                        height=display_h1,
                        preserveAspectRatio=True,
                        mask='auto'
                    )
                    c.drawImage(
                        bottom_path,
                        x2, y2,
                        width=target_width,
                        height=display_h2,
                        preserveAspectRatio=True,
                        mask='auto'
                    )

                c.save()

            else:
                # -------- 生成图片 --------
                target_width_px = int(round(target_width * scale))
                image_gap_px = int(round(image_gap * scale))

                # 排序
                if reserve:
                    top_img = img2
                    bottom_img = img1
                else:
                    top_img = img1
                    bottom_img = img2

                top_img = resize_keep_ratio(top_img, target_width_px)
                bottom_img = resize_keep_ratio(bottom_img, target_width_px)

                top_w, top_h_px = top_img.size
                bottom_w, bottom_h_px = bottom_img.size

                total_height_px = top_h_px + image_gap_px + bottom_h_px

                # 注意：PIL 原点在左上角，所以直接先算顶部起点
                top_start_y_px = (img_page_height - total_height_px) // 2

                x1_px = (img_page_width - target_width_px) // 2
                y1_px = top_start_y_px

                x2_px = (img_page_width - target_width_px) // 2
                y2_px = y1_px + top_h_px + image_gap_px

                # 白底A4画布
                canvas_mode = "L" if black_flag else "RGB"
                bg_color = 255 if black_flag else (255, 255, 255)
                page_img = Image.new(canvas_mode, (img_page_width, img_page_height), bg_color)

                page_img.paste(top_img, (x1_px, y1_px))
                page_img.paste(bottom_img, (x2_px, y2_px))

                # 保存图片
                out_path = output_dir / f"{base_name}.jpg"
                if page_img.mode == "RGBA":
                    page_img = page_img.convert("RGB")
                page_img.save(out_path, quality=95)

    except Exception as e:
        return f"处理失败：{str(e)}"

    if result_mode == 0:
        return f"处理完成，共生成 {len(image_files) // 2} 个PDF到最新处理结果中。"
    else:
        return f"处理完成，共生成 {len(image_files) // 2} 张排版图片到最新处理结果中。"