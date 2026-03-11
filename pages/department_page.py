"""
部门档案页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/archives/Department
功能: 新增部门、填写必填项、保存、查询、导出、删除
"""

import time
from typing import List
from playwright.sync_api import Page
from pages.base_page import BasePage


class DepartmentPage(BasePage):
    """部门档案页面 Page Object"""

    DEPARTMENT_PATH = "https://royal-pre.cs.kemai.com.cn/archives/ItemDepartmentList"

    def __init__(self, page: Page):
        super().__init__(page)

        # ============ 左侧菜单 ============
        # 档案菜单 - 精确匹配
        self.locator_archive_menu = (
            page.locator('.ivu-menu-submenu-title:has-text("档案")')
            .filter(has_text='档案')
            .first
        )
        # 部门档案菜单项
        self.locator_department_menu = (
            page.locator('.ivu-menu-item:has-text("部门档案")')
            .first
        )

        # ============ 工具栏按钮 ============
        # 使用button元素和文本定位
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
        # 新增面板中的部门名称输入框
        self.locator_department_name_input = self.page.locator(
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
    def navigate_to_department(self) -> None:
        """直接导航到部门档案页面"""
        self.page.goto(self.DEPARTMENT_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(3)

    def navigate_via_menu(self) -> None:
        """通过左侧菜单导航到部门档案页面"""
        print(f"正在通过菜单导航，当前URL: {self.page.url}")

        try:
            # 点击"档案"tab
            archive_tab = self.page.get_by_role("tab", name="档案")
            archive_tab.wait_for(state="visible", timeout=10000)
            archive_tab.click()
            time.sleep(1)
            print("已点击'档案'tab")

            # 点击"部门档案"菜单项
            dept_menu = self.page.get_by_text("部门档案")
            dept_menu.wait_for(state="visible", timeout=10000)
            dept_menu.click()
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
            self.navigate_to_department()

    def is_on_department_page(self, timeout: int = 10000) -> bool:
        """检查是否在部门档案页面"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if "Department" in self.page.url:
                    return True
                time.sleep(0.5)
            return False
        except Exception:
            return False

    # ------------------------------------------
    # 新增部门
    # ------------------------------------------
    def click_add(self) -> None:
        """点击新增按钮（先关闭可能拦截的弹窗）"""
        print("点击'新增'按钮")

        # 等待页面加载完成
        time.sleep(3)

        # 关闭可能遮挡的弹窗
        try:
            modal = self.page.locator(".ivu-modal-wrap:visible").first
            if modal.is_visible(timeout=1000):
                self.page.keyboard.press("Escape")
                time.sleep(0.5)
        except:
            pass

        # 等待表格加载完成
        try:
            self.locator_table.wait_for(state="visible", timeout=10000)
            spinner = self.page.locator(".ivu-spin-fix:visible").first
            if spinner.count() > 0:
                spinner.wait_for(state="hidden", timeout=10000)
        except:
            pass

        time.sleep(1)

        # 使用 get_by_role 方式查找按钮
        try:
            add_btn = self.page.get_by_role("button", name="新增").first
            add_btn.wait_for(state="visible", timeout=5000)
            add_btn.click(force=True)
            print("   使用 get_by_role 点击新增按钮")
            time.sleep(2)  # 等待新增面板打开
            return
        except Exception as e:
            print(f"   get_by_role 方式失败: {e}")

        # 使用 locator 方式
        try:
            add_btn = self.page.locator("button:has-text('新增')").first
            add_btn.wait_for(state="visible", timeout=5000)
            add_btn.click(force=True)
            print("   使用 locator 点击新增按钮")
            time.sleep(2)
            return
        except Exception as e:
            print(f"   locator 方式失败: {e}")

        # 最后尝试使用 JS 点击页面中包含"新增"文本的元素
        print("   尝试使用 JS 点击...")
        self.page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button, span, div');
                for (const btn of buttons) {
                    if (btn.innerText && btn.innerText.trim() === '新增') {
                        btn.click();
                        return;
                    }
                }
            }
        """)
        time.sleep(2)

    def fill_department_name(self, name: str) -> None:
        """填写部门名称（新增面板中，modal内第2个input）"""
        try:
            modal = self.page.locator('.ivu-modal-wrap:visible').last
            inp = modal.locator('input.ivu-input-with-word-count').nth(1)
            inp.wait_for(state='visible', timeout=8000)
            inp.click(click_count=3)
            inp.press_sequentially(name, delay=50)
            inp.blur()
            time.sleep(0.2)
            print(f"填写部门名称: {name}")
        except Exception as e:
            print(f"填写部门名称失败: {e}")

    def save_department(self) -> None:
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
        """填写查询条件（工具栏搜索框，第一个ivu-input，placeholder为名称/编码）"""
        try:
            search_box = self.page.locator('input.ivu-input').first
            search_box.wait_for(state='visible', timeout=10000)
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

    def search_department(self, keyword: str) -> None:
        """根据关键词查询部门"""
        print(f"查询部门，关键词: {keyword}")
        try:
            self.page.goto(self.DEPARTMENT_PATH)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)

            self.fill_search_input(keyword)
            self.click_search()
        except Exception as e:
            print(f"查询部门失败: {e}")

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
        """确认删除弹窗（ivu-confirm弹窗，确定是footer第二个按钮）"""
        try:
            # 先等待confirm弹窗出现
            confirm_footer = self.page.locator('.ivu-modal-confirm-footer')
            confirm_footer.wait_for(state='visible', timeout=5000)
            # 确定是footer中第二个按钮（第一个是「取消 Esc」）
            confirm_btn = confirm_footer.locator('button').nth(1)
            confirm_btn.wait_for(state='visible', timeout=3000)
            confirm_btn.click(force=True)
            print("已确认删除")
            time.sleep(3)
        except Exception as e:
            print(f"确认删除失败: {e}")

    def delete_department(self) -> None:
        """选中第一行并删除"""
        self.select_first_row()
        self.click_delete()
        self.confirm_delete()

    # ------------------------------------------
    # 组合操作
    # ------------------------------------------
    def add_department(self, department_data: dict) -> None:
        """
        新增部门（填写必填项：商品部门编码、商品部门）
        :param department_data: 部门数据字典，支持 code 和 name
        """
        self.click_add()
        time.sleep(1)

        # 填写商品部门编码（数字）
        if "code" in department_data:
            self.fill_department_code(department_data["code"])

        # 填写商品部门（中文名称）
        if "name" in department_data:
            self.fill_department_name(department_data["name"])

    def fill_department_code(self, code: str) -> None:
        """填写部门编码（新增面板中，modal内第1个input）"""
        try:
            modal = self.page.locator('.ivu-modal-wrap:visible').last
            inp = modal.locator('input.ivu-input-with-word-count').nth(0)
            inp.wait_for(state='visible', timeout=8000)
            inp.click(click_count=3)
            inp.press_sequentially(code, delay=50)
            inp.blur()
            time.sleep(0.2)
            print(f"填写部门编码: {code}")
        except Exception as e:
            print(f"填写部门编码失败: {e}")

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

    def is_department_exists(self, name: str = None, code: str = None) -> bool:
        """
        检查部门是否存在于表格列表中（逐行精确匹配）
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
                    // fallback: split full grid text by newlines
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
                    print(f"在表格中找到部门名称: {name}")
                    return True
                if code and code in row:
                    print(f"在表格中找到部门编码: {code}")
                    return True
            return False
        except Exception as e:
            print(f"is_department_exists 异常: {e}")
            return False

    def get_table_row_count(self) -> int:
        """获取表格行数"""
        try:
            self.wait_for_spinner_hidden()
            time.sleep(1)
            return self.locator_table_rows.count()
        except Exception:
            return 0
