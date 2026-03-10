"""
单位管理功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/unit
功能: 新增单位、填写必填项、保存、查询、删除
"""

from pages.login_page import LoginPage
from pages.unit_page import UnitPage
from playwright.sync_api import Page
import pytest
import allure
import time


@allure.epic("云帆系统")
@allure.feature("单位管理")
class TestUnit:
    """单位管理功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, unlogin_page: Page):
        """每个测试用例前：登录 → 导航到单位管理页面"""
        self.page = unlogin_page
        self.login_page = LoginPage(unlogin_page)
        self.unit_page = UnitPage(unlogin_page)

        # 登录
        self.login_page.navigate("https://royal-pre.cs.kemai.com.cn/login")
        self.login_page.login("15901234562", "123123123")

        # 等待登录成功
        assert self.login_page.is_login_successful(timeout=15000), "登录失败"
        print(f"登录成功，当前URL: {self.page.url}")

        # 等待并关闭可能出现的弹窗
        time.sleep(2)
        try:
            visible_modals = self.page.locator(".ivu-modal-wrap:visible").all()
            for modal in visible_modals:
                cancel_btn = modal.locator("button").filter(has_text="取消").first
                if cancel_btn.count() > 0 and cancel_btn.is_visible():
                    cancel_btn.click()
                    time.sleep(0.5)
            self.page.keyboard.press("Escape")
            time.sleep(0.5)
        except:
            pass

        # 导航到单位管理页面
        self.unit_page.navigate_to_unit()
        assert self.unit_page.is_on_unit_page(), "未成功导航到单位管理页面"
        print(f"已导航到单位管理页面，当前URL: {self.page.url}")

        yield

    # ==========================================================
    # 完整流程场景：新增、保存、查询、删除
    # ==========================================================
    @allure.story("完整流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_unit_workflow(self):
        """完整流程-新增单位、填写必填项、保存、查询、删除"""
        allure.dynamic.title("完整流程-新增单位、填写必填项、保存、查询、删除")

        # 准备测试数据（单位名称最多4位）
        timestamp = int(time.time())
        unit_data = {
            "name": f"T{timestamp % 1000:03d}",
        }
        print(f"测试单位数据: {unit_data}")

        # 步骤1: 新增单位
        with allure.step("步骤1: 新增单位"):
            print("\n步骤1: 新增单位")
            self.unit_page.add_unit(unit_data)
            print("已填写单位信息")

        # 步骤2: 保存单位
        with allure.step("步骤2: 保存单位"):
            print("\n步骤2: 保存单位")
            self.unit_page.save_unit()
            success_msg = self.unit_page.get_success_message(timeout=5000)
            print(f"保存提示: {success_msg}")

            if not success_msg:
                form_errors = self.unit_page.get_form_errors()
                if form_errors:
                    print(f"表单校验错误: {form_errors}")
                else:
                    error_msg = self.unit_page.get_error_message(timeout=2000)
                    if error_msg:
                        print(f"保存失败错误: {error_msg}")

        # 步骤3: 查询单位
        with allure.step("步骤3: 查询单位"):
            print("\n步骤3: 查询单位")
            self.unit_page.search_unit(unit_data["name"])
            time.sleep(2)

            assert self.unit_page.is_unit_exists(name=unit_data["name"]), (
                f"单位未在列表中找到，名称: {unit_data['name']}"
            )
            print(f"查询成功，单位名称: {unit_data['name']}")

        # 步骤4: 删除单位
        with allure.step("步骤4: 删除单位"):
            print("\n步骤4: 删除单位")
            self.unit_page.delete_unit()
            success_msg = self.unit_page.get_success_message(timeout=5000)
            print(f"删除提示: {success_msg}")

            # 验证单位已被删除
            self.unit_page.search_unit(unit_data["name"])
            time.sleep(2)
            assert not self.unit_page.is_unit_exists(name=unit_data["name"]), (
                f"单位删除后仍在列表中，名称: {unit_data['name']}"
            )
            print(f"删除成功，单位名称: {unit_data['name']}")
