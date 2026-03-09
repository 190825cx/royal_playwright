"""
项目全局 conftest.py
配置pytest插件和全局fixture
"""
from pytest import Item
import allure
import pytest
from typing import Dict

# 本地插件注册
pytest_plugins = [
    'plugins.pytest_playwright',
    'plugins.pytest_base_url_plugin'
]


def pytest_runtest_call(item: Item):
    """动态添加 allure 报告信息"""
    # 动态添加测试类的 allure.feature()
    if item.parent._obj.__doc__:
        allure.dynamic.feature(item.parent._obj.__doc__)
    # 动态添加测试用例的title 标题 allure.title()
    if item.function.__doc__:
        allure.dynamic.title(item.function.__doc__)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args) -> Dict:
    """浏览器启动参数 - 窗口最大化"""
    return {
        "args": ['--start-maximized'],
        **browser_type_launch_args,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright, pytestconfig) -> Dict:
    """浏览器上下文参数"""
    return {
        "no_viewport": True,  # 窗口最大化
        "ignore_https_errors": True,  # 忽略https报错
        **browser_context_args,
    }
