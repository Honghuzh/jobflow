"""模型工厂 — 从配置创建 LangChain ChatModel 实例。"""
from __future__ import annotations

import importlib
import logging
import os
import re
import os
from dotenv import load_dotenv

# 强行指定加载 .env 文件
# 我们假设 .env 在 backend 目录下
load_dotenv(os.path.join(os.getcwd(), ".env"))

logger = logging.getLogger(__name__)

# 配置中环境变量引用的正则（如 $OPENAI_API_KEY）
_ENV_VAR_PATTERN = re.compile(r"^\$([A-Z_][A-Z0-9_]*)$")


def create_chat_model(name: str, thinking_enabled: bool = False, **kwargs):
    """从 config.yaml 中的模型配置创建 LangChain ChatModel 实例。

    Args:
        name: 模型名称（对应 config.yaml 中 models[].name）
        thinking_enabled: 是否启用 thinking/reasoning 模式
        **kwargs: 覆盖配置中的参数

    Returns:
        LangChain BaseChatModel 实例

    Raises:
        ValueError: 模型配置未找到
        ImportError: 模型类不可导入
    """
    from jobflow.config.app_config import get_app_config

    config = get_app_config()
    models_config = config.get("models", [])

    # 查找目标模型配置
    model_cfg = next((m for m in models_config if m.get("name") == name), None)
    if model_cfg is None:
        # 如果没有配置，使用第一个模型
        if models_config:
            model_cfg = models_config[0]
            logger.warning("create_chat_model: 未找到模型 '%s'，使用默认模型 '%s'", name, model_cfg.get("name"))
        else:
            raise ValueError(f"未找到模型配置 '{name}'，请检查 config.yaml")

    # 解析 use 字段，格式：module:class
    use = model_cfg.get("use", "langchain_openai:ChatOpenAI")
    module_path, class_name = use.rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
        model_class = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        raise ImportError(f"无法加载模型类 '{use}': {exc}") from exc

    # 构建初始化参数，解析环境变量
    init_kwargs: dict = {}
    for key, value in model_cfg.items():
        if key in ("name", "display_name", "use"):
            continue
        init_kwargs[key] = _resolve_env_var(value)

    # kwargs 覆盖
    init_kwargs.update(kwargs)

    logger.info("create_chat_model: 创建 %s（%s）", name, class_name)
    return model_class(**init_kwargs)


def _resolve_env_var(value):
    """解析配置值中的环境变量引用（如 $OPENAI_API_KEY）。"""
    if isinstance(value, str):
        match = _ENV_VAR_PATTERN.match(value)
        if match:
            env_name = match.group(1)
            env_value = os.environ.get(env_name)
            if env_value is None:
                logger.warning("环境变量 %s 未设置", env_name)
            return env_value
    return value
