"""
基础页面对象 (BasePage)
所有 Page Object 的基类，封装通用操作，如等待、点击、输入等，提高复用性
"""
import time
from playwright.sync_api import Page, Locator
from typing import Optional


class BasePage:
    """所有页面对象的基类"""

    def __init__(self, page: Page):
        self.page = page

    def wait_and_click(self, locator: Locator, timeout: int = 5000, force: bool = False) -> None:
        """
        等待元素可见并点击
        :param locator: Playwright Locator 对象
        :param timeout: 等待超时时间（毫秒）
        :param force: 是否强制点击（忽略可见性掩盖等交互拦截）
        """
        locator.first.wait_for(state="visible", timeout=timeout)
        locator.first.click(force=force)

    def wait_and_fill(self, locator: Locator, text: str, timeout: int = 5000, clear: bool = True) -> None:
        """
        等待元素可见并输入文本
        :param locator: Playwright Locator 对象
        :param text: 要输入的文本
        :param timeout: 等待超时时间（毫秒）
        :param clear: 是否在输入前清空
        """
        locator.first.wait_for(state="visible", timeout=timeout)
        if clear:
            locator.first.clear()
        locator.first.fill(text)

    def get_text(self, locator: Locator, timeout: int = 3000) -> str:
        """
        安全地获取元素文本内容，带超时等待
        :return: 元素的文本（去除收尾空格），异常则返回空边框
        """
        try:
            locator.first.wait_for(state="visible", timeout=timeout)
            text = locator.first.text_content() or ""
            return text.strip()
        except Exception:
            return ""

    def wait_for_spinner_hidden(self, timeout: int = 10000) -> None:
        """
        等待页面加载遮罩（常见于 iView/Element Plus）消失
        """
        try:
            spinner = self.page.locator(".ivu-spin-fix:visible, .ivu-spin-show-text:visible, .el-loading-mask:visible")
            if spinner.count() > 0:
                spinner.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

    def close_current_modal(self) -> None:
        """
        尝试关闭当前可见的弹窗
        """
        try:
            # 方式1: 点击确定/返回/取消按钮
            close_btns = self.page.locator(
                '.ivu-modal-close, .el-dialog__headerbtn, .ivu-btn:has-text("取消"), .ivu-btn:has-text("返回"), .ivu-btn:has-text("关闭")'
            ).filter(visible=True).first
            
            if close_btns.count() > 0:
                close_btns.click(force=True)
                time.sleep(1)
                return
            
            # 方式2: 按 Esc 键
            self.page.keyboard.press("Escape")
            time.sleep(1)
        except Exception:
            pass
