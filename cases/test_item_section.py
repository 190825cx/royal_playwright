"""
商品课组管理功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/ItemSectionList
功能: 新增课组、查询课组、编辑课组、删除课组
"""

from pages.item_section_page import ItemSectionPage
from playwright.sync_api import Page
import pytest
import allure
import random
import time


@allure.epic("云帆系统")
@allure.feature("商品课组管理")
class TestItemSection:
    """商品课组功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, logged_page: Page, base_url: str):
        """每个测试用例前：导航到商品课组管理页面（复用已保存的登录态）"""
        self.page = logged_page
        self.section_page = ItemSectionPage(logged_page, base_url)

        self.section_page.navigate_to_section()
        assert self.section_page.is_on_section_page(), "未成功导航到商品课组管理页面"
        print(f"已导航到商品课组管理页面，当前URL: {self.page.url}")

        yield

    @allure.story("完整流程：新增、查询、编辑、删除")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_item_section_workflow(self):
        """完整流程-新增课组、查询、编辑课组、删除"""
        allure.dynamic.title("完整流程-新增课组、查询、编辑课组、删除")

        rand_id = random.randint(1000, 9999)
        section_data = {
            "code": f"{rand_id}",          # 编码最多4字符，仅数字
            "name": f"课组{rand_id}测试",  # 名称最多20字符
        }
        edit_name = f"课组{rand_id}已改"
        print(f"测试课组数据: {section_data}")

        # 步骤1: 新增课组
        with allure.step("步骤1: 新增课组"):
            print("\n步骤1: 新增课组")
            self.section_page.add_item_section(section_data)

            success_msg = self.section_page.get_success_message(timeout=5000)
            print(f"保存提示: {success_msg}")

            if not success_msg:
                form_errors = self.section_page.get_form_errors()
                if form_errors:
                    print(f"表单校验错误: {form_errors}")
                else:
                    error_msg = self.section_page.get_error_message(timeout=2000)
                    if error_msg:
                        print(f"保存失败错误: {error_msg}")

        # 步骤2: 查询课组
        with allure.step("步骤2: 查询课组"):
            print("\n步骤2: 查询课组")
            self.section_page.search_section(section_data["name"])
            time.sleep(2)

            assert self.section_page.is_section_exists(name=section_data["name"]), (
                f"课组未在列表中找到，名称: {section_data['name']}"
            )
            print(f"查询成功，课组名称: {section_data['name']}")

        # 步骤3: 编辑课组
        with allure.step("步骤3: 编辑课组"):
            print("\n步骤3: 编辑课组")
            self.section_page.edit_first_row({"name": edit_name})

            success_msg = self.section_page.get_success_message(timeout=5000)
            print(f"修改提示: {success_msg}")

            # 重新查询修改后的名称，验证修改成功
            self.section_page.search_section(edit_name)
            time.sleep(2)
            assert self.section_page.is_section_exists(name=edit_name), (
                f"修改后的课组未在列表中找到，名称: {edit_name}"
            )
            print(f"修改验证成功，课组名称: {edit_name}")

        # 步骤4: 删除课组
        with allure.step("步骤4: 删除课组"):
            print("\n步骤4: 删除课组")
            self.section_page.delete_section()

            success_msg = self.section_page.get_success_message(timeout=5000)
            print(f"删除提示: {success_msg}")

            # 验证已被删除
            self.section_page.search_section(edit_name)
            time.sleep(2)
            assert not self.section_page.is_section_exists(name=edit_name), (
                f"课组删除后仍在列表中，名称: {edit_name}"
            )
            print(f"删除成功，课组名称: {edit_name}")
