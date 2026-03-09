"""
登录页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/
登录流程: 输入账号密码 → 点击登录 → 滑块验证 → (可能出现"继续登录"确认弹窗) → 跳转到后台首页
"""
import random
from playwright.sync_api import Page, expect, ElementHandle
from pages.base_page import BasePage


class LoginPage(BasePage):
    """登录页面 Page Object"""

    # 登录页路径
    LOGIN_PATH = "/login"

    def __init__(self, page: Page):
        super().__init__(page)

        # ============ 账号密码区域 ============
        # 账号输入框（placeholder 含"账号"）
        self.locator_account = (
            page.locator('input[placeholder*="账号"]')
            .or_(page.locator('input[placeholder*="手机号"]'))
            .or_(page.locator('input[name="username"]'))
        )

        # 密码输入框
        self.locator_password = (
            page.locator('input[type="password"]')
            .or_(page.locator('input[placeholder*="密码"]'))
        )

        # 登录按钮
        self.locator_login_btn = (
            page.get_by_role("button", name="登录")
            .or_(page.locator('button:has-text("登录")'))
            .or_(page.locator('button[type="submit"]'))
        )

        # ============ 滑块验证区域 ============
        # 滑块按钮
        self.locator_slider_btn = page.locator(".km-slide-login__btn")
        # 滑块轨道容器
        self.locator_slider_track = page.locator(".km-slide-login")

        # ============ "已在另一设备登录"确认弹窗 ============
        # Element Plus MessageBox / Dialog 弹窗
        self.locator_confirm_dialog = (
            page.locator('.el-message-box')
            .or_(page.locator('.el-dialog'))
            .or_(page.locator('.ivu-modal'))
        )
        # 弹窗中的"继续登录"按钮
        self.locator_continue_login_btn = (
            page.get_by_role("button", name="继续登录")
            .or_(page.locator('.el-message-box__btns button:has-text("继续登录")'))
            .or_(page.locator('.el-dialog button:has-text("继续登录")'))
            .or_(page.locator('button:has-text("继续登录")'))
        )
        
        # ============ 错误提示模态框 ============
        # 账号或密码错误等提示框
        self.locator_error_modal = (
            page.locator('.ivu-modal')
            .or_(page.locator('.el-message-box'))
        )
        # 错误模态框中的确定按钮
        self.locator_error_modal_ok_btn = (
            page.get_by_role("button", name="确定")
            .or_(page.locator('.ivu-modal-footer button:has-text("确定")'))
            .or_(page.locator('.el-message-box__btns button:has-text("确定")'))
            .or_(page.locator('button:has-text("确定")'))
        )

        # ============ 提示信息 ============
        # Element Plus 消息提示（错误）
        self.locator_error_message = (
            page.locator('.el-message--error')
            .or_(page.locator('.el-message.is-error'))
            .or_(page.locator('.ivu-message-error'))
            .or_(page.locator('.ivu-message-error .ivu-message-content'))
        )
        # Element Plus 消息提示（任意类型）
        self.locator_any_message = (
            page.locator('.el-message')
            .or_(page.locator('.ivu-message'))
        )
        # 表单校验错误
        self.locator_form_error = (
            page.locator('.el-form-item__error')
            .or_(page.locator('.ivu-form-item-error'))
        )

        # ============ 登录成功后的元素 ============
        # 左侧导航菜单
        self.locator_sidebar = page.locator('.el-menu, [class*="sidebar"], [class*="nav-menu"]')
        # 顶部用户信息区域
        self.locator_header_user = page.locator('[class*="header"] [class*="user"]')

    # ------------------------------------------
    # 导航
    # ------------------------------------------
    def navigate(self, path: str = None):
        """
        导航到登录页面
        :param path: 页面路径，默认 /login
        """
        try:
            self.page.goto(path or self.LOGIN_PATH, timeout=60000, wait_until="commit")
            # 只要 commit 了，说明已经开始加载页面，后续可以通过显式等待来处理
        except Exception as e:
            print(f"导航过程中发生异常 (可能超时): {e}")
            # 如果超时，尝试再次刷新或继续
            try:
                self.page.reload(timeout=30000)
            except:
                pass
        
        # 尝试等待某个关键元素出现，而不是等待 networkidle
        try:
            self.locator_account.first.wait_for(state="visible", timeout=10000)
        except:
            print("警告: 登录页面关键元素未在10秒内出现")

    # ------------------------------------------
    # 表单操作
    # ------------------------------------------
    def fill_account(self, account: str):
        """填写账号"""
        self.wait_and_fill(self.locator_account, account)

    def fill_password(self, password: str):
        """填写密码"""
        self.wait_and_fill(self.locator_password, password)

    def click_login_button(self):
        """点击登录按钮"""
        self.wait_and_click(self.locator_login_btn)

    # ------------------------------------------
    # 滑块验证
    # ------------------------------------------
    def has_slider(self, timeout: int = 3000) -> bool:
        """
        检查滑块是否出现
        :param timeout: 等待超时（毫秒）
        :return: 是否出现滑块
        """
        try:
            self.locator_slider_btn.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def drag_slider(self) -> bool:
        """
        拟人化拖动滑块到轨道末端
        :return: 拖动是否成功
        """
        try:
            slider = self.locator_slider_btn.element_handle(timeout=5000)
            if not slider:
                return False

            # 获取轨道宽度
            track_width = 300  # 默认宽度
            try:
                track = self.locator_slider_track.element_handle(timeout=2000)
                if track:
                    track_box = track.bounding_box()
                    if track_box and track_box['width'] > 50:
                        track_width = track_box['width']
            except Exception:
                pass

            # 获取滑块位置
            box = slider.bounding_box()
            if not box:
                return False

            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2
            target_distance = track_width - box['width'] - 2

            # 移动到滑块并按下
            self.page.mouse.move(start_x, start_y)
            self.page.wait_for_timeout(random.randint(100, 250))
            self.page.mouse.down()
            self.page.wait_for_timeout(random.randint(50, 150))

            # ease-out 曲线拖动（先快后慢 + Y 轴抖动）
            steps = random.randint(30, 45)
            for i in range(1, steps + 1):
                t = i / steps
                progress = 1 - (1 - t) ** 3
                cur_x = start_x + target_distance * progress
                offset_y = random.uniform(-2, 2)
                self.page.mouse.move(cur_x, start_y + offset_y)

                if t < 0.3:
                    self.page.wait_for_timeout(random.randint(5, 12))
                elif t < 0.7:
                    self.page.wait_for_timeout(random.randint(8, 18))
                else:
                    self.page.wait_for_timeout(random.randint(15, 30))

            # 到位后松开
            self.page.wait_for_timeout(random.randint(100, 250))
            self.page.mouse.up()
            return True

        except Exception:
            return False

    def drag_slider_with_retry(self, max_retries: int = 3) -> bool:
        """
        带重试的滑块拖动
        :param max_retries: 最大重试次数
        :return: 是否成功
        """
        for attempt in range(1, max_retries + 1):
            if self.drag_slider():
                self.page.wait_for_timeout(1500)
                # 滑块消失 或 页面已跳转 → 成功
                if not self.has_slider(timeout=1000):
                    return True
                if "login" not in self.page.url.lower():
                    return True
            self.page.wait_for_timeout(random.randint(500, 1000))
        return False

    # ------------------------------------------
    # "已在另一设备登录"确认弹窗
    # ------------------------------------------
    def has_continue_login_dialog(self, timeout: int = 3000) -> bool:
        """
        检查是否出现"该账号已在另一设备登录"确认弹窗
        :param timeout: 等待超时（毫秒）
        :return: 是否出现
        """
        try:
            self.locator_continue_login_btn.first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def click_continue_login(self) -> None:
        """点击"继续登录"按钮"""
        self.locator_continue_login_btn.first.click()
        print("  已点击「继续登录」按钮")

    def handle_continue_login_dialog(self, timeout: int = 3000) -> bool:
        """
        检测并处理"该账号已在另一设备登录"确认弹窗
        :param timeout: 等待弹窗出现的超时时间
        :return: True=弹窗出现并已点击继续登录，False=未出现弹窗
        """
        if self.has_continue_login_dialog(timeout=timeout):
            print("  检测到「该账号已在另一设备登录」确认弹窗")
            self.click_continue_login()
            self.page.wait_for_timeout(1000)
            return True
        return False

    # ------------------------------------------
    # 组合操作
    # ------------------------------------------
    def login(self, account: str, password: str, handle_slider: bool = True, handle_dialog: bool = True) -> None:
        """
        完整登录操作：填写 → 点击登录 → 滑块验证 → 处理"继续登录"弹窗
        :param account: 账号
        :param password: 密码
        :param handle_slider: 是否自动处理滑块验证
        :param handle_dialog: 是否自动处理"该账号已在另一设备登录"确认弹窗
        """
        self.fill_account(account)
        self.fill_password(password)
        self.click_login_button()

        if handle_slider and self.has_slider(timeout=5000):
            self.drag_slider_with_retry()

        # 滑块完成后可能弹出"该账号已在另一设备登录"确认框
        if handle_dialog:
            self.handle_continue_login_dialog(timeout=3000)

    def login_without_slider(self, account: str, password: str) -> None:
        """
        仅填写账号密码并点击登录，不处理滑块
        用于测试输入校验等不会触发滑块的场景
        """
        self.fill_account(account)
        self.fill_password(password)
        self.click_login_button()

    # ------------------------------------------
    # 结果验证
    # ------------------------------------------
    def get_error_message(self, timeout: int = 3000) -> str:
        """
        获取错误提示信息（el-message 弹窗）
        :param timeout: 等待超时
        :return: 错误信息文本，未找到返回空字符串
        """
        return self.get_text(self.locator_error_message, timeout)

    def get_any_message(self, timeout: int = 3000) -> str:
        """
        获取任意类型的提示信息
        :return: 提示信息文本
        """
        return self.get_text(self.locator_any_message, timeout)

    def get_form_error(self, timeout: int = 2000) -> str:
        """
        获取表单校验错误信息
        :return: 表单错误文本
        """
        try:
            self.locator_form_error.first.wait_for(state="visible", timeout=timeout)
            text = self.locator_form_error.first.text_content() or ""
            text = text.strip()
            # 移除可能的标签文本（如"登录账号"），只保留错误提示
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) > 1 and ('请输入' in lines[-1] or '不能为空' in lines[-1] or '必填' in lines[-1]):
                return lines[-1]
            return text
        except Exception:
            return ""

    def get_error_modal_text(self, timeout: int = 5000) -> str:
        """
        获取错误模态框中的错误信息（如"账号或密码错误"）
        :return: 错误信息文本
        """
        try:
            # 查找可见的模态框
            modals = self.locator_error_modal.all()
            visible_modal = None
            for modal in modals:
                try:
                    if modal.is_visible():
                        visible_modal = modal
                        break
                except:
                    pass
            
            if not visible_modal:
                return ""
            
            text = visible_modal.text_content() or ""
            text = text.strip()
            # 移除标题和按钮文本，只保留错误信息
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            # 查找包含"错误"、"失败"、"无效"的行
            for line in lines:
                if '错误' in line or '失败' in line or '无效' in line:
                    # 提取核心错误信息，去除平台名称等前缀
                    if '账号或密码错误' in line:
                        return '账号或密码错误'
                    if '密码错误' in line:
                        return '密码错误'
                    if '账号错误' in line:
                        return '账号错误'
                    return line
            # 如果没有找到，返回最后一行（通常是错误信息）
            if lines:
                return lines[-1]
            return text
        except Exception as e:
            print(f"  get_error_modal_text 异常: {e}")
            return ""

    def is_login_successful(self, timeout: int = 15000) -> bool:
        """
        验证登录是否成功
        判断依据：URL 不再包含 login（跳转到后台首页）
        :param timeout: 超时时间（毫秒）
        """
        try:
            self.page.wait_for_url(
                lambda url: "login" not in url.lower(),
                timeout=timeout,
            )
            return True
        except Exception:
            return False

    def is_on_login_page(self) -> bool:
        """当前是否仍在登录页"""
        return "login" in self.page.url.lower()
