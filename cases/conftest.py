"""
测试用例 conftest.py
定义测试用例级别的fixture
"""
import pytest
from pages.login_page import LoginPage
from typing import Any, List, Dict
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Error,
    Page,
)
import allure
import os
from slugify import slugify


def _build_artifact_test_folder(
        pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str
) -> str:
    """构建测试产物存储路径"""
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(output_dir, slugify(request.node.nodeid), folder_or_file_name)


@pytest.fixture(scope="session")
def login_first(context, base_url, pytestconfig) -> None:
    """
    全局登录一次，用于需要登录态的测试用例
    完整流程：输入账号密码 → 点击登录 → 滑块验证 → 等待跳转
    """
    print(f"base_url---- {base_url}")
    page = context.new_page()
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("15901234560", "123123123", handle_slider=True)
    # 等待登录成功跳转
    login_page.is_login_successful(timeout=15000)
    print(f"全局登录完成，当前URL: {page.url}")


@pytest.fixture
def unlogin_page(browser: Browser, browser_context_args: Dict,
                 pytestconfig: Any, request: pytest.FixtureRequest):
    """
    每个用例独立的浏览器上下文和页面（无登录态）
    每次创建全新上下文，用例之间 cookie/storage 完全隔离
    带用例失败截图和视频功能
    """
    # 每个用例创建独立上下文，确保无残留 cookie
    context = browser.new_context(**browser_context_args)
    pages: List[Page] = []
    context.on("page", lambda page: pages.append(page))

    page = context.new_page()
    yield page

    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else True

    # 截图判断
    screenshot_option = pytestconfig.getoption("--screenshot")
    capture_screenshot = screenshot_option == "on" or (
            failed and screenshot_option == "only-on-failure"
    )
    print(f"capture_screenshot:{capture_screenshot}")

    if capture_screenshot:
        for index, p in enumerate(pages):
            human_readable_status = "failed" if failed else "finished"
            screenshot_path = _build_artifact_test_folder(
                pytestconfig, request, f"test-{human_readable_status}-{index + 1}.png"
            )
            print(f'-----------------{screenshot_path}')
            try:
                p.screenshot(timeout=5000, path=screenshot_path)
                # 把截图放入allure报告
                allure.attach.file(screenshot_path,
                                   name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.PNG
                                   )
            except Error:
                pass

    # 用例添加视频
    video_option = pytestconfig.getoption("--video")
    preserve_video = video_option == "on" or (
            failed and video_option == "retain-on-failure"
    )
    if preserve_video:
        for index, p in enumerate(pages):
            video = p.video
            if not video:
                continue
            try:
                video_path = video.path()
                file_name = os.path.basename(video_path)
                file_path = _build_artifact_test_folder(pytestconfig, request, file_name)
                video.save_as(path=file_path)
                # 放入视频
                human_readable_status = "failed" if failed else "finished"
                allure.attach.file(file_path,
                                   name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.WEBM)
            except Error:
                # Silent catch empty videos.
                pass

    # 关闭页面和上下文，彻底清除本次用例的所有状态
    page.close()
    context.close()
