"""
调零售价单页面对象
目标网站: https://royal-pre.cs.kemai.com.cn/archives/itemPriceChangeList
功能: 新增调零售价单、修改零售价、保存审核、查询单号
"""

import time
from playwright.sync_api import Page
from pages.base_page import BasePage


class ItemPriceChangePage(BasePage):
    """调零售价单页面 Page Object"""

    PRICE_CHANGE_PATH = "/archives/itemPriceChangeList"

    def __init__(self, page: Page, base_url: str = "https://royal-pre.cs.kemai.com.cn"):
        super().__init__(page)
        self.base_url = base_url.rstrip("/")

        # ============ 工具栏按钮 ============
        self.locator_add_btn = self.page.get_by_role("button", name="新增").first
        self.locator_search_btn = self.page.get_by_role("button", name="查询").first

        # ============ 提示信息 ============
        self.locator_success_message = self.page.locator(".ivu-message-success")
        self.locator_error_message = self.page.locator(".ivu-message-error")

    # ------------------------------------------
    # 导航
    # ------------------------------------------
    def navigate_to_price_change(self) -> None:
        """直接导航到调零售价单页面"""
        self.page.goto(self.base_url + self.PRICE_CHANGE_PATH)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

    def is_on_price_change_page(self, timeout: int = 10000) -> bool:
        """检查是否在调零售价单页面"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if "itemPriceChange" in self.page.url:
                    return True
                time.sleep(0.5)
            return False
        except Exception:
            return False

    # ------------------------------------------
    # 新增调价单
    # ------------------------------------------
    def click_add(self) -> None:
        """点击新增按钮"""
        print("点击'新增'按钮")
        self.locator_add_btn.wait_for(state="visible", timeout=10000)
        self.locator_add_btn.click()
        time.sleep(2)

    def select_all_organizations(self) -> None:
        """选择全部机构（点击单选按钮）"""
        try:
            print("选择全部机构")
            time.sleep(2)

            # 点击"全部机构"单选按钮
            all_org_radio = self.page.get_by_role("radio", name="全部机构")
            if all_org_radio.is_visible(timeout=3000):
                all_org_radio.click()
                time.sleep(1)
                print("已选择全部机构")
            else:
                print("未找到全部机构单选按钮")
        except Exception as e:
            print(f"选择全部机构失败: {e}")

    def click_product_search(self) -> None:
        """点击商品检索按钮"""
        try:
            print("点击商品检索按钮")
            search_btn = self.page.get_by_role("button", name="商品检索")
            search_btn.wait_for(state="visible", timeout=5000)
            search_btn.click()
            time.sleep(2)
            print("商品检索对话框已打开")
        except Exception as e:
            print(f"点击商品检索按钮失败: {e}")

    def click_select_product(self) -> None:
        """点击选择商品按钮"""
        try:
            print("点击选择商品按钮")
            select_btn = self.page.get_by_role("button", name="选择商品")
            select_btn.wait_for(state="visible", timeout=5000)
            select_btn.click()
            time.sleep(2)
            print("选择商品对话框已打开")
        except Exception as e:
            print(f"点击选择商品按钮失败: {e}")

    def input_product_code(self, code: str) -> None:
        """在商品检索对话框中输入商品编码并搜索"""
        try:
            print(f"输入商品编码: {code}")
            time.sleep(2)  # 等待对话框完全加载

            # 通过placeholder定位商品编码输入框
            # placeholder: "国际条码/商品编码/商品名称/助记码"
            code_input = self.page.locator("input[placeholder*='商品编码'], input[placeholder*='国际条码']").first
            code_input.wait_for(state="visible", timeout=5000)
            code_input.click()
            code_input.fill(code)
            time.sleep(1)

            # 点击查询按钮
            query_btn = self.page.get_by_role("button", name="查询")
            if query_btn.is_visible(timeout=2000):
                query_btn.click()
                time.sleep(2)
                print("商品编码已输入并点击查询")
            else:
                # 如果没有查询按钮，按回车搜索
                code_input.press("Enter")
                time.sleep(2)
                print("商品编码已输入并回车搜索")

        except Exception as e:
            print(f"输入商品编码失败: {e}")

    def select_product_and_confirm(self) -> None:
        """选择商品并确认"""
        try:
            print("选择商品并确认")
            time.sleep(2)  # 等待商品列表加载

            # 关键发现：商品选择对话框中，可见的复选框有2个
            # 第一个是"全选"复选框，第二个是商品行的复选框
            visible_checkboxes = self.page.locator(".ivu-modal .ivu-checkbox-wrapper:visible").all()
            print(f"对话框中找到 {len(visible_checkboxes)} 个可见的复选框")

            if len(visible_checkboxes) >= 2:
                # 点击第二个复选框（商品行）- 使用 force=True 避免被拦截
                visible_checkboxes[1].click(force=True)
                time.sleep(1)
                print("已选择商品（点击第二个复选框）")

                # 验证是否选中
                is_checked = self.page.locator(".ivu-modal .ivu-checkbox-checked").count() > 0
                print(f"复选框选中状态: {is_checked}")
            else:
                print("复选框数量不足，尝试备用方案...")
                # 备用方案：查找所有复选框并点击最后一个
                all_checkboxes = self.page.locator(".ivu-checkbox-wrapper").all()
                if len(all_checkboxes) > 0:
                    all_checkboxes[-1].click(force=True)
                    time.sleep(1)
                    print("已通过备用方案选择商品")

            # 点击确定按钮
            confirm_btn = self.page.get_by_role("button", name="确定")
            if confirm_btn.count() > 0:
                confirm_btn.first.click()
                time.sleep(3)
                print("已确认选择")
            else:
                print("未找到确定按钮")
        except Exception as e:
            print(f"选择商品并确认失败: {e}")

    def modify_retail_price(self, new_price: str) -> None:
        """修改新零售价"""
        try:
            print(f"修改新零售价为: {new_price}")
            # 等待商品信息加载到表格
            time.sleep(3)

            # 查找页面上所有可编辑的输入框（在表格区域，y > 200）
            all_inputs = self.page.locator("input:visible").all()
            editable_inputs = []
            for inp in all_inputs:
                try:
                    box = inp.bounding_box()
                    is_editable = inp.is_editable()
                    if box and box['y'] > 200 and is_editable:
                        editable_inputs.append(inp)
                except:
                    continue

            print(f"找到 {len(editable_inputs)} 个可编辑的表格输入框")

            # 修改最后一个可编辑输入框（通常是新零售价）
            if editable_inputs:
                price_input = editable_inputs[-1]
                price_input.click(click_count=3)  # 三击全选
                price_input.fill(new_price)
                time.sleep(1)
                print(f"新零售价已修改为: {new_price}")
            else:
                print("未找到可编辑的价格输入框，尝试备用方案...")

                # 备用方案：直接查找表格中所有输入框
                table_inputs = self.page.locator(".ivu-table input:visible").all()
                print(f"表格中找到 {len(table_inputs)} 个输入框")

                for inp in reversed(table_inputs):
                    try:
                        if inp.is_editable():
                            inp.click(click_count=3)
                            inp.fill(new_price)
                            time.sleep(1)
                            print(f"新零售价已修改为: {new_price}")
                            return
                    except:
                        continue

                print("未找到价格输入框，可能商品未正确添加")
        except Exception as e:
            print(f"修改新零售价失败: {e}")

    def save_and_audit(self) -> str:
        """保存并审核，返回单号"""
        bill_number = ""
        try:
            # 先关闭可能存在的弹窗
            self.close_blocking_modals()

            print("点击保存按钮")
            save_btn = self.page.get_by_role("button", name="保存")
            # 等待保存按钮可用
            for i in range(10):
                if save_btn.count() > 0 and save_btn.first.is_enabled():
                    # 使用 force 点击避免被遮挡
                    save_btn.first.click(force=True)
                    print("保存按钮已点击")
                    break
                time.sleep(1)
                print(f"等待保存按钮可用... ({i+1}/10)")

            time.sleep(3)

            # 检查保存结果
            success_msg = self.get_success_message(timeout=5000)
            if success_msg:
                print(f"保存成功: {success_msg}")

            # 保存后立即获取单号（在模态框关闭前）
            bill_number = self._extract_bill_number_from_modal()
            if bill_number:
                print(f"保存后获取到单号: {bill_number}")

            print("点击审核按钮")
            audit_btn = self.page.get_by_role("button", name="审核")
            if audit_btn.count() > 0 and audit_btn.first.is_visible(timeout=3000):
                audit_btn.first.click(force=True)
                time.sleep(2)

                # 确认审核弹窗
                confirm_btn = self.page.get_by_role("button", name="确定")
                if confirm_btn.count() > 0 and confirm_btn.first.is_visible(timeout=3000):
                    confirm_btn.first.click()
                    time.sleep(2)

                print("保存并审核完成")
            else:
                print("未找到审核按钮，可能已自动审核或保存后自动审核")
        except Exception as e:
            print(f"保存并审核失败: {e}")

        return bill_number

    def _extract_bill_number_from_modal(self) -> str:
        """从当前编辑模态框中提取单号"""
        import re
        try:
            # 等待一下让页面更新
            time.sleep(1)

            # 方式1: 查找模态框中的单号label和输入框
            modal = self.page.locator(".ivu-modal-content:visible, .myModal:visible").first
            if modal.count() > 0:
                # 查找单号label
                bill_labels = modal.locator(".ivu-form-item-label").filter(has_text="单号")
                if bill_labels.count() > 0:
                    parent = bill_labels.first.locator("xpath=..")
                    bill_input = parent.locator("input").first
                    if bill_input.is_visible(timeout=1000):
                        value = bill_input.input_value()
                        if value and len(value) >= 8:
                            return value

                # 方式2: 从模态框文本中查找单号模式
                modal_text = modal.inner_text()
                match = re.search(r'单号[：:\s]*(\d{8,})', modal_text)
                if match:
                    return match.group(1)

                # 方式3: 查找模态框标题中的单号
                header = modal.locator(".ivu-modal-header, .ivu-modal-header-inner").first
                if header.count() > 0:
                    header_text = header.inner_text()
                    match = re.search(r'(\d{10,})', header_text)
                    if match:
                        return match.group(1)

            # 方式4: 查找整个页面的单号
            bill_labels = self.page.locator(".ivu-form-item-label").filter(has_text="单号")
            if bill_labels.count() > 0:
                for label in bill_labels.all():
                    parent = label.locator("xpath=..")
                    bill_input = parent.locator("input").first
                    if bill_input.is_visible(timeout=500):
                        value = bill_input.input_value()
                        if value and len(value) >= 8:
                            return value

            return ""
        except Exception as e:
            print(f"提取单号失败: {e}")
            return ""

    def close_blocking_modals(self) -> None:
        """关闭可能阻挡操作的弹窗"""
        try:
            # 使用ESC键关闭可能的弹窗
            self.page.keyboard.press("Escape")
            time.sleep(0.5)

            # 检查是否有小型提示弹窗（如"请选择一条数据"）
            modals = self.page.locator(".ivu-modal-wrap:visible").all()
            for modal in modals:
                try:
                    # 检查是否是小弹窗（高度小于200px通常是提示弹窗）
                    box = modal.bounding_box()
                    if box and box['height'] < 200:
                        # 尝试点击确定按钮
                        confirm = modal.get_by_role("button", name="确定")
                        if confirm.is_visible(timeout=500):
                            confirm.click()
                            time.sleep(0.3)
                            continue

                        # 尝试点击关闭按钮
                        close_btn = modal.locator(".ivu-modal-close")
                        if close_btn.is_visible(timeout=500):
                            close_btn.click()
                            time.sleep(0.3)
                except:
                    pass
        except:
            pass

    def get_bill_number(self) -> str:
        """获取单号 - 从当前页面或列表中获取"""
        try:
            time.sleep(2)
            import re

            # 方式1: 从当前编辑模态框中查找
            bill_labels = self.page.locator(".ivu-form-item-label").filter(has_text="单号")
            if bill_labels.count() > 0:
                for label in bill_labels.all():
                    try:
                        parent = label.locator("xpath=..")
                        bill_input = parent.locator("input").first
                        if bill_input.is_visible(timeout=1000):
                            value = bill_input.input_value()
                            if value and len(value) >= 8:
                                print(f"从单号输入框获取到单号: {value}")
                                return value
                    except:
                        continue

            # 方式2: 从URL获取
            url = self.page.url
            if "billNo=" in url:
                bill_no = url.split("billNo=")[1].split("&")[0]
                print(f"从URL获取到单号: {bill_no}")
                return bill_no

            # 方式3: 从成功消息中获取
            success_msg = self.page.locator(".ivu-message-success").first
            if success_msg.is_visible(timeout=1000):
                msg_text = success_msg.inner_text()
                match = re.search(r'(\d{10,})', msg_text)
                if match:
                    print(f"从成功消息获取到单号: {match.group(1)}")
                    return match.group(1)

            print("未能获取到单号")
            return ""
        except Exception as e:
            print(f"获取单号失败: {e}")
            return ""

    def get_first_bill_number_from_list(self) -> str:
        """从列表页获取第一条记录的单号"""
        try:
            time.sleep(2)
            import re

            # 确保在列表页
            if "itemPriceChangeList" not in self.page.url:
                self.navigate_to_price_change()
                time.sleep(2)

            # 等待加载完成
            self.wait_for_spinner_hidden(timeout=10000)

            # 使用JavaScript获取第一行数据
            result = self.page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('.km-grid-body .km-grid-tr-wrap');
                    if (rows.length > 1) {
                        // 第二个tr-wrap包含实际数据
                        const cells = rows[1].querySelectorAll('.km-grid-td');
                        const cellTexts = [];
                        cells.forEach(cell => {
                            let text = cell.innerText;
                            text = text.replace('td_placeholder', '').trim();
                            if (text) {
                                cellTexts.push(text);
                            }
                        });
                        return cellTexts;
                    }
                    return [];
                }
            """)

            if result:
                print(f"第一行数据: {result[:5]}")
                # 单号格式: TA + 数字 (如 TA1003202603170002)
                for cell in result:
                    match = re.match(r'^(TA\d+)$', cell)
                    if match:
                        bill_no = match.group(1)
                        print(f"从列表第一行获取到单号: {bill_no}")
                        return bill_no

            # 备用方式：从整个grid文本中查找
            grid = self.page.locator(".km-grid-body").first
            if grid.count() > 0:
                grid_text = grid.inner_text()
                matches = re.findall(r'\b(TA\d{10,})\b', grid_text)
                if matches:
                    bill_no = matches[0]
                    print(f"从列表grid获取到单号: {bill_no}")
                    return bill_no

            print("未能从列表获取到单号")
            return ""
        except Exception as e:
            print(f"从列表获取单号失败: {e}")
            return ""

    def back_to_list(self) -> None:
        """返回列表"""
        try:
            print("返回列表")
            # 先关闭可能阻挡的模态框
            self.close_blocking_modals()

            back_btn = self.page.get_by_role("button", name="返回").first
            if back_btn.is_visible(timeout=2000):
                # 使用 force=True 避免被其他元素拦截
                back_btn.click(force=True)
                time.sleep(2)
                print("已点击返回按钮")
            else:
                # 直接导航回列表页
                print("返回按钮不可见，直接导航")
                self.navigate_to_price_change()

            # 确保回到列表页
            time.sleep(1)
            if "itemPriceChangeList" not in self.page.url or "billNo" in self.page.url:
                self.navigate_to_price_change()
        except Exception as e:
            print(f"返回列表失败: {e}")
            self.navigate_to_price_change()

    def search_by_bill_number(self, bill_no: str) -> None:
        """按单号查询"""
        try:
            print(f"按单号查询: {bill_no}")

            # 确保在列表页
            if "itemPriceChangeList" not in self.page.url or "billNo" in self.page.url:
                self.navigate_to_price_change()
                time.sleep(2)

            # 方式1: 通过placeholder "单据编号" 查找
            bill_input = self.page.locator("input[placeholder*='单据编号'], input[placeholder*='单号']").first
            if bill_input.is_visible(timeout=3000):
                bill_input.click()
                bill_input.fill(bill_no)
                time.sleep(1)
                print("已在单据编号输入框输入")
            else:
                # 方式2: 通过label查找
                bill_label = self.page.locator(".ivu-form-item-label").filter(has_text="单号")
                if bill_label.count() > 0:
                    print("找到单号label")
                    parent = bill_label.first.locator("xpath=..")
                    bill_input = parent.locator("input").first
                    if bill_input.is_visible(timeout=3000):
                        bill_input.click()
                        bill_input.fill(bill_no)
                        time.sleep(1)
                        print("已在单号输入框输入")
                else:
                    raise Exception("未找到单号输入框")

            # 点击查询按钮
            self.locator_search_btn.click()
            time.sleep(2)
            print("查询完成")
        except Exception as e:
            print(f"按单号查询失败: {e}")

    def is_bill_exists(self, bill_no: str) -> bool:
        """检查单号是否存在于列表中"""
        try:
            self.wait_for_spinner_hidden(timeout=10000)
            time.sleep(1)
            grid_text = self.page.evaluate("""
                () => {
                    const grid = document.querySelector('.km-grid-body-scroll') ||
                                 document.querySelector('.km-grid-body') ||
                                 document.querySelector('.ivu-table-body');
                    return grid ? (grid.innerText || grid.textContent || '') : '';
                }
            """)
            if bill_no in grid_text:
                print(f"在表格中找到单号: {bill_no}")
                return True
            return False
        except Exception as e:
            print(f"is_bill_exists 异常: {e}")
            return False

    def get_success_message(self, timeout: int = 5000) -> str:
        """获取成功提示信息"""
        try:
            self.locator_success_message.wait_for(state="visible", timeout=timeout)
            msg = self.locator_success_message.inner_text()
            return msg
        except Exception:
            return ""

    def get_error_message(self, timeout: int = 3000) -> str:
        """获取错误提示信息"""
        try:
            self.locator_error_message.wait_for(state="visible", timeout=timeout)
            msg = self.locator_error_message.inner_text()
            return msg
        except Exception:
            return ""
