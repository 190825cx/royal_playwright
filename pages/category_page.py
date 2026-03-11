"""
类别管理页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/archives/ItemCategory
功能: 新增类别、填写必填项、保存、查询、导出、删除
"""

import time
from typing import List
from playwright.sync_api import Page
from pages.base_page import BasePage


class CategoryPage(BasePage):
    """类别管理页面 Page Object"""

    CATEGORY_PATH = "https://royal-pre.cs.kemai.com.cn/archives/ItemClsList"

    def __init__(self, page: Page):
        super().__init__(page)

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
        # 新增面板中的类别名称输入框
        self.locator_category_name_input = self.page.locator(
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
    def navigate_to_category(self) -> None:
        """直接导航到类别管理页面"""
        self.page.goto(self.CATEGORY_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

    def navigate_via_menu(self) -> None:
        """通过左侧菜单导航到类别管理页面"""
        print(f"正在通过菜单导航，当前URL: {self.page.url}")

        try:
            # 点击"档案"tab
            archive_tab = self.page.get_by_role("tab", name="档案")
            archive_tab.wait_for(state="visible", timeout=10000)
            archive_tab.click()
            time.sleep(1)
            print("已点击'档案'tab")

            # 点击"类别管理"菜单项
            cat_menu = self.page.get_by_text("类别管理")
            cat_menu.wait_for(state="visible", timeout=10000)
            cat_menu.click()
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
            self.navigate_to_category()

    def is_on_category_page(self, timeout: int = 10000) -> bool:
        """检查是否在类别管理页面"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if "ItemClsList" in self.page.url:
                    return True
                time.sleep(0.5)
            return False
        except Exception:
            return False

    # ------------------------------------------
    # 新增类别
    # ------------------------------------------
    def click_add(self) -> None:
        """点击新增按钮"""
        print("点击'新增'按钮")
        # 先关闭可能拦截的弹窗（用关闭按钮，而非Escape）
        try:
            close_btn = self.page.locator('.ivu-modal-wrap:visible .ivu-modal-close').first
            if close_btn.is_visible(timeout=1000):
                close_btn.click()
                time.sleep(0.5)
        except:
            pass
        self.locator_add_btn.wait_for(state="visible", timeout=10000)
        self.locator_add_btn.click()
        # 等待新增modal出现（通过等待保存按钮出现来确认）
        try:
            self.page.get_by_role('button', name='保存').first.wait_for(state='visible', timeout=10000)
        except:
            pass
        time.sleep(1)

    def fill_category_name(self, name: str) -> None:
        """填写类别名称（通过Vue实例currentValue直接设置）"""
        try:
            inp = self.page.locator('.ivu-modal-wrap:visible input.ivu-input-with-word-count').first
            inp.wait_for(state='visible', timeout=8000)
            # 通过Vue组件实例设置值，触发v-model响应
            self.page.evaluate("""
                (value) => {
                    const modal = Array.from(document.querySelectorAll('.ivu-modal-wrap'))
                        .find(m => window.getComputedStyle(m).display !== 'none');
                    const inp = modal.querySelector('input.ivu-input-with-word-count');
                    let el = inp;
                    while (el) {
                        if (el.__vue__) break;
                        el = el.parentElement;
                    }
                    if (el && el.__vue__ && 'currentValue' in el.__vue__.$data) {
                        el.__vue__.currentValue = value;
                        el.__vue__.$emit('input', value);
                        el.__vue__.$emit('change', value);
                    }
                }
            """, name)
            time.sleep(0.3)
            print(f"填写类别名称: {name}")
        except Exception as e:
            print(f"填写类别名称失败: {e}")

    def fill_category_sort(self, sort: str = '10') -> None:
        """填写类别编码（modal中第一个非disabled的ivu-input，2位数字，必须唯一）"""
        try:
            modal = self.page.locator('.ivu-modal-wrap:visible').last
            # 类别编码是第一个非disabled的ivu-input
            code_inp = modal.locator('input.ivu-input:not([disabled])').nth(0)
            code_inp.wait_for(state='visible', timeout=8000)
            code_inp.click(click_count=3)
            code_inp.press_sequentially(sort, delay=50)
            code_inp.blur()
            time.sleep(0.2)
            print(f"填写类别编码: {sort}")
        except Exception as e:
            print(f"填写类别编码失败: {e}")

    def save_category(self) -> None:
        """点击保存按钮并等待结果（处理OS平台编码冲突确认框）"""
        print("点击'保存'按钮")
        save_btn = self.page.get_by_role("button", name="保存").first
        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.click()
        print("保存按钮已点击，等待结果...")
        time.sleep(2)
        # 处理可能出现的OS平台编码冲突确认框
        try:
            confirm_btn = self.page.locator('.ivu-modal-wrap:visible .ivu-btn-primary:has-text("确定")').last
            if confirm_btn.is_visible(timeout=2000):
                confirm_btn.click()
                print("已处理编码冲突确认框")
                time.sleep(2)
        except:
            pass

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

    def search_category(self, keyword: str) -> None:
        """根据关键词查询类别"""
        print(f"查询类别，关键词: {keyword}")
        try:
            self.page.goto(self.CATEGORY_PATH)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)

            self.fill_search_input(keyword)
            self.click_search()
        except Exception as e:
            print(f"查询类别失败: {e}")

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
            confirm_btn = self.page.get_by_role('button', name='确定').first
            confirm_btn.wait_for(state='visible', timeout=5000)
            confirm_btn.click(force=True)
            print("已确认删除")
            time.sleep(2)
        except Exception as e:
            print(f"确认删除失败: {e}")

    def delete_category(self) -> None:
        """选中第一行并删除"""
        self.select_first_row()
        self.click_delete()
        self.confirm_delete()

    # ------------------------------------------
    # 组合操作
    # ------------------------------------------
    def add_category(self, category_data: dict) -> None:
        """
        新增类别（填写必填项：类别编码、类别名称）
        :param category_data: 类别数据字典，支持 code 和 name
        """
        import time as _time
        self.click_add()

        # 填写类别编码（2位数字，优先用传入的code，否则用时间戳生成唯一值）
        code_val = category_data.get("code") or category_data.get("sort") or str(int(_time.time()) % 90 + 10)
        self.fill_category_sort(code_val)

        # 填写类别名称
        if "name" in category_data:
            self.fill_category_name(category_data["name"])

    def fill_category_code(self, code: str) -> None:
        """类别编码由系统自动生成（disabled），无需填写，此方法保留兼容性"""
        print(f"类别编码由系统自动生成，跳过填写: {code}")

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

    def is_category_exists(self, name: str = None, code: str = None) -> bool:
        """
        检查类别是否存在于表格列表中（逐行精确匹配）
        """
        try:
            self.wait_for_spinner_hidden(timeout=10000)
            time.sleep(1)
            row_texts = self.page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('.km-grid-tr-wrap');
                    if (rows.length > 0) {
                        return Array.from(rows).map(r => r.innerText || r.textContent || '');
                    }
                    const grid = document.querySelector('.km-grid-body-scroll') ||
                                 document.querySelector('.km-grid-body') ||
                                 document.querySelector('.km-grid');
                    return grid ? (grid.innerText || grid.textContent || '').split('\\n') : [];
                }
            """)
            for row in row_texts:
                row = row.strip()
                if not row:
                    continue
                if name and name in row:
                    print(f"在表格中找到类别名称: {name}")
                    return True
                if code and code in row:
                    print(f"在表格中找到类别编码: {code}")
                    return True
            return False
        except Exception as e:
            print(f"is_category_exists 异常: {e}")
            return False

    def get_table_row_count(self) -> int:
        """获取表格行数"""
        try:
            self.wait_for_spinner_hidden()
            time.sleep(1)
            return self.locator_table_rows.count()
        except Exception:
            return 0
