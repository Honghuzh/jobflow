"""沙箱抽象 — 文档生成沙箱的统一接口。"""
from __future__ import annotations

import logging
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class Sandbox(ABC):
    """沙箱抽象基类，定义统一的文件操作和命令执行接口。"""

    @abstractmethod
    def execute_command(self, command: str) -> tuple[int, str, str]:
        """执行命令。

        Args:
            command: Shell 命令字符串

        Returns:
            (return_code, stdout, stderr) 三元组
        """

    @abstractmethod
    def read_file(self, path: str) -> str:
        """读取文件内容。

        Args:
            path: 文件路径

        Returns:
            文件文本内容
        """

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """写入文件内容。

        Args:
            path: 文件路径
            content: 文件内容
        """

    @abstractmethod
    def list_dir(self, path: str) -> list[str]:
        """列出目录内容。

        Args:
            path: 目录路径

        Returns:
            文件/目录名列表
        """


class LocalSandbox(Sandbox):
    """本地文件系统沙箱实现。

    在指定的根目录下进行文件操作，防止路径逃逸。
    """

    def __init__(self, root: str = "."):
        self._root = Path(root).resolve()

    def _resolve_path(self, path: str) -> Path:
        """解析路径，确保不逃逸沙箱根目录。"""
        resolved = (self._root / path).resolve()
        if not str(resolved).startswith(str(self._root)):
            raise PermissionError(f"路径 '{path}' 超出沙箱范围")
        return resolved

    def execute_command(self, command: str) -> tuple[int, str, str]:
        """在沙箱根目录下执行 Shell 命令。"""
        logger.info("LocalSandbox.execute_command: %s", command)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=str(self._root), timeout=60)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "命令执行超时（60s）"
        except Exception as exc:
            return -1, "", str(exc)

    def read_file(self, path: str) -> str:
        """读取沙箱内的文件。"""
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在：{path}")
        return full_path.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> None:
        """写入沙箱内的文件（自动创建父目录）。"""
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        logger.info("LocalSandbox.write_file: %s（%d 字节）", path, len(content))

    def list_dir(self, path: str = ".") -> list[str]:
        """列出沙箱内的目录。"""
        full_path = self._resolve_path(path)
        if not full_path.exists():
            return []
        return sorted(p.name for p in full_path.iterdir())
