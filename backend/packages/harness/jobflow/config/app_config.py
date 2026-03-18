"""应用配置系统 — 从 config.yaml 加载配置，支持环境变量解析。"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_SEARCH_PATHS = ["config.yaml", "../config.yaml", "../../config.yaml"]
_ENV_VAR_PATTERN = re.compile(r"\$([A-Z_][A-Z0-9_]*)")

_cached_config: dict | None = None


class AppConfig:
    """应用配置类，提供类型安全的配置访问。"""

    def __init__(self, data: dict):
        self._data = data

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值。"""
        return self._data.get(key, default)

    def get_model_config(self, name: str | None = None) -> dict | None:
        """获取指定模型的配置，name 为 None 时返回第一个。"""
        models = self._data.get("models", [])
        if not models:
            return None
        if name is None:
            return models[0]
        return next((m for m in models if m.get("name") == name), None)

    def get_memory_config(self) -> dict:
        """获取记忆系统配置。"""
        return self._data.get("memory", {"enabled": False})

    def get_subagent_config(self) -> dict:
        """获取 Sub-Agent 配置。"""
        return self._data.get("subagents", {"enabled": True, "max_concurrent": 3, "timeout_seconds": 900})

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data


def get_app_config(config_path: str | None = None) -> dict:
    """加载并缓存应用配置。

    Args:
        config_path: 配置文件路径，为 None 时自动搜索

    Returns:
        配置字典（环境变量已解析）
    """
    global _cached_config
    if _cached_config is not None and config_path is None:
        return _cached_config

    try:
        import yaml
    except ImportError:
        logger.warning("get_app_config: pyyaml 未安装，返回空配置")
        return {}

    # 搜索配置文件
    search_paths = [config_path] if config_path else _CONFIG_SEARCH_PATHS
    cfg_file: Path | None = None

    for path_str in search_paths:
        path = Path(path_str)
        if path.exists():
            cfg_file = path
            break

    if cfg_file is None:
        logger.warning("get_app_config: 未找到 config.yaml，使用空配置。请复制 config.example.yaml 为 config.yaml")
        return {}

    try:
        with open(cfg_file, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        config = _resolve_env_vars(raw)
        logger.info("get_app_config: 从 %s 加载配置", cfg_file)
        if config_path is None:
            _cached_config = config
        return config
    except Exception as exc:
        logger.error("get_app_config: 加载失败 — %s", exc)
        return {}


def _resolve_env_vars(obj: Any) -> Any:
    """递归解析配置中的 $ENV_VAR 引用。"""
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # 完整匹配（整个字符串是一个 $VAR）
        full_match = re.match(r"^\$([A-Z_][A-Z0-9_]*)$", obj)
        if full_match:
            return os.environ.get(full_match.group(1))
        # 部分替换（字符串中内嵌 $VAR）
        def replace(m: re.Match) -> str:
            return os.environ.get(m.group(1), m.group(0))

        return _ENV_VAR_PATTERN.sub(replace, obj)
    return obj
