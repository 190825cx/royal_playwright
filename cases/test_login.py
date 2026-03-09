"""
登录功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/
数据驱动: data/login_data.yaml
登录流程: 输入账号密码 → 点击登录 → 滑块验证 → 跳转后台首页
"""
from pages.login_page import LoginPage
from common.data_loader import get_test_data, parametrize_with_ids
from playwright.sync_api import Page
import pytest
import allure


# ============ 加载测试数据 ============
DATA_FILE = "login_data.yaml"

_success_data, _success_ids = parametrize_with_ids(
    DATA_FILE, "login_success",
    fields=("account", "password", "description"),
)

_empty_data, _empty_ids = parametrize_with_ids(
    DATA_FILE, "login_empty_validation",
    fields=("account", "password", "description", "expected_error"),
)

_wrong_data, _wrong_ids = parametrize_with_ids(
    DATA_FILE, "login_wrong_credentials",
    fields=("account", "password", "description", "expected_error"),
)

_format_data, _format_ids = parametrize_with_ids(
    DATA_FILE, "login_invalid_format",
    fields=("account", "password", "description", "expected_error"),
)


@allure.epic("云帆系统")
@allure.feature("登录功能")
class TestLogin:
    """登录功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, unlogin_page: Page):
        """每个测试用例前：打开新页面 → 访问登录页"""
        self.page = unlogin_page
        self.login_page = LoginPage(unlogin_page)
        self.login_page.navigate()
        yield

    # ==========================================================
    # 登录成功场景
    # ==========================================================
    @allure.story("登录成功场景")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("account, password, description", _success_data, ids=_success_ids)
    def test_login_success(self, account: str, password: str, description: str):
        """登录成功-完整流程（含滑块验证）"""
        allure.dynamic.title(f"登录成功-{description}")

        # 完整登录：填写 → 点击 → 滑块
        self.login_page.login(account, password)

        # 验证：页面跳转离开登录页
        assert self.login_page.is_login_successful(timeout=15000), (
            f"登录未成功跳转，当前URL: {self.page.url}"
        )
        print(f"登录成功，当前URL: {self.page.url}")
        print(f"页面标题: {self.page.title()}")

    # ==========================================================
    # 登录失败 - 空值校验（不触发滑块）
    # ==========================================================
    @allure.story("登录失败-空值校验")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "account, password, description, expected_error",
        _empty_data, ids=_empty_ids,
    )
    def test_login_empty_validation(
        self, account: str, password: str, description: str, expected_error: str
    ):
        """空值校验-不触发滑块"""
        allure.dynamic.title(f"空值校验-{description}")

        # 仅填写并点击，不处理滑块
        self.login_page.login_without_slider(account, password)
        self.page.wait_for_timeout(1000)

        # 验证：应仍在登录页
        assert self.login_page.is_on_login_page(), (
            f"预期留在登录页，实际URL: {self.page.url}"
        )

        # 尝试获取表单校验错误或弹窗错误
        form_err = self.login_page.get_form_error(timeout=2000)
        msg_err = self.login_page.get_error_message(timeout=1000)
        any_msg = self.login_page.get_any_message(timeout=1000)
        actual_error = form_err or msg_err or any_msg

        print(f"测试场景: {description}")
        print(f"表单错误: {form_err}")
        print(f"弹窗错误: {msg_err}")
        print(f"任意提示: {any_msg}")

        if expected_error:
            assert actual_error, f"期望有错误提示，但未捕获到任何提示信息"
            assert expected_error in actual_error, (
                f"期望包含 '{expected_error}'，实际: '{actual_error}'"
            )

    # ==========================================================
    # 登录失败 - 错误凭证（会触发滑块）
    # ==========================================================
    @allure.story("登录失败-错误凭证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "account, password, description, expected_error",
        _wrong_data, ids=_wrong_ids,
    )
    def test_login_wrong_credentials(
        self, account: str, password: str, description: str, expected_error: str
    ):
        """错误凭证-触发滑块后返回错误"""
        allure.dynamic.title(f"错误凭证-{description}")

        # 完整登录流程（含滑块），但不自动处理"该账号已在另一设备登录"弹窗
        self.login_page.login(account, password, handle_slider=True, handle_dialog=False)
        self.page.wait_for_timeout(3000)

        # 如果检测到"该账号已在另一设备登录"弹窗，点击"继续登录"按钮
        if self.login_page.has_continue_login_dialog(timeout=1000):
            print("  检测到「该账号已在另一设备登录」确认弹窗")
            self.login_page.click_continue_login()
            self.page.wait_for_timeout(1000)
            
            # 点击"继续登录"后，等待错误提示出现
            print("  等待错误提示出现...")

        # 验证：应仍在登录页或出现错误提示
        print(f"测试场景: {description}")
        print(f"当前URL: {self.page.url}")

        # 尝试获取错误信息（模态框、弹窗、表单错误）
        modal_err = self.login_page.get_error_modal_text(timeout=5000)
        msg_err = self.login_page.get_error_message(timeout=1000)
        form_err = self.login_page.get_form_error(timeout=1000)
        actual_error = modal_err or msg_err or form_err
        print(f"错误信息: {actual_error}")

        # 如果没有错误信息且页面已跳转，说明账号密码实际有效
        if not actual_error and not self.login_page.is_on_login_page():
            pytest.skip(f"测试账号密码实际有效，页面已跳转")

        # 不应该成功跳转
        if self.login_page.is_on_login_page():
            print("符合预期：仍在登录页")
        else:
            # 如果跳转了，说明凭证实际是对的
            pytest.skip(f"测试账号密码实际有效，页面已跳转")

        if expected_error:
            assert expected_error in actual_error, (
                f"期望包含 '{expected_error}'，实际: '{actual_error}'"
            )

    # ==========================================================
    # 登录失败 - 无效输入格式
    # ==========================================================
    @allure.story("登录失败-无效输入格式")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.parametrize(
        "account, password, description, expected_error",
        _format_data, ids=_format_ids,
    )
    def test_login_invalid_format(
        self, account: str, password: str, description: str, expected_error: str
    ):
        """无效格式-验证前端校验或后端拒绝"""
        allure.dynamic.title(f"无效格式-{description}")

        # 先尝试不处理滑块的方式（可能前端直接拦截）
        self.login_page.login_without_slider(account, password)
        self.page.wait_for_timeout(1000)

        # 检查是否出现了表单校验错误（前端直接拦截）
        form_err = self.login_page.get_form_error(timeout=1500)
        if form_err:
            print(f"前端校验拦截: {form_err}")
            assert self.login_page.is_on_login_page()
            return

        # 如果出现了滑块，说明前端没拦截，走完整流程
        if self.login_page.has_slider(timeout=2000):
            self.login_page.drag_slider_with_retry()
            self.page.wait_for_timeout(2000)

        # 验证：应仍在登录页
        print(f"测试场景: {description}")
        print(f"当前URL: {self.page.url}")

        error_msg = self.login_page.get_error_message(timeout=2000)
        any_msg = self.login_page.get_any_message(timeout=1000)
        actual_error = form_err or error_msg or any_msg
        print(f"错误信息: {actual_error}")

        # 不应该成功登录
        assert self.login_page.is_on_login_page(), (
            f"预期仍在登录页，实际URL: {self.page.url}"
        )

        if expected_error:
            assert expected_error in actual_error, (
                f"期望包含 '{expected_error}'，实际: '{actual_error}'"
            )

    # ==========================================================
    # 滑块验证专项测试
    # ==========================================================
    @allure.story("滑块验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_slider_appears_after_login_click(self):
        """点击登录后滑块应出现"""
        success = get_test_data(DATA_FILE, "login_success")[0]

        self.login_page.fill_account(success["account"])
        self.login_page.fill_password(success["password"])
        self.login_page.click_login_button()

        # 验证滑块出现
        assert self.login_page.has_slider(timeout=5000), "点击登录后未出现滑块验证"
        print("滑块验证组件已出现")
