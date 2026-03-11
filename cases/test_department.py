"""
部门档案功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/Department
功能: 新增部门、填写必填项、保存、查询、导出、删除
"""

from pages.login_page import LoginPage
from pages.department_page import DepartmentPage
from playwright.sync_api import Page
import pytest
import allure
import time


@allure.epic("云帆系统")
@allure.feature("部门档案")
class TestDepartment:
    """部门档案功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, unlogin_page: Page):
        """每个测试用例前：登录 → 导航到部门档案页面"""
        self.page = unlogin_page
        self.login_page = LoginPage(unlogin_page)
        self.department_page = DepartmentPage(unlogin_page)

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

        # 导航到部门档案页面
        self.department_page.navigate_to_department()
        assert self.department_page.is_on_department_page(), "未成功导航到部门档案页面"
        print(f"已导航到部门档案页面，当前URL: {self.page.url}")

        yield

    # ==========================================================
    # 完整流程场景：新增、保存、查询、导出、删除
    # ==========================================================
    @allure.story("完整流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_department_workflow(self):
        """完整流程-新增部门、填写必填项、保存、查询、导出、删除"""
        allure.dynamic.title("完整流程-新增部门、填写必填项、保存、查询、导出、删除")

        # 准备测试数据
        timestamp = int(time.time())
        department_data = {
            "code": f"{timestamp % 10000:04d}",  # 商品部门编码（数字）
            "name": f"测试部门{timestamp % 100:02d}",  # 商品部门（中文）
        }
        print(f"测试部门数据: {department_data}")

        # 步骤1: 新增部门
        with allure.step("步骤1: 新增部门"):
            print("\n步骤1: 新增部门")
            self.department_page.add_department(department_data)
            print("已填写部门信息")

        # 步骤2: 保存部门
        with allure.step("步骤2: 保存部门"):
            print("\n步骤2: 保存部门")
            self.department_page.save_department()
            success_msg = self.department_page.get_success_message(timeout=5000)
            print(f"保存提示: {success_msg}")

            if not success_msg:
                form_errors = self.department_page.get_form_errors()
                if form_errors:
                    print(f"表单校验错误: {form_errors}")
                else:
                    error_msg = self.department_page.get_error_message(timeout=2000)
                    if error_msg:
                        print(f"保存失败错误: {error_msg}")

        # 步骤3: 查询部门
        with allure.step("步骤3: 查询部门"):
            print("\n步骤3: 查询部门")
            self.department_page.search_department(department_data["name"])
            time.sleep(2)

            assert self.department_page.is_department_exists(name=department_data["name"]), (
                f"部门未在列表中找到，名称: {department_data['name']}"
            )
            print(f"查询成功，部门名称: {department_data['name']}")

        # 步骤4: 导出
        with allure.step("步骤4: 导出"):
            print("\n步骤4: 导出")
            self.department_page.click_export()
            print("导出操作已完成")

        # 步骤5: 删除部门
        with allure.step("步骤5: 删除部门"):
            print("\n步骤5: 删除部门")
            self.department_page.delete_department()
            success_msg = self.department_page.get_success_message(timeout=5000)
            print(f"删除提示: {success_msg}")

            # 验证部门已被删除
            self.department_page.search_department(department_data["name"])
            time.sleep(2)
            assert not self.department_page.is_department_exists(name=department_data["name"]), (
                f"部门删除后仍在列表中，名称: {department_data['name']}"
            )
            print(f"删除成功，部门名称: {department_data['name']}")
