"""
调零售价单功能测试用例
测试网站: https://royal-pre.cs.kemai.com.cn/archives/itemPriceChangeList
功能: 新增调零售价单、修改零售价、保存审核、查询单号
"""

from pages.item_price_change_page import ItemPriceChangePage
from playwright.sync_api import Page
import pytest
import allure
import time


@allure.epic("云帆系统")
@allure.feature("调零售价单")
class TestItemPriceChange:
    """调零售价单功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, logged_page: Page, base_url: str):
        """每个测试用例前：导航到调零售价单页面（复用已保存的登录态）"""
        self.page = logged_page
        self.price_change_page = ItemPriceChangePage(logged_page, base_url)

        self.price_change_page.navigate_to_price_change()
        assert self.price_change_page.is_on_price_change_page(), "未成功导航到调零售价单页面"
        print(f"已导航到调零售价单页面，当前URL: {self.page.url}")

        yield

    @allure.story("完整流程：新增调价单、修改零售价、保存审核、查询单号")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_price_change_workflow(self):
        """完整流程-新增调价单、修改零售价、保存审核、查询单号"""
        allure.dynamic.title("完整流程-新增调价单、修改零售价、保存审核、查询单号")

        product_code = "2999900339037"
        new_price = "99.99"
        print(f"测试商品编码: {product_code}, 新零售价: {new_price}")

        # 步骤1: 点击新增
        with allure.step("步骤1: 点击新增"):
            print("\n步骤1: 点击新增")
            self.price_change_page.click_add()
            time.sleep(2)

        # 步骤2: 选择全部机构
        with allure.step("步骤2: 选择全部机构"):
            print("\n步骤2: 选择全部机构")
            self.price_change_page.select_all_organizations()
            time.sleep(1)

        # 步骤3: 点击选择商品
        with allure.step("步骤3: 点击选择商品"):
            print("\n步骤3: 点击选择商品")
            self.price_change_page.click_select_product()
            time.sleep(2)

        # 步骤4: 输入商品编码并搜索
        with allure.step("步骤4: 输入商品编码并搜索"):
            print("\n步骤4: 输入商品编码并搜索")
            self.price_change_page.input_product_code(product_code)
            time.sleep(2)

        # 步骤5: 选择商品并确认
        with allure.step("步骤5: 选择商品并确认"):
            print("\n步骤5: 选择商品并确认")
            self.price_change_page.select_product_and_confirm()
            time.sleep(2)

        # 步骤6: 修改新零售价
        with allure.step("步骤6: 修改新零售价"):
            print("\n步骤6: 修改新零售价")
            self.price_change_page.modify_retail_price(new_price)
            time.sleep(1)

        # 步骤7: 保存并审核
        with allure.step("步骤7: 保存并审核"):
            print("\n步骤7: 保存并审核")
            bill_no = self.price_change_page.save_and_audit()

            success_msg = self.price_change_page.get_success_message(timeout=5000)
            print(f"审核提示: {success_msg}")

            if not success_msg:
                error_msg = self.price_change_page.get_error_message(timeout=2000)
                if error_msg:
                    print(f"审核失败错误: {error_msg}")

        # 步骤8: 返回列表并获取单号
        with allure.step("步骤8: 返回列表并获取单号"):
            print("\n步骤8: 返回列表并获取单号")
            # 先关闭可能存在的提示弹窗
            self.price_change_page.close_blocking_modals()

            # 返回列表
            self.price_change_page.back_to_list()
            time.sleep(2)

            # 从列表获取单号
            if not bill_no:
                bill_no = self.price_change_page.get_first_bill_number_from_list()
            assert bill_no, "未能获取到单号"
            print(f"获取到单号: {bill_no}")

        # 步骤9: 按单号查询验证
        with allure.step("步骤9: 按单号查询验证"):
            print("\n步骤9: 按单号查询验证")
            self.price_change_page.search_by_bill_number(bill_no)
            time.sleep(2)

            assert self.price_change_page.is_bill_exists(bill_no), (
                f"单号未在列表中找到: {bill_no}"
            )
            print(f"查询成功，单号: {bill_no}")
