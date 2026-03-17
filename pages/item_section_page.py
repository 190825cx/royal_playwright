"""
商品课组管理页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/archives/ItemSectionList
功能: 新增课组、编辑课组、查询课组、删除课组
"""

import time
from typing import List
from playwright.sync_api import Page
from pages.base_page import BasePage


class ItemSectionPage(BasePage):
    """商品课组管理页面 Page Object"""

    SECTION_PATH = "/archives/ItemSectionList"

    def __init__(self, page: Page, base_url: str = "https://royal-pre.cs.kemai.com.cn"):
        super().__init__(page)
        self.base_url = base_url.rstrip("/")

        # ============ 工具栏按钮 ============
        self.locator_add_btn = self.page.get_by_role("button", name="新增").first
        self.locator_delete_btn = self.page.get_by_role("button", name="删除").first
        self.locator_search_btn = self.page.get_by_role("button", name="查询").first
        self.locator_reset_btn = self.page.get_by_role("button", name="重置").first

        # ============ 查询字段 ============
        # placeholder="课组编码/课组名称"
        self.locator_search_input = self.page.get_by_placeholder("课组编码/课组名称")

        # ============ 表格 ============
        self.locator_table_rows = self.page.locator(".ivu-table-tbody tr")

        # ============ 提示信息 ============
        self.locator_success_message = self.page.locator(".ivu-message-success")
        self.locator_error_message = self.page.locator(".ivu-message-error")
        self.locator_form_errors = self.page.locator(".ivu-form-item-error-tip")

    # ------------------------------------------
    # 导航
    # ------------------------------------------
    def navigate_to_section(self) -> None:
        """直接导航到商品课组管理页面"""
        self.page.goto(self.base_url + self.SECTION_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

    def is_on_section_page(self, timeout: int = 10000) -> bool:
        """检查是否在商品课组管理页面"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if "ItemSection" in self.page.url:
                    return True
                time.sleep(0.5)
            return False
        except Exception:
            return False

    # ------------------------------------------
    # 面板内输入框（新增/编辑共用）
    # 面板是 ivu-modal-wrap（无 ivu-modal-hidden 的那个）
    # ------------------------------------------
    def _get_active_modal(self):
        """获取当前可见的弹窗（不含 ivu-modal-hidden）"""
        return self.page.locator(
            ".ivu-modal-wrap:not(.ivu-modal-hidden)"
        ).last

    def _fill_panel_code(self, code: str) -> None:
        """填写面板中的编码字段（modal内第1个 ivu-input）"""
        try:
            modal = self._get_active_modal()
            inp = modal.locator("input.ivu-input").nth(0)
            inp.wait_for(state="visible", timeout=8000)
            inp.click(click_count=3)
            inp.fill(code)
            print(f"填写编码: {code}")
        except Exception as e:
            print(f"填写编码失败: {e}")

    def _fill_panel_name(self, name: str) -> None:
        """填写面板中的名称字段
        新增模式: 编码(nth0)/名称(nth1)/备注(nth2) 都可用，名称=nth(1)
        编辑模式: 编码 disabled，非disabled输入为 名称(nth0)/备注(nth1)，名称=nth(0)
        """
        try:
            modal = self._get_active_modal()
            non_disabled = modal.locator("input.ivu-input:not([disabled])")
            # 编辑模式只有2个非disabled input（名称+备注），新增有3个（编码+名称+备注）
            count = non_disabled.count()
            if count >= 3:
                # 新增模式：名称是第2个
                inp = non_disabled.nth(1)
            else:
                # 编辑模式：名称是第1个
                inp = non_disabled.nth(0)
            inp.wait_for(state="visible", timeout=8000)
            inp.click(click_count=3)
            inp.fill(name)
            print(f"填写名称: {name}")
        except Exception as e:
            print(f"填写名称失败: {e}")

    def _save_panel(self) -> None:
        """点击面板内保存按钮"""
        modal = self._get_active_modal()
        save_btn = modal.get_by_role("button", name="保存")
        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.click()
        print("保存按钮已点击，等待结果...")
        time.sleep(2)

    # ------------------------------------------
    # 新增
    # ------------------------------------------
    def click_add(self) -> None:
        """点击新增按钮"""
        print("点击'新增'按钮")
        self._close_modal_if_visible()
        self.locator_add_btn.wait_for(state="visible", timeout=10000)
        self.locator_add_btn.click()
        time.sleep(1)

    def _close_modal_if_visible(self) -> None:
        """关闭可能遮挡的新增/编辑面板（若已打开则先关闭）"""
        try:
            # 仅当新增/编辑面板已打开时才关闭（点击取消按钮）
            cancel_btn = self.page.locator(
                ".ivu-modal-wrap:not(.ivu-modal-hidden) .ivu-btn:has-text('取消')"
            ).first
            if cancel_btn.is_visible(timeout=1000):
                cancel_btn.click()
                time.sleep(0.5)
        except Exception:
            pass

    def add_item_section(self, data: dict) -> None:
        """新增课组：填写编码、名称后保存"""
        self.click_add()
        time.sleep(1)
        if "code" in data:
            self._fill_panel_code(data["code"])
        if "name" in data:
            self._fill_panel_name(data["name"])
        self._save_panel()

    # ------------------------------------------
    # 查询
    # ------------------------------------------
    def fill_search_input(self, text: str) -> None:
        """填写查询条件（搜索框 placeholder=课组编码/课组名称）"""
        try:
            search_box = self.locator_search_input
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

    def search_section(self, keyword: str) -> None:
        """导航刷新页面后按关键词查询"""
        print(f"查询课组，关键词: {keyword}")
        self.page.goto(self.base_url + self.SECTION_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)
        self.fill_search_input(keyword)
        self.click_search()

    # ------------------------------------------
    # 编辑（行内操作按钮）
    # ------------------------------------------
    def click_first_row_edit(self) -> None:
        """点击第一行操作列的编辑按钮"""
        try:
            edit_btn = self.page.locator(".km-grid-cell-operate").first
            edit_btn.wait_for(state="visible", timeout=5000)
            edit_btn.click()
            print("已点击第一行编辑按钮")
            time.sleep(1)
        except Exception as e:
            print(f"点击编辑按钮失败: {e}")

    def edit_first_row(self, new_data: dict) -> None:
        """编辑第一行课组（点击行内编辑按钮，修改名称，保存）"""
        self.click_first_row_edit()
        if "name" in new_data:
            self._fill_panel_name(new_data["name"])
        self._save_panel()

    # ------------------------------------------
    # 删除
    # ------------------------------------------
    def select_first_row(self) -> None:
        """勾选表格第一行复选框"""
        try:
            # checkbox nth(0) 是全选，nth(1) 是第一行数据
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

    def delete_section(self) -> None:
        """选中第一行并删除"""
        self.select_first_row()
        self.click_delete()
        self.confirm_delete()

    # ------------------------------------------
    # 断言辅助
    # ------------------------------------------
    def get_success_message(self, timeout: int = 5000) -> str:
        """获取成功提示信息"""
        for loc in [
            self.page.locator(".ivu-message-success"),
            self.page.locator(".ivu-notice-success"),
        ]:
            text = self.get_text(loc, timeout=timeout)
            if text:
                return text
        return ""

    def get_error_message(self, timeout: int = 3000) -> str:
        """获取错误提示信息"""
        for loc in [
            self.page.locator(".ivu-message-error"),
            self.page.locator(".ivu-notice-error"),
            self.page.locator(".ivu-form-item-error-tip"),
        ]:
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

    def is_section_exists(self, name: str = None, code: str = None) -> bool:
        """检查课组是否存在于列表中"""
        try:
            self.wait_for_spinner_hidden(timeout=10000)
            time.sleep(1)
            grid_text = self.page.evaluate("""
                () => {
                    const grid = document.querySelector('.km-grid-body-scroll') ||
                                 document.querySelector('.km-grid-body') ||
                                 document.querySelector('.km-grid') ||
                                 document.querySelector('.ivu-table-body');
                    return grid ? (grid.innerText || grid.textContent || '') : '';
                }
            """)
            if name and name in grid_text:
                print(f"在表格中找到课组名称: {name}")
                return True
            if code and code in grid_text:
                print(f"在表格中找到课组编码: {code}")
                return True
            return False
        except Exception as e:
            print(f"is_section_exists 异常: {e}")
            return False

    def get_table_row_count(self) -> int:
        """获取表格行数"""
        try:
            self.wait_for_spinner_hidden()
            time.sleep(1)
            return self.locator_table_rows.count()
        except Exception:
            return 0
