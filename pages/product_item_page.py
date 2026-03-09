"""
商品档案页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/archives/ItemList
功能: 新增商品、填写必填项、保存、审核、查询
"""

import time
from typing import List, Optional
from playwright.sync_api import Page
from pages.base_page import BasePage


class ProductItemPage(BasePage):
    """商品档案页面 Page Object"""

    PRODUCT_ITEM_PATH = "https://royal-pre.cs.kemai.com.cn/archives/ItemList"

    def __init__(self, page: Page):
        super().__init__(page)

        # ============ 导航菜单 ============
        # 左侧导航 - 档案菜单
        self.locator_archive_menu = (
            self.page.locator('.ivu-menu-submenu-title:has-text("档案")')
            .or_(self.page.get_by_text("档案"))
            .first
        )
        # 商品档案菜单项
        self.locator_product_item_menu = (
            self.page.locator('.ivu-menu-item:has-text("商品档案")')
            .or_(self.page.get_by_text("商品档案"))
            .first
        )

        # ============ 工具栏按钮 ============
        # 新增按钮 (主界面的新增)
        self.locator_add_btn = self.page.locator(
            '.ivu-btn-primary:has-text("新增")'
        ).filter(visible=True).first
        # 保存按钮 (表单界面的保存)
        self.locator_save_btn = (
            self.page.locator('.ivu-btn-primary:has-text("保存")')
            .or_(self.page.locator('.ivu-btn-blue:has-text("保存")'))
            .filter(visible=True)
            .first
        )
        # 审核按钮
        self.locator_audit_btn = (
            self.page.locator('.ivu-btn-primary:has-text("审核")')
            .filter(visible=True)
            .first
        )
        # 查询按钮
        self.locator_search_btn = (
            self.page.locator('.ivu-btn-primary:has-text("查询")')
            .filter(visible=True)
            .first
        )
        # 重置按钮
        self.locator_reset_btn = (
            self.page.locator('.ivu-btn-ghost:has-text("重置")')
            .filter(visible=True)
            .first
        )

        # ============ 表单字段 (使用 label 辅助定位) ============
        # 商品编码
        self.locator_product_code = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="商品编码"),
            )
            .locator("input")
            .filter(visible=True)
        )
        # 商品名称
        self.locator_product_name = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="商品名称"),
            )
            .locator("input")
            .filter(visible=True)
        )
        # 条码
        self.locator_barcode = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="国际条码"),
            )
            .locator("input")
            .filter(visible=True)
        )
        # 规格
        self.locator_spec = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="规格"),
            )
            .locator("input")
            .filter(visible=True)
        )
        # 单位
        self.locator_unit = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="库存单位"),
            )
            .locator("input")
            .filter(visible=True)
        )
        # 类别
        self.locator_category = (
            self.page.locator(".ivu-form-item")
            .filter(has=self.page.locator(".ivu-form-item-label", has_text="类别"))
            .locator('.ivu-cascader-rel, .ivu-select-selection, input[type="text"]')
            .first
        )
        # 品牌
        self.locator_brand = (
            self.page.locator(".ivu-form-item")
            .filter(has=self.page.locator(".ivu-form-item-label", has_text="品牌"))
            .locator('.ivu-select-selection, input[type="text"]')
            .first
        )
        # 主供应商
        self.locator_supplier = (
            self.page.locator(".ivu-form-item")
            .filter(has=self.page.locator(".ivu-form-item-label", has_text="主供应商"))
            .locator(".ivu-input, .ivu-select-selection, input")
            .first
        )
        # 存储方式
        self.locator_storage = (
            self.page.locator(".ivu-form-item")
            .filter(has=self.page.locator(".ivu-form-item-label", has_text="存储方式"))
            .locator(".ivu-select-selection, input")
            .first
        )

        # ============ 价格字段 ============
        # 进货价
        self.locator_purchase_price = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="进货价"),
            )
            .locator("input")
            .filter(visible=True)
        )
        # 零售价
        self.locator_retail_price = (
            self.page.locator(
                ".ivu-form-item",
                has=self.page.locator(".ivu-form-item-label", has_text="零售价"),
            )
            .locator("input")
            .filter(visible=True)
        )

        # ============ 查询字段 ============
        # 查询条件 - 商品编码/条码/名称
        self.locator_search_input = self.page.locator(
            'input[placeholder*="商品编码/条码/名称"]'
        ).first

        # ============ 表格 ============
        # 商品列表表格
        self.locator_table = self.page.locator(".ivu-table-wrapper").first
        # 表格行
        self.locator_table_rows = self.page.locator(".ivu-table-tbody tr")

        # ============ 提示信息 ============
        # 成功提示
        self.locator_success_message = self.page.locator(".ivu-message-success")
        # 错误提示
        self.locator_error_message = self.page.locator(".ivu-message-error")
        self.locator_form_errors = self.page.locator(".ivu-form-item-error-tip")
        # 确认对话框
        self.locator_confirm_dialog = self.page.locator(".ivu-modal:visible")
        # 确认对话框中的确定按钮
        self.locator_confirm_ok_btn = self.page.locator(
            '.ivu-modal-footer .ivu-btn-primary:has-text("确定")'
        )

    # ------------------------------------------
    # 导航
    # ------------------------------------------
    def navigate_to_product_item(self) -> None:
        """导航到商品档案页面"""
        self.page.goto(self.PRODUCT_ITEM_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

    def navigate_via_menu(self) -> None:
        """通过左侧菜单导航到商品档案页面"""
        print(f"正在通过菜单导航，当前URL: {self.page.url}")

        # 确保侧边栏菜单是展开的
        try:
            # 查找"档案"菜单
            self.locator_archive_menu.wait_for(state="visible", timeout=10000)
            print("找到'档案'菜单")

            # 点击展开
            self.locator_archive_menu.click()
            time.sleep(1)

            # 点击商品档案菜单项
            print("等待'商品档案'菜单项可见")
            self.locator_product_item_menu.wait_for(state="visible", timeout=5000)
            print("点击'商品档案'菜单项")
            self.locator_product_item_menu.click()

            # 等待一会看是否跳转
            time.sleep(3)

            if self.PRODUCT_ITEM_PATH not in self.page.url:
                print(
                    f"菜单点击后未跳转到预期页面 (当前: {self.page.url})，尝试直接跳转"
                )
                self.navigate_to_product_item()
            else:
                print(f"菜单导航成功，当前URL: {self.page.url}")
                # 即使 URL 对，也可能是在详情页，尝试刷新一下
                if not self.locator_add_btn.is_visible(timeout=2000):
                    print("主界面按钮不可见，强制 reload 页面")
                    self.page.reload()
                    self.page.wait_for_load_state("networkidle")
                    time.sleep(2)

                # 等待主表格加载
                try:
                    self.locator_table.wait_for(state="visible", timeout=10000)
                    # 等待 loading 消失
                    spinner = self.page.locator(".ivu-spin-fix:visible").first
                    if spinner.count() > 0:
                        spinner.wait_for(state="hidden", timeout=10000)
                except:
                    pass

        except Exception as e:
            print(f"菜单导航过程中出错: {e}，尝试直接跳转")
            self.navigate_to_product_item()

    # ------------------------------------------
    # 新增商品
    # ------------------------------------------
    def is_on_product_item_page(self, timeout: int = 10000) -> bool:
        """检查是否在商品档案页面"""
        try:
            # 等待 URL 包含路径，或者新增按钮可见
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if self.PRODUCT_ITEM_PATH in self.page.url:
                    return True
                if self.locator_add_btn.is_visible():
                    return True
                time.sleep(0.5)
            return False
        except Exception:
            return False

    def get_success_message(self, timeout: int = 5000) -> str:
        """获取成功提示信息"""
        locators = [
            self.page.locator(".ivu-message-success"),
            self.page.locator(".ivu-notice-success"),
            self.page.locator(".ivu-message-custom-content.ivu-message-success"),
        ]
        for loc in locators:
            text = self.get_text(loc, timeout=500)
            if text: return text
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
            if text: return text
        return ""

    def is_product_exists(self, code: str = None, name: str = None) -> bool:
        """
        检查商品是否存在于列表中
        :param code: 商品编码
        :param name: 商品名称
        :return: 是否存在
        """
        try:
            # 等待 loading 消失
            self.wait_for_spinner_hidden(timeout=10000)
            time.sleep(2)
            # 先检查整个页面文本（最可靠）
            page_text = self.page.evaluate("() => document.body.innerText")
            if code and code in page_text:
                print(f"在页面文本中找到商品编码: {code}")
                return True
            if name and name in page_text:
                print(f"在页面文本中找到商品名称: {name}")
                return True
            # 打印调试信息
            print(f"页面文本片段(前500字符): {page_text[:500]}")
            # 用 evaluate 读取表格真实数据行
            table_text = self.page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('.ivu-table-tbody tr');
                    const texts = [];
                    rows.forEach(row => {
                        const text = row.innerText || row.textContent || '';
                        if (!text.includes('td_placeholder') && text.trim()) {
                            texts.push(text.trim());
                        }
                    });
                    return texts;
                }
            """)
            print(f"表格真实数据行共 {len(table_text)} 行")
            for text in table_text:
                print(f"  行内容: {text[:80]}")
                if code and code in text:
                    return True
                if name and name in text:
                    return True
            return False
        except Exception as e:
            print(f"is_product_exists 异常: {e}")
            return False

    def click_add(self) -> None:
        """点击新增按钮"""
        print("点击'新增'按钮")
        self.wait_and_click(self.locator_add_btn)
        # 等待表单加载
        time.sleep(3)

    def fill_product_code(self, code: str) -> None:
        """填写商品编码"""
        try:
            # 等待元素可见
            self.locator_product_code.first.wait_for(state="visible", timeout=5000)
            # 检查是否禁用
            if self.locator_product_code.first.is_editable():
                self.wait_and_fill(self.locator_product_code, code)
                print(f"填写商品编码: {code}")
            else:
                print("商品编码字段处于禁用状态，跳过填写（可能是自动生成）")
        except Exception as e:
            print(f"填写商品编码失败: {e}")

    def fill_product_name(self, name: str) -> None:
        """填写商品名称"""
        self.wait_and_fill(self.locator_product_name, name)
        print(f"填写商品名称: {name}")

    def fill_barcode(self, barcode: str) -> None:
        """填写条码"""
        try:
            self.locator_barcode.first.wait_for(state="visible", timeout=5000)
            if self.locator_barcode.first.is_editable():
                self.wait_and_fill(self.locator_barcode, barcode)
                print(f"填写条码: {barcode}")
        except Exception:
            pass

    def fill_spec(self, spec: str) -> None:
        """填写规格"""
        try:
            self.wait_and_fill(self.locator_spec, spec)
            print(f"填写规格: {spec}")
        except Exception:
            pass

    def fill_unit(self, unit: str) -> None:
        """填写单位"""
        try:
            self.locator_unit.first.wait_for(state="visible", timeout=5000)
            self.locator_unit.first.focus()
            self.locator_unit.first.click()
            time.sleep(0.3)
            # 先清除再填写
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            self.page.keyboard.type(unit)
            time.sleep(1)
            
            # 尝试点击出现的下拉项
            try:
                # iView 下拉项通常在 body 底部
                dropdown_item = self.page.locator(".ivu-select-dropdown:visible .ivu-select-item").filter(has_text=unit).first
                if dropdown_item.count() == 0:
                    dropdown_item = self.page.locator(".ivu-select-dropdown:visible .ivu-select-item").first
                
                if dropdown_item.count() > 0 and dropdown_item.is_visible():
                    print(f"点击单位下拉项: {dropdown_item.text_content().strip()}")
                    dropdown_item.click(force=True)
                else:
                    self.page.keyboard.press("Enter")
            except:
                self.page.keyboard.press("Enter")

            print(f"填写单位: {unit}")
            time.sleep(0.5)
        except Exception as e:
            print(f"填写单位失败: {e}")

    def fill_storage_method(self, storage: str = "常温") -> None:
        """选择存储方式 - 下拉框选择，默认选择常温"""
        try:
            print(f"尝试选择存储方式: {storage}")

            # 先按 Escape 关闭可能存在的弹窗
            try:
                self.page.keyboard.press("Escape")
                time.sleep(0.3)
            except:
                pass

            # 查找可见的存储方式 label
            storage_labels = (
                self.page.locator(".ivu-form-item-label")
                .filter(has_text="存储方式")
                .all()
            )
            visible_label = None
            for label in storage_labels:
                if label.is_visible():
                    visible_label = label
                    break

            if not visible_label:
                print("存储方式字段不可见，跳过（可能不是必填项）")
                return

            # 找到对应的 form-item
            storage_form_item = visible_label.locator(
                'xpath=ancestor::div[contains(@class, "ivu-form-item")]'
            ).first
            storage_form_item.scroll_into_view_if_needed()
            time.sleep(0.5)

            # 点击下拉框 - 使用 force=True
            clickable = storage_form_item.locator(".ivu-select-selection, .ivu-select, .ivu-input").first
            if not clickable.is_visible():
                print("存储方式点击元素不可见，尝试点击 form-item 区域")
                storage_form_item.click(force=True)
            else:
                clickable.click(force=True)
            time.sleep(1.5)

            # 等待下拉框出现
            try:
                # iView Select 默认生成的下拉框可能不在 form-item 内，而是在 body 底部
                dropdown = self.page.locator(".ivu-select-dropdown:visible").last
                dropdown.wait_for(state="visible", timeout=3000)

                # 优先选择指定的存储方式（如常温）
                if storage:
                    target_option = dropdown.locator(f'.ivu-select-item:has-text("{storage}")').first
                    if target_option.count() > 0 and target_option.is_visible():
                        print(f"选择存储方式: {storage}")
                        target_option.click(force=True)
                        time.sleep(0.5)
                        return

                # 如果没找到指定选项，选择第一个
                first_option = dropdown.locator(".ivu-select-item").first
                if first_option.count() > 0:
                    print(f"选择存储方式(第一个)")
                    first_option.click(force=True)
                else:
                    print("未找到存储方式下拉选项")
            except Exception as e:
                print(f"存储方式下拉框未正常显示: {e}")
                # 最后的尝试：直接键盘向下选择
                self.page.keyboard.press("ArrowDown")
                self.page.keyboard.press("Enter")

        except Exception as e:
            print(f"选择存储方式失败: {e}")

    def fill_category(self, category: str = None) -> None:
        """填写/选择类别 - 点击 pick 图标弹出选择器，选择第一个"""
        try:
            print("尝试选择类别...")

            # 查找可见的类别 label
            category_labels = (
                self.page.locator(".ivu-form-item-label").filter(has_text="类别").all()
            )
            visible_label = None
            for label in category_labels:
                if label.is_visible():
                    visible_label = label
                    break

            if not visible_label:
                print("类别字段不可见，跳过")
                return

            # 找到对应的 form-item
            category_form_item = visible_label.locator(
                'xpath=ancestor::div[contains(@class, "ivu-form-item")]'
            ).first
            category_form_item.scroll_into_view_if_needed()
            time.sleep(0.5)

            # 点击 pick 图标 (km-more) 触发弹窗
            pick_icon = category_form_item.locator(".km-more, i.km").first
            if pick_icon.count() > 0 and pick_icon.is_visible():
                print("点击类别 pick 图标")
                pick_icon.click()
            else:
                # 备选：点击输入框
                print("未找到 pick 图标，点击输入框")
                clickable = category_form_item.locator("input").first
                clickable.click()
            time.sleep(1)

            # 等待 pick 弹窗出现
            pick_modal = self.page.locator(
                ".ivu-modal-wrap:visible .ivu-modal-content"
            ).first
            try:
                pick_modal.wait_for(state="visible", timeout=3000)
                print("检测到类别 pick 弹窗")

                # 等待表格加载完成（等待 loading 消失）
                try:
                    modal_spinner = self.page.locator(".ivu-modal-wrap:visible .ivu-spin-fix:visible")
                    if modal_spinner.count() > 0:
                        modal_spinner.wait_for(state="hidden", timeout=5000)
                except:
                    pass
                time.sleep(1)

                # 如果提供了搜索值且目前没数据，尝试在弹窗中搜索
                if category:
                    modal_search_input = self.page.locator('.ivu-modal-wrap:visible input[placeholder*="搜索"], .ivu-modal-wrap:visible input[placeholder*="名称"]').first
                    if modal_search_input.count() > 0 and modal_search_input.is_visible():
                        print(f"在弹窗中搜索类别: {category}")
                        modal_search_input.fill(category)
                        self.page.keyboard.press("Enter")
                        # 尝试点击弹窗内的“查询”按钮
                        search_btn = self.page.locator('.ivu-modal-wrap:visible button.ivu-btn-primary:has-text("查询")').first
                        if search_btn.count() > 0 and search_btn.is_visible():
                            search_btn.click()
                        time.sleep(2)
                
                # 等待表格有数据
                table_rows = self.page.locator(".ivu-modal-wrap:visible .ivu-table-tbody tr")
                
                # 如果没数据，尝试清除搜索并重新等待
                if table_rows.count() == 0:
                    print("无数据，尝试清除搜索并展示所有...")
                    modal_search_input = self.page.locator('.ivu-modal-wrap:visible input[placeholder*="搜索"], .ivu-modal-wrap:visible input[placeholder*="名称"]').first
                    if modal_search_input.count() > 0:
                        modal_search_input.fill("")
                        self.page.keyboard.press("Enter")
                    time.sleep(2)
                
                # 如果还是没数据，尝试在该弹窗内点击树形节点 (如果存在)
                if table_rows.count() == 0:
                    first_tree_node = self.page.locator(".ivu-modal-wrap:visible .ivu-tree-title").first
                    if first_tree_node.count() > 0:
                        print("表格无数据，尝试点击树节点")
                        first_tree_node.click(force=True)
                        time.sleep(0.5)

                # 点击第一行
                if table_rows.first.count() > 0:
                    print("点击表格第一行...")
                    table_rows.first.click(force=True)
                    time.sleep(0.5)

                # 点击确定按钮
                confirm_btn = self.page.locator('.ivu-modal-wrap:visible button.ivu-btn-primary:has-text("确定")').first
                if confirm_btn.count() > 0 and confirm_btn.is_visible():
                    print("点击确定按钮...")
                    confirm_btn.click(force=True)
                    time.sleep(1)
                    return
            except Exception as e:
                print(f"处理类别弹窗异常: {e}")

            # 尝试2: 树形弹窗
            tree_node = self.page.locator(".ivu-tree-title:visible").first
            if tree_node.count() > 0:
                print(f"检测到树形选择，点击第一个节点")
                tree_node.click(force=True)
                return

            # 尝试3: 下拉选择
            dropdown_item = self.page.locator(
                ".ivu-select-dropdown:visible .ivu-select-item"
            ).first
            if dropdown_item.count() > 0:
                dropdown_item.click(force=True)
                return

            print("类别选择操作完成")
        except Exception as e:
            print(f"选择类别失败: {e}")

    def fill_brand(self, brand: str) -> None:
        """填写/选择品牌 - 点击 pick 图标弹出选择器，选择第一个"""
        try:
            print(f"尝试选择品牌: {brand}")

            # 等待页面加载完成
            try:
                spinner = self.page.locator(
                    ".ivu-spin-fix:visible, .ivu-spin-show-text:visible"
                )
                spinner.wait_for(state="hidden", timeout=10000)
            except:
                pass
            time.sleep(0.5)

            # 查找可见的品牌 label
            brand_labels = (
                self.page.locator(".ivu-form-item-label").filter(has_text="品牌").all()
            )
            visible_label = None
            for label in brand_labels:
                if label.is_visible():
                    visible_label = label
                    break

            if not visible_label:
                print("品牌字段不可见，跳过")
                return

            # 找到对应的 form-item
            brand_form_item = visible_label.locator(
                'xpath=ancestor::div[contains(@class, "ivu-form-item")]'
            ).first
            brand_form_item.scroll_into_view_if_needed()
            time.sleep(0.5)

            # 尝试点击 pick 图标 (km-more) 触发弹窗
            pick_icon = brand_form_item.locator(".km-more, i.km").first
            if pick_icon.count() > 0 and pick_icon.is_visible():
                print("点击品牌 pick 图标")
                pick_icon.click(force=True)
                time.sleep(1)

                # 等待 pick 弹窗出现
                pick_modal = self.page.locator(
                    ".ivu-modal-wrap:visible .ivu-modal-content"
                ).first
                try:
                    pick_modal.wait_for(state="visible", timeout=3000)
                    print("检测到品牌 pick 弹窗")

                    # 等待表格加载
                    time.sleep(1)

                    if brand:
                        modal_search_input = self.page.locator('.ivu-modal-wrap:visible input[placeholder*="搜索"], .ivu-modal-wrap:visible input[placeholder*="名称"]').first
                        if modal_search_input.count() > 0 and modal_search_input.is_visible():
                            print(f"在弹窗中搜索品牌: {brand}")
                            modal_search_input.fill(brand)
                            self.page.keyboard.press("Enter")
                            time.sleep(1.5)

                    # 点击第一行
                    table_rows = self.page.locator(".ivu-modal-wrap:visible .ivu-table-tbody tr")
                    if table_rows.first.count() > 0:
                        print("点击第一行...")
                        table_rows.first.click(force=True)
                        time.sleep(0.5)

                    # 点击确定按钮
                    confirm_btn = self.page.locator('.ivu-modal-wrap:visible .ivu-btn-primary:has-text("确定")').first
                    if confirm_btn.count() > 0:
                        confirm_btn.click(force=True)
                        time.sleep(1)
                        print("品牌选择完成")
                        return
                except Exception as e:
                    print(f"处理品牌弹窗异常: {e}")
            else:
                # 备选：点击输入框，尝试下拉选择
                print("未找到品牌 pick 图标，尝试下拉选择")
                clickable = brand_form_item.locator(
                    ".ivu-select-selection, .ivu-input, input"
                ).first
                clickable.click(force=True)
                time.sleep(1)

                if brand:
                    self.page.keyboard.type(brand)
                    time.sleep(1)
                    self.page.keyboard.press("Enter")
                    time.sleep(0.5)

                # 选择第一个下拉项
                first_option = self.page.locator(
                    ".ivu-select-dropdown:visible .ivu-select-item"
                ).first
                if first_option.count() > 0:
                    print("选择品牌下拉项")
                    first_option.click(force=True)
                    time.sleep(0.5)
                else:
                    print("未找到品牌下拉选项")

            print("品牌选择完成")
        except Exception as e:
            print(f"选择品牌失败: {e}")

    def fill_supplier(self, supplier: str = None) -> None:
        """填写/选择主供应商 - 点击 pick 图标弹出选择器，选择第一个"""
        try:
            print("尝试选择主供应商...")

            # 等待页面加载完成（等待 loading spinner 消失）
            try:
                spinner = self.page.locator(
                    ".ivu-spin-fix:visible, .ivu-spin-show-text:visible"
                )
                spinner.wait_for(state="hidden", timeout=10000)
            except:
                pass
            time.sleep(0.5)

            # 查找可见的主供应商 label
            supplier_labels = (
                self.page.locator(".ivu-form-item-label")
                .filter(has_text="主供应商")
                .all()
            )
            visible_label = None
            for label in supplier_labels:
                if label.is_visible():
                    visible_label = label
                    break

            if not visible_label:
                print("主供应商字段不可见，跳过")
                return

            # 找到对应的 form-item
            supplier_form_item = visible_label.locator(
                'xpath=ancestor::div[contains(@class, "ivu-form-item")]'
            ).first
            supplier_form_item.scroll_into_view_if_needed()
            time.sleep(0.5)

            # 点击 pick 图标 (km-more) 触发弹窗
            pick_icon = supplier_form_item.locator(".km-more, i.km").first
            if pick_icon.count() > 0 and pick_icon.is_visible():
                print("点击主供应商 pick 图标")
                pick_icon.click(force=True)
            else:
                # 备选：点击输入框
                print("未找到 pick 图标，点击输入框")
                clickable = supplier_form_item.locator("input").first
                clickable.click(force=True)
            time.sleep(1)

            # 等待 pick 弹窗出现
            pick_modal = self.page.locator(
                ".ivu-modal-wrap:visible .ivu-modal-content"
            ).first
            try:
                pick_modal.wait_for(state="visible", timeout=3000)
                print("检测到主供应商 pick 弹窗")

                # 如果提供了搜索值，在弹窗中搜索
                if supplier:
                    modal_search_input = self.page.locator('.ivu-modal-wrap:visible input[placeholder*="搜索"], .ivu-modal-wrap:visible input[placeholder*="名称"]').first
                    if modal_search_input.count() > 0 and modal_search_input.is_visible():
                        print(f"在弹窗中搜索供应商: {supplier}")
                        modal_search_input.fill(supplier)
                        self.page.keyboard.press("Enter")
                        time.sleep(1.5)

                # 点击第一行
                table_rows = self.page.locator(".ivu-modal-wrap:visible .ivu-table-tbody tr")
                if table_rows.first.count() > 0:
                    print("点击第一行...")
                    table_rows.first.click(force=True)
                    time.sleep(0.5)

                # 点击确定按钮
                confirm_btn = self.page.locator('.ivu-modal-wrap:visible .ivu-btn-primary:has-text("确定")').first
                if confirm_btn.count() > 0:
                    confirm_btn.click(force=True)
                    time.sleep(1)
                    return

            except Exception as e:
                # 如果没有弹出 pick 弹窗，尝试下拉选择
                print(f"处理主供应商弹窗异常: {e}")
                first_option = self.page.locator(
                    ".ivu-select-dropdown:visible .ivu-select-item"
                ).first
                if first_option.count() > 0:
                    first_option.click(force=True)

            print("主供应商选择操作完成")
        except Exception as e:
            print(f"选择主供应商失败: {e}")

    def fill_purchase_price(self, price: str) -> None:
        """填写进货价"""
        try:
            self.locator_purchase_price.first.wait_for(state="visible", timeout=5000)
            self.locator_purchase_price.first.fill(price)
            print(f"填写进货价: {price}")
        except Exception:
            pass

    def fill_retail_price(self, price: str) -> None:
        """填写零售价"""
        try:
            self.locator_retail_price.first.wait_for(state="visible", timeout=5000)
            self.locator_retail_price.first.fill(price)
            print(f"填写零售价: {price}")
        except Exception:
            pass

    # ------------------------------------------
    # 保存和审核
    # ------------------------------------------
    def click_save(self) -> None:
        """点击保存按钮"""
        print(f"正在尝试点击保存按钮")
        # 直接使用公共的关闭模型方法
        self.close_current_modal()
        
        self.wait_and_click(self.locator_save_btn, force=True)
        print("保存按钮已点击")
        time.sleep(1)

    def click_audit(self) -> None:
        """点击审核按钮"""
        self.wait_and_click(self.locator_audit_btn, force=True)
        time.sleep(1)

    def click_confirm(self) -> None:
        """点击确认对话框中的确定按钮"""
        self.locator_confirm_ok_btn.first.click(force=True)
        time.sleep(1)

    # ------------------------------------------
    # 查询
    # ------------------------------------------
    def fill_search_input(self, text: str) -> None:
        """填写查询条件 - 商品编码/条码/名称"""
        try:
            self.wait_and_fill(self.locator_search_input, text, timeout=10000)
        except Exception as e:
            print(f"填写查询条件失败: {e}")

    def click_search(self) -> None:
        """点击查询按钮"""
        self.wait_and_click(self.locator_search_btn)
        time.sleep(2)

    def close_modal(self) -> None:
        """关闭当前可见的弹窗或详情页"""
        self.close_current_modal()

    def click_reset(self) -> None:
        """点击重置按钮，如果不可见尝试先关闭弹窗或重新导航"""
        try:
            # 确保没有加载遮罩
            self.wait_for_spinner_hidden()

            # 等待重置按钮，如果 3 秒内没出现，尝试关闭弹窗
            if not self.locator_reset_btn.is_visible(timeout=3000):
                print("重置按钮不可见，尝试关闭可能存在的详情弹窗...")
                self.close_modal()
                time.sleep(1)
            
            # 如果还是不见，尝试重新通过菜单导航（兜底方案）
            if not self.locator_reset_btn.is_visible(timeout=2000):
                print("重置按钮仍不可见，尝试重新导航到列表页...")
                self.navigate_via_menu()
                time.sleep(1)

            # 如果还是不见，最后的兜底：强制刷新页面
            if not self.locator_reset_btn.is_visible(timeout=2000):
                print("重置按钮还是不见，最后的尝试: Reload")
                self.page.reload()
                self.page.wait_for_load_state("networkidle")
                time.sleep(3)

            # 再次等待并点击
            self.locator_reset_btn.wait_for(state="visible", timeout=10000)
            self.locator_reset_btn.click(force=True)
            time.sleep(1)
        except Exception as e:
            print(f"点击重置按钮失败: {e}")
            # 如果失败了，尝试直接清空输入框 (如果有)
            try:
                self.locator_search_input.wait_for(state="visible", timeout=2000)
                self.locator_search_input.fill("")
            except:
                pass

    # ------------------------------------------
    # 组合操作
    # ------------------------------------------
    def add_product(self, product_data: dict) -> None:
        """
        新增商品（填写必填项）
        :param product_data: 商品数据字典
        """
        self.click_add()
        time.sleep(3)  # 等待弹窗完全加载

        # 填写必填项
        if "code" in product_data:
            self.fill_product_code(product_data["code"])
        if "name" in product_data:
            self.fill_product_name(product_data["name"])
        if "barcode" in product_data:
            self.fill_barcode(product_data["barcode"])

        # 规格
        if "spec" in product_data:
            self.fill_spec(product_data["spec"])

        # 类别（输入后按回车会返回类别）
        self.fill_category(product_data.get("category"))

        # 存储方式
        self.fill_storage_method(product_data.get("storage", ""))

        # 品牌（输入后按回车会返回品牌）
        if "brand" in product_data:
            self.fill_brand(product_data["brand"])

        # 主供应商（输入后按回车会返回主供应商）
        if "supplier" in product_data:
            self.fill_supplier(product_data.get("supplier", ""))

        # 库存单位
        if "unit" in product_data:
            self.fill_unit(product_data["unit"])

        # 价格
        if "purchase_price" in product_data:
            self.fill_purchase_price(product_data["purchase_price"])
        if "retail_price" in product_data:
            self.fill_retail_price(product_data["retail_price"])

        # 补充：尝试点击一下表单空白处，触发校验或确保输入生效
        try:
            # 点击表单标题或空白区域
            self.page.locator(".ivu-modal-header, .ivu-form").first.click(
                position={"x": 10, "y": 10}
            )
        except:
            pass
        time.sleep(1)

        # 打印当前表单状态（可选，用于调试）
        try:
            errors = self.get_form_errors()
            if errors:
                print(f"当前表单存在校验错误: {errors}")
        except:
            pass

    def _handle_confirm_dialog(self, dialog_name: str = "确认", timeout: int = 10000) -> bool:
        """
        统一处理 iView 的确认弹窗
        :param dialog_name: 弹窗名称（仅用于日志）
        :param timeout: 等待超时时间
        :return: 是否处理成功
        """
        print(f"等待 {dialog_name} 确认弹窗...")
        # 综合多种可能的 iView 弹窗确定按钮定位方式
        confirm_btn = self.page.locator('.ivu-modal-confirm-footer .ivu-btn-primary') \
            .or_(self.page.locator('.ivu-modal-footer .ivu-btn-primary')) \
            .or_(self.page.locator('.ivu-modal-wrap:visible .ivu-btn-primary:has-text("确定")')) \
            .or_(self.page.locator('.ivu-btn-primary:has-text("确定")')) \
            .filter(visible=True).last
        
        try:
            if confirm_btn.is_visible(timeout=timeout):
                btn_text = confirm_btn.text_content().strip()
                print(f"检测到 {dialog_name} 弹窗，点击按钮: {btn_text}")
                try:
                    confirm_btn.click(timeout=3000)
                except:
                    confirm_btn.click(force=True)
                # 等待所有弹窗消失，避免遮挡后续操作
                try:
                    self.page.locator('.ivu-modal-wrap:visible').wait_for(state='hidden', timeout=5000)
                except Exception:
                    # 弹窗未消失时强制按 Escape
                    self.page.keyboard.press('Escape')
                    time.sleep(0.5)
                time.sleep(0.5)
                return True
            else:
                print(f"未在 {timeout}ms 内检测到 {dialog_name} 确认弹窗")
                return False
        except Exception as e:
            print(f"处理 {dialog_name} 弹窗时发生异常: {e}")
            return False

    def save_product(self) -> None:
        """保存商品并等待操作完成，处理保存后的审核确认弹框"""
        self.click_save()
        print("等待保存操作完成...")
        
        # 处理保存后弹出的确认弹框（如“保存成功，是否审核？”等）
        self._handle_confirm_dialog("保存成功", timeout=5000)

        try:
            # 等待提示信息
            msg = self.page.locator(
                ".ivu-message-success, .ivu-notice-success, .ivu-message-error, .ivu-notice-error"
            ).first
            if msg.is_visible(timeout=5000):
                print(f"系统提示: {msg.text_content().strip()}")
        except:
            pass

        time.sleep(2)

    def audit_product(self) -> None:
        """审核商品"""
        print("准备审核商品")
        try:
            # 0. 先关闭所有可能遮挡的弹窗（保存后可能残留 myModal）
            try:
                modals = self.page.locator('.ivu-modal-wrap:visible').all()
                for modal in modals:
                    ok_btn = modal.locator('.ivu-btn-primary:has-text("确定"), .ivu-btn:has-text("关闭"), .ivu-btn:has-text("取消")').first
                    if ok_btn.count() > 0 and ok_btn.is_visible():
                        ok_btn.click(force=True)
                        time.sleep(0.5)
                # 再按 Escape 保险
                self.page.keyboard.press("Escape")
                time.sleep(0.5)
            except Exception:
                pass

            # 1. 勾选列表第一行（如果还在列表页）
            if self.locator_add_btn.is_visible(timeout=2000):
                print("在列表页，尝试勾选第一行...")
                first_checkbox = self.page.locator('.ivu-table-row').first.locator('.ivu-checkbox-input').first
                if first_checkbox.is_visible(timeout=3000):
                    first_checkbox.click(force=True)
                    time.sleep(1)
            
            # 2. 点击审核按钮
            print("等待审核按钮启用...")
            self.locator_audit_btn.first.wait_for(state="visible", timeout=10000)
            
            start_time = time.time()
            btn_enabled = False
            while time.time() - start_time < 15:
                is_disabled = self.locator_audit_btn.first.get_attribute("disabled")
                if is_disabled is None or is_disabled == "false":
                    btn_enabled = True
                    break
                time.sleep(1)

            if btn_enabled:
                self.locator_audit_btn.first.click(force=True)
                print("已点击审核按钮")
            else:
                print("警告：审核按钮未启用，尝试强制点击")
                self.locator_audit_btn.first.click(force=True)

            # 3. 处理审核成功后的确认弹窗
            self._handle_confirm_dialog("审核成功", timeout=10000)

            # 4. 确保回到列表页
            if self.locator_save_btn.is_visible(timeout=2000) or self.page.locator('.ivu-btn:has-text("返回")').first.is_visible():
                print("检测到仍在详情/编辑页，点击'返回'")
                back_btn = self.page.locator('.ivu-btn:has-text("返回")').or_(self.page.locator('.ivu-btn:has-text("取消")')).filter(visible=True).first
                if back_btn.is_visible():
                    back_btn.click(force=True)
                    time.sleep(2)

            # 5. 最后验证是否回到了列表页
            if not self.locator_add_btn.is_visible(timeout=3000):
                print("未能自动返回列表页，强制导航...")
                self.page.goto(self.PRODUCT_ITEM_PATH)
                time.sleep(2)
                
        except Exception as e:
            print(f"审核过程发生异常: {e}")
            
        time.sleep(1)

    def search_product_by_code(self, code: str) -> None:
        """根据编码查询商品"""
        print(f"查询商品，编码: {code}")
        try:
            # 1. 强制导航到列表页并刷新，确保处于干净的状态
            print("强制导航并刷新页面以进行查询...")
            self.page.goto(self.PRODUCT_ITEM_PATH)
            self.page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # 2. 查找搜索框
            search_input = self.page.locator('input[placeholder*="商品编码/条码/名称"]') \
                .or_(self.page.locator('.ivu-input[placeholder*="查询"]')) \
                .or_(self.page.locator('.ivu-input[placeholder*="编码"]')) \
                .filter(visible=True).first
            
            search_input.wait_for(state="visible", timeout=15000)
            
            # 3. 填写并查询
            search_input.click()
            search_input.clear()
            search_input.fill(code)
            
            # 点击查询按钮
            self.page.locator('.ivu-btn-primary:has-text("查询")').filter(visible=True).first.click()
            # 等待查询结果加载
            self.wait_for_spinner_hidden(timeout=10000)
            time.sleep(2)
            
        except Exception as e:
            print(f"查询操作失败: {e}")
            # 兜底：尝试点击重置按钮
            try:
                self.locator_reset_btn.click(force=True)
                time.sleep(1)
                self.locator_search_input.fill(code)
                self.click_search()
                time.sleep(2)
            except:
                pass

    def get_form_errors(self) -> List[str]:
        """获取表单校验错误信息"""
        try:
            errors = self.locator_form_errors.all_text_contents()
            return [e.strip() for e in errors if e.strip()]
        except Exception:
            return []

    def get_error_message(self, timeout: int = 3000) -> str:
        """获取错误提示信息"""
        try:
            self.locator_error_message.first.wait_for(state="visible", timeout=timeout)
            return self.locator_error_message.first.text_content().strip()
        except Exception:
            return ""

    def search_product_by_name(self, name: str) -> None:
        """根据商品名称查询商品"""
        self.fill_search_name(name)
        self.click_search()

    # ------------------------------------------
    # 结果验证
    # ------------------------------------------
    def has_confirm_dialog(self, timeout: int = 3000) -> bool:
        """
        检查是否出现确认对话框
        :param timeout: 等待超时（毫秒）
        :return: 是否出现
        """
        try:
            self.locator_confirm_dialog.first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_table_row_count(self) -> int:
        """获取表格行数"""
        try:
            return self.locator_table_rows.count()
        except Exception:
            return 0
