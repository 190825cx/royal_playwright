"""
品牌管理功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/ItemBrand
功能: 新增品牌、填写必填项、保存、查询、导出、删除
"""

from pages.login_page import LoginPage
from pages.brand_page import BrandPage
from playwright.sync_api import Page
import pytest
import allure
import time


@allure.epic("云帆系统")
@allure.feature("品牌管理")
class TestBrand:
    """品牌管理功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, unlogin_page: Page):
        """每个测试用例前：登录 → 导航到品牌管理页面"""
        self.page = unlogin_page
        self.login_page = LoginPage(unlogin_page)
        self.brand_page = BrandPage(unlogin_page)

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

        # 导航到品牌管理页面
        self.brand_page.navigate_to_brand()
        assert self.brand_page.is_on_brand_page(), "未成功导航到品牌管理页面"
        print(f"已导航到品牌管理页面，当前URL: {self.page.url}")

        yield

    # ==========================================================
    # 完整流程场景：新增、保存、查询、导出、删除
    # ==========================================================
    @allure.story("完整流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_brand_workflow(self):
        """完整流程-新增品牌、填写必填项、保存、查询、导出、删除"""
        allure.dynamic.title("完整流程-新增品牌、填写必填项、保存、查询、导出、删除")

        # 准备测试数据
        timestamp = int(time.time())
        brand_data = {
            "code": f"B{timestamp % 1000:03d}",  # 品牌编码
            "name": f"测试品牌{timestamp % 100:02d}",  # 品牌名称
        }
        print(f"测试品牌数据: {brand_data}")

        # 步骤1: 新增品牌
        with allure.step("步骤1: 新增品牌"):
            print("\n步骤1: 新增品牌")
            self.brand_page.add_brand(brand_data)
            print("已填写品牌信息")

        # 步骤2: 保存品牌
        with allure.step("步骤2: 保存品牌"):
            print("\n步骤2: 保存品牌")
            self.brand_page.save_brand()
            success_msg = self.brand_page.get_success_message(timeout=5000)
            print(f"保存提示: {success_msg}")

            if not success_msg:
                form_errors = self.brand_page.get_form_errors()
                if form_errors:
                    print(f"表单校验错误: {form_errors}")
                else:
                    error_msg = self.brand_page.get_error_message(timeout=2000)
                    if error_msg:
                        print(f"保存失败错误: {error_msg}")

        # 步骤3: 查询品牌
        with allure.step("步骤3: 查询品牌"):
            print("\n步骤3: 查询品牌")
            self.brand_page.search_brand(brand_data["name"])
            time.sleep(2)

            assert self.brand_page.is_brand_exists(name=brand_data["name"]), (
                f"品牌未在列表中找到，名称: {brand_data['name']}"
            )
            print(f"查询成功，品牌名称: {brand_data['name']}")

        # 步骤4: 导出
        with allure.step("步骤4: 导出"):
            print("\n步骤4: 导出")
            self.brand_page.click_export()
            print("导出操作已完成")

        # 步骤5: 删除品牌
        with allure.step("步骤5: 删除品牌"):
            print("\n步骤5: 删除品牌")
            self.brand_page.delete_brand()
            success_msg = self.brand_page.get_success_message(timeout=5000)
            print(f"删除提示: {success_msg}")

            # 验证品牌已被删除
            self.brand_page.search_brand(brand_data["name"])
            time.sleep(2)
            assert not self.brand_page.is_brand_exists(name=brand_data["name"]), (
                f"品牌删除后仍在列表中，名称: {brand_data['name']}"
            )
            print(f"删除成功，品牌名称: {brand_data['name']}")
