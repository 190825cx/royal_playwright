"""
数据驱动工具模块
支持从 YAML / JSON 文件加载测试数据，配合 pytest.mark.parametrize 使用
"""
import os
import json
from typing import List, Tuple, Any

import yaml


# 数据文件根目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _resolve_path(file_name: str) -> str:
    """将文件名解析为 data/ 目录下的绝对路径"""
    path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"测试数据文件不存在: {path}")
    return path


def load_yaml(file_name: str) -> dict:
    """
    加载 YAML 文件并返回完整字典

    :param file_name: data/ 目录下的 YAML 文件名，如 'login_data.yaml'
    :return: 解析后的字典
    """
    path = _resolve_path(file_name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(file_name: str) -> dict:
    """
    加载 JSON 文件并返回完整字典

    :param file_name: data/ 目录下的 JSON 文件名
    :return: 解析后的字典
    """
    path = _resolve_path(file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_test_data(file_name: str, key: str) -> List[dict]:
    """
    从数据文件中获取指定 key 的测试数据列表

    :param file_name: 数据文件名 (支持 .yaml / .yml / .json)
    :param key: 数据文件中的顶层 key
    :return: 测试数据字典列表
    """
    ext = os.path.splitext(file_name)[1].lower()
    if ext in (".yaml", ".yml"):
        data = load_yaml(file_name)
    elif ext == ".json":
        data = load_json(file_name)
    else:
        raise ValueError(f"不支持的数据文件格式: {ext}，仅支持 .yaml / .yml / .json")

    if key not in data:
        raise KeyError(f"数据文件 '{file_name}' 中未找到 key: '{key}'，可用 key: {list(data.keys())}")

    return data[key]


def parametrize_data(
    file_name: str,
    key: str,
    fields: Tuple[str, ...] = None,
) -> List[tuple]:
    """
    获取测试数据并转换为 pytest.mark.parametrize 所需的元组列表

    用法示例::

        @pytest.mark.parametrize(
            "phone, password, description",
            parametrize_data("login_data.yaml", "login_empty_validation",
                             fields=("phone", "password", "description"))
        )
        def test_xxx(self, phone, password, description):
            ...

    :param file_name: 数据文件名
    :param key: 数据文件中的顶层 key
    :param fields: 要提取的字段元组，如 ("phone", "password", "description")
                   若为 None，则返回完整字典列表
    :return: 元组列表，每个元组对应一条测试数据
    """
    data_list = get_test_data(file_name, key)

    if fields is None:
        return data_list

    result = []
    for item in data_list:
        row = tuple(item.get(field, "") for field in fields)
        result.append(row)
    return result


def parametrize_with_ids(
    file_name: str,
    key: str,
    fields: Tuple[str, ...],
    id_field: str = "case_id",
) -> Tuple[List[tuple], List[str]]:
    """
    获取测试数据，同时生成 pytest parametrize 的 ids

    用法示例::

        data, ids = parametrize_with_ids(
            "login_data.yaml", "login_empty_validation",
            fields=("phone", "password", "description"),
            id_field="case_id"
        )

        @pytest.mark.parametrize("phone, password, description", data, ids=ids)
        def test_xxx(self, phone, password, description):
            ...

    :param file_name: 数据文件名
    :param key: 数据文件中的顶层 key
    :param fields: 要提取的字段元组
    :param id_field: 用作 test id 的字段名，默认 "case_id"
    :return: (数据元组列表, id列表)
    """
    data_list = get_test_data(file_name, key)

    result = []
    ids = []
    for item in data_list:
        row = tuple(item.get(field, "") for field in fields)
        result.append(row)
        ids.append(item.get(id_field, ""))
    return result, ids
