"""
类别管理功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/ItemCategory
功能: 新增类别、填写必填项、保存、查询、导出、删除
"""

from pages.category_page import CategoryPage
from playwright.sync_api import Page
import pytest
import allure
import random
import time


@allure.epic("云帆系统")
@allure.feature("类别管理")
class TestCategory:
    """类别管理功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, logged_page: Page, base_url: str):
        """每个测试用例前：直接导航到类别管理页面（复用已保存的登录态）"""
        self.page = logged_page
        self.category_page = CategoryPage(logged_page, base_url)

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
        rand3 = random.randint(100, 999)
        category_data = {
            "code": f"{rand3}",  # 类别编码（3位随机数）
            "name": f"UI测试类别{rand3}",  # 类别名称
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

            # 验证类别已被删除
            self.category_page.search_category(category_data["name"])
            time.sleep(2)
            assert not self.category_page.is_category_exists(name=category_data["name"]), (
                f"类别删除后仍在列表中，名称: {category_data['name']}"
            )
            print(f"删除成功，类别名称: {category_data['name']}")
