"""
测试用例 conftest.py
定义测试用例级别的fixture
"""
import os
import pytest
from pages.login_page import LoginPage
from typing import Any, List, Dict
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Error,
    Page,
    Playwright,
)
import allure
from slugify import slugify

# 登录态存储文件路径
AUTH_STATE_FILE = os.path.join(os.path.dirname(__file__), ".auth_state.json")


def _build_artifact_test_folder(
        pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str
) -> str:
    """构建测试产物存储路径"""
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(output_dir, slugify(request.node.nodeid), folder_or_file_name)


@pytest.fixture(scope="session")
def auth_state(browser: Browser, browser_context_args: Dict, base_url: str) -> str:
    """
    全局只登录一次，将登录态（cookies + localStorage）保存到文件。
    后续所有用例通过加载该文件恢复登录态，无需重新登录。
    """
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    login_page = LoginPage(page)
    login_page.navigate(base_url.rstrip("/") + "/login")
    login_page.login("15901234562", "123123123")
    assert login_page.is_login_successful(timeout=15000), "全局登录失败，请检查账号密码或网络"
    print(f"全局登录完成，当前URL: {page.url}")
    # 保存登录态到文件
    context.storage_state(path=AUTH_STATE_FILE)
    page.close()
    context.close()
    return AUTH_STATE_FILE


@pytest.fixture
def logged_page(auth_state: str, browser: Browser, browser_context_args: Dict,
               pytestconfig: Any, request: pytest.FixtureRequest):
    """
    每个用例独立的浏览器上下文，复用已保存的登录态（无需重新登录）。
    带用例失败截图和视频功能。
    """
    context = browser.new_context(
        **browser_context_args,
        storage_state=auth_state,
    )
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
                human_readable_status = "failed" if failed else "finished"
                allure.attach.file(file_path,
                                   name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.WEBM)
            except Error:
                pass

    page.close()
    context.close()


@pytest.fixture
def unlogin_page(browser: Browser, browser_context_args: Dict,
               pytestconfig: Any, request: pytest.FixtureRequest):
    """
    未登录状态的独立浏览器上下文，用于登录功能测试。
    不加载任何登录态。
    """
    context = browser.new_context(**browser_context_args)
    pages: List[Page] = []
    context.on("page", lambda page: pages.append(page))

    page = context.new_page()
    yield page

    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else True

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
                allure.attach.file(screenshot_path,
                                   name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.PNG
                                   )
            except Error:
                pass

    page.close()
    context.close()


