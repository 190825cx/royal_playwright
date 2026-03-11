"""
类别管理功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/ItemCategory
功能: 新增类别、填写必填项、保存、查询、导出、删除
"""

from pages.login_page import LoginPage
from pages.category_page import CategoryPage
from playwright.sync_api import Page
import pytest
import allure
import time


@allure.epic("云帆系统")
@allure.feature("类别管理")
class TestCategory:
    """类别管理功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, unlogin_page: Page):
        """每个测试用例前：登录 → 导航到类别管理页面"""
        self.page = unlogin_page
        self.login_page = LoginPage(unlogin_page)
        self.category_page = CategoryPage(unlogin_page)

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

        # 导航到类别管理页面
        self.category_page.navigate_to_category()
        assert self.category_page.is_on_category_page(), "未成功导航到类别管理页面"
        print(f"已导航到类别管理页面，当前URL: {self.page.url}")

        yield

    # ==========================================================
    # 完整流程场景：新增、保存、查询、导出、删除
    # ==========================================================
    @allure.story("完整流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_category_workflow(self):
        """完整流程-新增类别、填写必填项、保存、查询、导出、删除"""
        allure.dynamic.title("完整流程-新增类别、填写必填项、保存、查询、导出、删除")

        # 准备测试数据
        timestamp = int(time.time())
        category_data = {
            "code": f"{timestamp % 90 + 10:02d}",  # 类别编码（两位数字10-99）
            "name": f"测试{timestamp % 10000:04d}",  # 类别名称（4位数字后缀保证唯一）
        }
        print(f"测试类别数据: {category_data}")

        # 步骤1: 新增类别
        with allure.step("步骤1: 新增类别"):
            print("\n步骤1: 新增类别")
            self.category_page.add_category(category_data)
            print("已填写类别信息")

        # 步骤2: 保存类别
        with allure.step("步骤2: 保存类别"):
            print("\n步骤2: 保存类别")
            self.category_page.save_category()
            success_msg = self.category_page.get_success_message(timeout=5000)
            print(f"保存提示: {success_msg}")

            if not success_msg:
                form_errors = self.category_page.get_form_errors()
                if form_errors:
                    print(f"表单校验错误: {form_errors}")
                else:
                    error_msg = self.category_page.get_error_message(timeout=2000)
                    if error_msg:
                        print(f"保存失败错误: {error_msg}")

        # 步骤3: 查询类别
        with allure.step("步骤3: 查询类别"):
            print("\n步骤3: 查询类别")
            self.category_page.search_category(category_data["name"])
            time.sleep(2)

            assert self.category_page.is_category_exists(name=category_data["name"]), (
                f"类别未在列表中找到，名称: {category_data['name']}"
            )
            print(f"查询成功，类别名称: {category_data['name']}")

        # 步骤4: 导出
        with allure.step("步骤4: 导出"):
            print("\n步骤4: 导出")
            self.category_page.click_export()
            print("导出操作已完成")

        # 步骤5: 删除类别
        with allure.step("步骤5: 删除类别"):
            print("\n步骤5: 删除类别")
            self.category_page.delete_category()
            success_msg = self.category_page.get_success_message(timeout=5000)
            print(f"删除提示: {success_msg}")

            # 验证类别已被删除（搜索精确名称后表格应为空）
            self.category_page.search_category(category_data["name"])
            time.sleep(2)
            assert not self.category_page.is_category_exists(name=category_data["name"]), (
                f"类别删除后仍在列表中，名称: {category_data['name']}"
            )
            print(f"删除成功，类别名称: {category_data['name']}")
