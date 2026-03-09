# YF 系统 UI 自动化测试项目

基于 Playwright + Pytest 的 UI 自动化测试框架

## 测试目标

- 网站地址: https://royal-pre.cs.kemai.com.cn/
- 测试账号: 15901234560
- 测试密码: 123123123

## 项目结构

```
yf_playwright/
├── conftest.py              # 全局配置和fixture
├── pytest.ini               # pytest配置文件
├── requirements.txt         # 依赖包
├── README.md               # 项目说明
├── plugins/                 # 自定义插件
│   ├── __init__.py
│   ├── pytest_playwright.py # Playwright插件
│   └── pytest_base_url_plugin.py # Base URL插件
├── pages/                   # 页面对象（Page Object）
│   ├── __init__.py
│   └── login_page.py       # 登录页面对象
├── cases/                   # 测试用例
│   ├── __init__.py
│   ├── conftest.py         # 用例级别fixture
│   └── test_login.py       # 登录测试用例
└── test-results/           # 测试结果（自动生成）
```

## 环境安装

### 1. 创建虚拟环境（可选）

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装浏览器

```bash
playwright install chromium
# 或安装所有浏览器
playwright install
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行指定测试文件

```bash
pytest cases/test_login.py
```

### 运行指定测试用例

```bash
pytest cases/test_login.py::TestLogin::test_login_success
```

### 常用参数

```bash
# 有头模式（显示浏览器）
pytest --headed

# 无头模式
pytest

# 指定浏览器
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# 慢速执行（便于观察）
pytest --slowmo 500

# 生成 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

## 配置说明

### pytest.ini 配置项

- `--headed`: 显示浏览器窗口
- `--screenshot=only-on-failure`: 失败时截图
- `--video=retain-on-failure`: 失败时保存视频
- `--base-url`: 测试目标网站地址

## 页面对象说明

### LoginPage (login_page.py)

登录页面的 Page Object，封装了登录相关的元素定位和操作方法：

- `navigate()`: 导航到登录页面
- `fill_phone(phone)`: 填写手机号
- `fill_password(password)`: 填写密码
- `click_login_button()`: 点击登录按钮
- `login(phone, password)`: 完整登录操作
- `get_error_message()`: 获取错误提示
- `is_login_successful()`: 检查登录是否成功

## 注意事项

1. **元素定位器调整**: 由于无法实际访问目标网站，页面元素的定位器可能需要根据实际页面进行调整。运行测试后，如果定位失败，请检查页面结构并更新 `login_page.py` 中的定位器。

2. **测试断言调整**: 测试用例中的断言也需要根据实际页面响应进行调整，例如登录成功后的跳转URL、成功提示等。

3. **等待策略**: 当前使用固定等待时间，生产环境建议使用显式等待以提高测试稳定性。

## 后续扩展

1. 添加更多页面对象（如首页、用户中心等）
2. 添加更多测试用例（如注册、找回密码等）
3. 集成 CI/CD 流水线
