"""
商品档案功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/retail/product/item
功能: 新增商品、填写必填项、保存、审核、查询
"""

from pages.login_page import LoginPage
from pages.product_item_page import ProductItemPage
from playwright.sync_api import Page
import pytest
import allure
import time


@allure.epic("云帆系统")
@allure.feature("商品档案")
class TestProductItem:
    """商品档案功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, unlogin_page: Page):
        """每个测试用例前：登录 → 导航到商品档案页面"""
        self.page = unlogin_page
        self.login_page = LoginPage(unlogin_page)
        self.product_item_page = ProductItemPage(unlogin_page)

        # 登录 - 使用完整 URL
        self.login_page.navigate("https://royal-pre.cs.kemai.com.cn/login")
        self.login_page.login("15901234562", "123123123")

        # 等待登录成功
        assert self.login_page.is_login_successful(timeout=15000), "登录失败"
        print(f"登录成功，当前URL: {self.page.url}")

        # 等待应用到期提醒弹窗并关闭
        time.sleep(2)
        try:
            # 尝试关闭所有可见弹窗
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

        # 导航到商品档案页面
        self.product_item_page.navigate_via_menu()
        assert self.product_item_page.is_on_product_item_page(), (
            "未成功导航到商品档案页面"
        )
        print(f"已导航到商品档案页面，当前URL: {self.page.url}")

        yield

    # ==========================================================
    # 完整流程场景：新增、保存、审核、查询
    # ==========================================================
    @allure.story("完整流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_product_workflow(self):
        """完整流程-新增、保存、审核、查询"""
        allure.dynamic.title("完整流程-新增、保存、审核、查询")

        # 准备测试数据
        timestamp = int(time.time())
        product_data = {
            "code": f"{timestamp % 10000000000:010d}",
            "name": f"测试商品{timestamp}",
            "barcode": f"6901234{timestamp % 1000000:06d}",
            "spec": "500ml",
            "unit": "瓶",
            "category": "0001",
            "brand": "0001",
            "supplier": "0001",  # 主供应商，会弹出pick选择第一个
            "purchase_price": "10.00",
            "retail_price": "15.00",
            "storage": "常温",
        }

        print(f"测试商品数据: {product_data}")

        # 步骤1: 新增商品
        print("\n步骤1: 新增商品")
        self.product_item_page.add_product(product_data)
        print("已填写商品信息")

        # 步骤2: 保存商品
        print("\n步骤2: 保存商品")
        self.product_item_page.save_product()
        success_msg = self.product_item_page.get_success_message(timeout=5000)
        print(f"保存提示: {success_msg}")

        if not success_msg:
            form_errors = self.product_item_page.get_form_errors()
            if form_errors:
                print(f"表单校验错误: {form_errors}")
            else:
                error_msg = self.product_item_page.get_error_message(timeout=2000)
                if error_msg:
                    print(f"保存失败错误: {error_msg}")

        # 步骤3: 审核商品
        print("\n步骤3: 审核商品")
        self.product_item_page.audit_product()
        success_msg = self.product_item_page.get_success_message(timeout=5000)
        print(f"审核提示: {success_msg}")

        # 步骤4: 查询商品
        print("\n步骤4: 查询商品")
        self.product_item_page.click_reset()
        self.product_item_page.search_product_by_code(product_data["code"])
        time.sleep(2)

        # 验证商品是否存在
        assert self.product_item_page.is_product_exists(code=product_data["code"]), (
            f"商品未在列表中找到，编码: {product_data['code']}"
        )
        print(f"完整流程执行成功，商品编码: {product_data['code']}")
