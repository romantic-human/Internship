"""图片处理工具：压缩、格式转换、base64 编码"""
import base64
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 支持的图片格式
SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "bmp", "webp", "gif"}

# 最大尺寸（像素）
MAX_SIZE = 2048


def process_image_to_base64(file_bytes: bytes, max_size: int = MAX_SIZE) -> Optional[str]:
    """
    处理图片：压缩 → 转为 base64 字符串

    Args:
        file_bytes: 图片文件的字节内容
        max_size: 最大边长（像素），超过会等比缩放

    Returns:
        base64 编码字符串，失败返回 None
    """
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(file_bytes))

        # 转为 RGB（去掉 alpha 通道，兼容 JPEG）
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # 等比缩放
        w, h = img.size
        if max(w, h) > max_size:
            ratio = max_size / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            logger.info(f"图片已缩放: {w}x{h} -> {new_w}x{new_h}")

        # 转为 JPEG 并压缩
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        file_bytes = buffer.getvalue()

        # base64 编码
        return base64.b64encode(file_bytes).decode("utf-8")

    except ImportError:
        logger.error("Pillow 未安装，请执行: pip install Pillow")
        return None
    except Exception as e:
        logger.exception(f"图片处理失败: {e}")
        return None


def validate_image(file_name: str, file_size: int, max_size_mb: int = 10) -> tuple[bool, str]:
    """
    校验图片文件

    Args:
        file_name: 文件名
        file_size: 文件大小（字节）
        max_size_mb: 最大文件大小（MB）

    Returns:
        (is_valid, error_message)
    """
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if ext not in SUPPORTED_FORMATS:
        return False, f"不支持的图片格式，仅支持: {', '.join(SUPPORTED_FORMATS)}"

    max_bytes = max_size_mb * 1024 * 1024
    if file_size > max_bytes:
        return False, f"图片大小超过限制 ({max_size_mb}MB)"

    return True, ""
