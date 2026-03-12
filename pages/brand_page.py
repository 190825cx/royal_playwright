"""
品牌管理页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/archives/ItemBrand
功能: 新增品牌、填写必填项、保存、查询、导出、删除
"""

import time
from typing import List
from playwright.sync_api import Page
from pages.base_page import BasePage


class BrandPage(BasePage):
    """品牌管理页面 Page Object"""

    BRAND_PATH = "/archives/ItemBrandList"

    def __init__(self, page: Page, base_url: str = "https://royal-pre.cs.kemai.com.cn"):
        super().__init__(page)
        self.base_url = base_url.rstrip("/")

        # ============ 工具栏按钮 ============
        self.locator_add_btn = self.page.get_by_role("button", name="新增").first
        self.locator_delete_btn = self.page.get_by_role("button", name="删除").first
        self.locator_search_btn = self.page.get_by_role("button", name="查询").first
        self.locator_reset_btn = self.page.get_by_role("button", name="重置").first
        self.locator_export_btn = self.page.get_by_role("button", name="导出").first

        # ============ 查询字段 ============
        self.locator_search_input = self.page.get_by_role("textbox", name="名称").first

        # ============ 新增面板 ============
        self.locator_add_panel = self.page.locator(
            "[class*='drawer'], [class*='k-drawer']"
        ).last
        # 新增面板中的品牌名称输入框
        self.locator_brand_name_input = self.page.locator(
            "input.ivu-input"
        ).last
        # 新增面板保存按钮
        self.locator_save_btn = self.page.get_by_role("button", name="保存").first

        # ============ 表格 ============
        self.locator_table = self.page.locator(".ivu-table-wrapper").first
        self.locator_table_rows = self.page.locator(".ivu-table-tbody tr")

        # ============ 提示信息 ============
        self.locator_success_message = self.page.locator(".ivu-message-success")
        self.locator_error_message = self.page.locator(".ivu-message-error")
        self.locator_form_errors = self.page.locator(".ivu-form-item-error-tip")

        # ============ 确认弹窗 ============
        self.locator_confirm_ok_btn = (
            self.page.locator('.ivu-modal-confirm-footer .ivu-btn-primary')
            .or_(self.page.locator('.ivu-modal-footer .ivu-btn-primary:has-text("确定")'))
            .or_(self.page.locator('.ivu-btn-primary:has-text("确定")'))
        )

    # ------------------------------------------
    # 导航
    # ------------------------------------------
    def navigate_to_brand(self) -> None:
        """直接导航到品牌管理页面"""
        self.page.goto(self.base_url + self.BRAND_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

    def navigate_via_menu(self) -> None:
        """通过左侧菜单导航到品牌管理页面"""
        print(f"正在通过菜单导航，当前URL: {self.page.url}")

        try:
            # 点击"档案"tab
            archive_tab = self.page.get_by_role("tab", name="档案")
            archive_tab.wait_for(state="visible", timeout=10000)
            archive_tab.click()
            time.sleep(1)
            print("已点击'档案'tab")

            # 点击"品牌管理"菜单项
            brand_menu = self.page.get_by_text("品牌管理")
            brand_menu.wait_for(state="visible", timeout=10000)
            brand_menu.click()
            time.sleep(2)

            print(f"菜单导航成功，当前URL: {self.page.url}")

            # 等待主表格加载
            try:
                self.locator_table.wait_for(state="visible", timeout=10000)
                spinner = self.page.locator(".ivu-spin-fix:visible").first
                if spinner.count() > 0:
                    spinner.wait_for(state="hidden", timeout=10000)
            except:
                pass
        except Exception as e:
            print(f"菜单导航过程中出错: {e}，尝试直接跳转")
            self.navigate_to_brand()

    def is_on_brand_page(self, timeout: int = 10000) -> bool:
        """检查是否在品牌管理页面"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if "ItemBrand" in self.page.url:
                    return True
                time.sleep(0.5)
            return False
        except Exception:
            return False

    # ------------------------------------------
    # 新增品牌
    # ------------------------------------------
    def click_add(self) -> None:
        """点击新增按钮（先关闭可能拦截的弹窗）"""
        print("点击'新增'按钮")
        # 关闭可能遮挡的弹窗
        try:
            modal = self.page.locator(".ivu-modal-wrap:visible").first
            if modal.is_visible(timeout=1000):
                self.page.keyboard.press("Escape")
                time.sleep(0.5)
        except:
            pass
        self.locator_add_btn.wait_for(state="visible", timeout=10000)
        self.locator_add_btn.click()
        time.sleep(1)

    def fill_brand_name(self, name: str) -> None:
        """填写品牌名称（新增面板中，modal内第2个input）"""
        try:
            modal = self.page.locator('.ivu-modal-wrap:visible').last
            inp = modal.locator('input.ivu-input').nth(1)
            inp.wait_for(state='visible', timeout=8000)
            inp.click()
            inp.fill(name)
            print(f"填写品牌名称: {name}")
        except Exception as e:
            print(f"填写品牌名称失败: {e}")

    def save_brand(self) -> None:
        """点击保存按钮并等待结果"""
        print("点击'保存'按钮")
        save_btn = self.page.get_by_role("button", name="保存").first
        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.click()
        print("保存按钮已点击，等待结果...")
        time.sleep(2)

    # ------------------------------------------
    # 查询
    # ------------------------------------------
    def fill_search_input(self, text: str) -> None:
        """填写查询条件（工具栏搜索框）"""
        try:
            # 工具栏搜索框，placeholder="名称"
            search_box = self.page.get_by_placeholder("名称").first
            search_box.wait_for(state="visible", timeout=10000)
            search_box.click()
            search_box.clear()
            search_box.fill(text)
            print(f"填写查询条件: {text}")
        except Exception as e:
            print(f"填写查询条件失败: {e}")

    def click_search(self) -> None:
        """点击查询按钮"""
        self.locator_search_btn.wait_for(state="visible", timeout=5000)
        self.locator_search_btn.click()
        self.wait_for_spinner_hidden(timeout=10000)
        time.sleep(2)

    def search_brand(self, keyword: str) -> None:
        """根据关键词查询品牌"""
        print(f"查询品牌，关键词: {keyword}")
        try:
            self.page.goto(self.base_url + self.BRAND_PATH)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)

            self.fill_search_input(keyword)
            self.click_search()
        except Exception as e:
            print(f"查询品牌失败: {e}")

    # ------------------------------------------
    # 导出
    # ------------------------------------------
    def click_export(self) -> None:
        """点击导出按钮"""
        try:
            self.locator_export_btn.wait_for(state="visible", timeout=5000)
            self.locator_export_btn.click()
            print("已点击导出按钮")
            time.sleep(2)
        except Exception as e:
            print(f"导出失败: {e}")

    # ------------------------------------------
    # 删除
    # ------------------------------------------
    def select_first_row(self) -> None:
        """勾选表格第一行"""
        try:
            # 表格中第一个数据行的 checkbox（跳过表头的 checkbox）
            first_row_checkbox = self.page.get_by_role("checkbox").nth(1)
            first_row_checkbox.wait_for(state="visible", timeout=5000)
            first_row_checkbox.click(force=True)
            print("已勾选第一行")
            time.sleep(0.5)
        except Exception as e:
            print(f"勾选第一行失败: {e}")

    def click_delete(self) -> None:
        """点击删除按钮"""
        self.locator_delete_btn.wait_for(state="visible", timeout=5000)
        self.locator_delete_btn.click(force=True)
        print("删除按钮已点击")
        time.sleep(1)

    def confirm_delete(self) -> None:
        """确认删除弹窗"""
        try:
            confirm_btn = self.page.locator('.ivu-modal-wrap:visible .ivu-btn-primary').last
            confirm_btn.wait_for(state='visible', timeout=5000)
            confirm_btn.click()
            print("已确认删除")
            time.sleep(2)
        except Exception as e:
            print(f"确认删除失败: {e}")

    def delete_brand(self) -> None:
        """选中第一行并删除"""
        self.select_first_row()
        self.click_delete()
        self.confirm_delete()

    # ------------------------------------------
    # 组合操作
    # ------------------------------------------
    def add_brand(self, brand_data: dict) -> None:
        """
        新增品牌（填写必填项：品牌编码、品牌名称）
        :param brand_data: 品牌数据字典，支持 code 和 name
        """
        self.click_add()
        time.sleep(1)

        # 填写品牌编码
        if "code" in brand_data:
            self.fill_brand_code(brand_data["code"])

        # 填写品牌名称
        if "name" in brand_data:
            self.fill_brand_name(brand_data["name"])

    def fill_brand_code(self, code: str) -> None:
        """填写品牌编码（新增面板中，modal内第1个input）"""
        try:
            modal = self.page.locator('.ivu-modal-wrap:visible').last
            inp = modal.locator('input.ivu-input').nth(0)
            inp.wait_for(state='visible', timeout=8000)
            inp.click(click_count=3)
            inp.press_sequentially(code, delay=50)
            inp.blur()
            time.sleep(0.2)
            print(f"填写品牌编码: {code}")
        except Exception as e:
            print(f"填写品牌编码失败: {e}")

    # ------------------------------------------
    # 断言辅助
    # ------------------------------------------
    def get_success_message(self, timeout: int = 5000) -> str:
        """获取成功提示信息"""
        locators = [
            self.page.locator(".ivu-message-success"),
            self.page.locator(".ivu-notice-success"),
        ]
        for loc in locators:
            text = self.get_text(loc, timeout=timeout)
            if text:
                return text
        return ""

    def get_error_message(self, timeout: int = 3000) -> str:
        """获取错误提示信息"""
        locators = [
            self.page.locator(".ivu-message-error"),
            self.page.locator(".ivu-notice-error"),
            self.page.locator(".ivu-form-item-error-tip"),
        ]
        for loc in locators:
            text = self.get_text(loc, timeout=500)
            if text:
                return text
        return ""

    def get_form_errors(self) -> List[str]:
        """获取表单校验错误列表"""
        try:
            errors = self.locator_form_errors.all_text_contents()
            return [e.strip() for e in errors if e.strip()]
        except Exception:
            return []

    def is_brand_exists(self, name: str = None, code: str = None) -> bool:
        """
        检查品牌是否存在于列表中
        :param name: 品牌名称
        :param code: 品牌编码
        """
        try:
            self.wait_for_spinner_hidden(timeout=10000)
            time.sleep(1)
            grid_text = self.page.evaluate("""
                () => {
                    const grid = document.querySelector('.km-grid-body-scroll') ||
                                 document.querySelector('.km-grid-body') ||
                                 document.querySelector('.km-grid');
                    return grid ? (grid.innerText || grid.textContent || '') : '';
                }
            """)
            if name and name in grid_text:
                print(f"在表格中找到品牌名称: {name}")
                return True
            if code and code in grid_text:
                print(f"在表格中找到品牌编码: {code}")
                return True
            return False
        except Exception as e:
            print(f"is_brand_exists 异常: {e}")
            return False

    def get_table_row_count(self) -> int:
        """获取表格行数"""
        try:
            self.wait_for_spinner_hidden()
            time.sleep(1)
            return self.locator_table_rows.count()
        except Exception:
            return 0
