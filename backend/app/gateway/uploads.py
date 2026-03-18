"""Uploads — 处理上传文件的保存与校验。"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# 文件大小限制：10 MB
_MAX_FILE_SIZE = 10 * 1024 * 1024

# 支持的文件类型
_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".md", ".txt"}

# 合法的 thread_id 格式（UUID + 字母数字 + 短横线）
_SAFE_THREAD_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


async def save_upload(file: "UploadFile", thread_id: str) -> str:  # type: ignore[name-defined]
    """保存上传的文件到指定路径。

    Args:
        file: FastAPI UploadFile 对象
        thread_id: 当前对话线程 ID（仅允许字母数字和 -_）

    Returns:
        保存后的文件绝对路径

    Raises:
        ValueError: 文件类型不支持、超过大小限制或 thread_id 格式不合法
    """
    # 校验 thread_id，防止路径穿越
    if not _SAFE_THREAD_ID_RE.match(thread_id):
        raise ValueError(f"thread_id 格式不合法: {thread_id!r}")

    filename = file.filename or "upload"
    # 仅保留文件名，移除可能的路径前缀
    filename = os.path.basename(filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}，仅支持 {', '.join(sorted(_ALLOWED_EXTENSIONS))}")

    dest_dir = Path(f".jobflow/uploads/{thread_id}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename

    content = await file.read()
    if len(content) > _MAX_FILE_SIZE:
        raise ValueError(f"文件过大: {len(content)} 字节，最大允许 {_MAX_FILE_SIZE} 字节（10 MB）")

    dest_path.write_bytes(content)
    logger.info("save_upload: 文件已保存至 %s", dest_path)
    return str(dest_path.resolve())
