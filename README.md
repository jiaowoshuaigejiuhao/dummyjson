# MiniShop API Automation Framework 🚀

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pytest](https://img.shields.io/badge/Pytest-7.0%2B-green)
![Allure](https://img.shields.io/badge/Allure-Report-orange)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)

## 📖 项目简介

基于 **Python + Pytest + Requests + Allure** 实现的接口自动化测试框架。
项目针对 [DummyJSON](https://dummyjson.com/) 的模拟电商业务（Auth, Products, Carts, Users, Posts, Todos 等）完成了全链路接口自动化覆盖。具备**多环境切换**、**Session 全局共享**、**数据驱动**、**动态闭环断言**等企业级特性。

## 🏗️ 核心架构与技术栈

- **设计模式**：BaseApi 基础封装 + 业务 API 分层 + TestCases 分离。
- **测试框架**：Pytest (Fixture 管理生命周期, Parametrize 实现数据驱动)。
- **HTTP 客户端**：Requests (封装统一的日志记录、异常捕获、Session 保持)。
- **鉴权管理**：实现 `Session Scope` 级的登录态共享，解决 Token 传递与复用问题。
- **数据处理**：
  - YAML 管理测试数据。
  - JsonPath 处理深层嵌套 JSON 提取。
  - 动态关联：通过 API 提取真实 ID 进行闭环测试，解决 Mock 数据不确定性问题。
- **报告集成**：Allure 2 详细测试报告（包含 Request/Response 日志附件）。

## ⚡️ 亮点实现
Session 共享机制：
在 conftest.py 中定义 global_session fixture，实现登录一次，所有业务模块（Product, Cart等）自动继承 Header 和 Token，大幅提升执行效率。

健壮的断言策略：
针对 Mock 数据易变的特性，采用“先查后验”的闭环逻辑。例如：测试“查询用户购物车”时，先获取存在购物车的 UserID，再进行查询，防止因随机数据导致误报。

Allure 深度集成：
自定义 Logger，将每个接口的 Method、URL、Params、Response 自动 Attach 到 Allure 报告步骤中，便于问题排查。

## 📊 测试报告截图
<img width="1920" height="953" alt="image" src="https://github.com/user-attachments/assets/440d228d-beef-4711-bece-50a7e6ee0334" />
<img width="1920" height="953" alt="image" src="https://github.com/user-attachments/assets/d80f12bc-1d2e-47c8-ba8f-d674a30b87c8" />
<img width="1920" height="953" alt="image" src="https://github.com/user-attachments/assets/07245211-9519-4e63-9218-b25d7a3d20ea" />




## 🚀 快速开始
1. 安装依赖
Bash
pip install -r requirements.txt

2. 运行测试
Bash

# 默认运行 (Dev环境)
pytest

# 指定环境
pytest --env=test

# 生成 Allure 报告
pytest --alluredir=./allure-results
allure serve ./allure-results




## 📂 目录结构

MiniShop_API_Automation/
├── apis/                  # 接口对象层 (API Objects)
│   ├── base_api.py        # 核心封装 (Session, Log, Exception)
│   ├── auth_api.py        # 认证模块
│   ├── product_api.py     # 商品模块
│   ├── cart_api.py        # 购物车模块
│   └── ...
├── config/                # 配置文件
│   └── env.yaml           # 多环境配置 (Dev/Test)
├── data/                  # 测试数据 (YAML)
├── logs/                  # 运行日志
├── tests/                 # 测试用例层
│   ├── conftest.py        # Fixture 共享与配置
│   ├── test_auth_flow.py
│   ├── test_product_flow.py
│   └── ...
├── utils/                 # 工具类 (Log, Yaml)
├── pytest.ini             # Pytest 配置文件
├── requirements.txt       # 依赖库
└── run.py                 # 启动入口

