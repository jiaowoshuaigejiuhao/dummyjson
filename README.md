MiniShop API Automation Framework 🚀
基于 Python + Pytest + Requests + Allure 实现的接口自动化测试框架，针对 DummyJSON 模拟电商业务（Auth、Products、Carts、Users、Posts、Todos 等）完成了接口回归与部分端到端链路的自动化覆盖。

框架具备：

多环境切换、命令行参数控制（env/baseurl/timeout/proxy）
Session 全局共享 + 干净 Session 隔离
YAML 数据驱动（登录、搜索、分页、刷新 token 等）
统一的 BaseApi 封装（超时、日志、Allure 附件、敏感字段脱敏）
可选 Fiddler Mock/弱网注入开关（基于 header + fixture）
Smoke/Negative/Need-fiddler 等用例分组能力
🏗 核心架构与技术栈
设计分层

BaseApi：
统一封装 requests.Session、timeout、URL 拼接、请求/响应日志、Allure 附件、异常处理与敏感字段脱敏。
业务 API 分层 (ApiObject)：
AuthApi / ProductApi / CartApi / UsersApi / ... 只关注接口路径和业务语义，构造函数透传 **kwargs（如 timeout）给 BaseApi，便于后续扩展重试/代理等能力。
TestCases 分离：
Auth、Product、Cart 等各自独立的 flow 文件，结合 YAML 数据驱动和 Pytest mark（smoke/negative）。
主要技术栈

测试框架：Pytest
fixture 管理生命周期（session 和 function scope）
pytest_addoption 自定义命令行参数：--env / --baseurl / --proxy / --insecure / --timeout
parametrize + YAML 实现数据驱动
mark 分类：smoke、negative、nondestructive、need_fiddler 等
HTTP 客户端：Requests
基于 requests.Session 做登录态复用（Authorization header）
基于 BaseApi 统一注入 timeout，防止 CI 挂死
数据处理：
YAML 管理测试数据（AUTH_login_cases.yaml、PRODUCT_search_cases.yaml、AUTH_refresh_cases.yaml 等）
动态关联：通过接口先查再用真实 ID（userId/productId/cartId），减少 Demo 环境不稳定带来的误报
报告与日志：
Allure 2：每个请求的 Request/Response Meta & Body 以附件形式挂到步骤上
自定义 Logger：记录 Method/URL/脱敏后的 kwargs、状态码、耗时
⚙️ 框架亮点实现
1. Session 共享 + 干净 Session 隔离
在 tests/conftest.py 中，通过 session_factory + shared_session + clean_session 设计：

shared_session (session scope)
用于业务回归流：通过 logged_in_auth_api 登录一次后，所有业务 Api（ProductApi、CartApi 等）共享同一 Session 和 Token。
clean_session (function scope)
用于负向/安全测试：auth_api 使用独立 Session，测试错误密码/伪造 token 等场景，避免污染全局登录态。
2. BaseApi 工程化封装
apis/base_api.py 封装了请求的各个横切能力：

URL 规范化：base_url.rstrip("/") + "/" + urljoin 防止路径拼错
默认超时：支持 --timeout 命令行参数，未显式传入时统一使用 BaseApi 的配置
请求/响应日志与 Allure 附件：
Request：method / url / headers / json/data（均做敏感字段脱敏）
Response Meta：status_code / elapsed_ms / headers / url
Response Body：JSON 优先，其次 text
敏感字段脱敏：对 password/token/authorization 等字段做统一替换，日志与 Allure 报告中不会泄漏真实值
Token 管理：set_token() 自动写入 session.headers["Authorization"]，实现登录一次，多模块复用
3. 鉴权与 Auth 流程设计
针对 DummyJSON Auth 模块，设计了完整的登录/鉴权/刷新流程测试：

登录场景：
使用 AUTH_login_cases.yaml 数据驱动：覆盖正常登录、密码错误、用户不存在、空用户名/密码、缺字段、类型错误等
测试函数统一断言：
HTTP 状态码
token 是否存在（兼容 token/accessToken）
正向用例用户名一致
负向用例错误 message 包含预期关键字（大小写不敏感）
/auth/me 场景：
未登录访问 /auth/me：打上 @pytest.mark.negative，验证返回未授权
已登录访问 /auth/me：打上 @pytest.mark.smoke，验证返回当前用户信息（username/email 等）
刷新 token 场景：
通过 AUTH_refresh_cases.yaml 组合 pre_login + fake_token + expect 字段：
已登录有效 token 刷新成功
未登录/无 token 刷新失败
伪造 token/过期 token 行为（根据 DummyJSON 实际行为调整期望）
刷新成功后使用新 token 再调 /auth/me 验证新 token 真的有效
4. 商品搜索/分类等业务测试设计
搜索场景（test_search_products）：
利用 PRODUCT_search_cases.yaml 管理多种搜索组合：
不同关键字：iphone / samsung / phone / 特殊字符 / 不存在关键字
边界 limit：1、>系统上限
验证总数 min_total、每次返回条数 max_limit、字段存在 has_field
测试逻辑统一：
len(products) <= max_limit（分页逻辑）
total >= min_total 或 total == 0（不存在关键字）
has_field 在第一条商品中存在（如 title/price）
分类到详情链路：
通过 test_category_workflow/小链路用例：
GET /products/category/{category} → 取一个 product → GET /products/{id}
对比 id/title 等字段一致性
5. Fiddler Mock/弱网注入预埋能力
通过 header + fixture 的设计，使得 pytest 用例可以“按需触发” Fiddler 中配置的 Mock/弱网规则：

在 conftest.py 中预置扩展 fixture：
product_api_empty_list：为 Session 增加 X-Mock-Scenario: products_empty header，用于 FiddlerScript 将 /products/search 强制返回空列表。
product_api_slow：为 Session 增加 X-Simulate-SlowNet: true header，用于 FiddlerScript 添加 trickle-delay/限速，实现弱网模拟。
对应用例加上 @pytest.mark.need_fiddler，避免在未配置 Fiddler 时误跑。
后续只需在 FiddlerScript 中基于这些 header 写规则，就能实现“用例驱动的 Mock/弱网注入”。

📊 测试报告与日志
执行完成后，可在 logs/ 目录下查看按日期分割的运行日志（含请求/响应关键字段、耗时）。
使用 Allure 生成可视化报告：
每条用例按业务流程拆分为多个 steps（例如“登录”，“搜索商品”，“加入购物车”，“校验购物车金额”）。
每个步骤包含附加的 Request/Response（JSON/文本），方便快速定位问题。
示例报告截图可自行补充（如 Allure 的概览页面、某条失败用例的详情页等）。

🚀 快速开始
安装依赖
Bash

pip install -r requirements.txt
运行测试
默认运行（Dev 环境）
Bash

pytest
指定环境
Bash

pytest --env=test
设置基础 URL（覆盖 env.yaml）
Bash

pytest --env=test --baseurl=https://dummyjson.com
设置网络策略：超时 & 代理（Fiddler 抓包/Mock）
Bash

# 设置超时（秒）
pytest --timeout=5

# 通过本机 Fiddler 抓包 + HTTPS 解密（需本地开启 Fiddler，默认 8888 端口）
pytest --proxy --insecure
按标记运行
Bash

# 只跑核心链路（登录 + 获取当前用户 + 商品基础查询等）
pytest -m smoke

# 只跑负向/错误场景
pytest -m negative

# 只跑依赖 Fiddler Mock/弱网的用例（需预先在 Fiddler 中配置规则）
pytest -m need_fiddler --proxy --insecure
生成 Allure 报告
Bash

pytest --alluredir=./allure-results
allure serve ./allure-results
📂 目录结构
text

MiniShop_API_Automation/
├── apis/                  # 接口对象层 (API Objects)
│   ├── base_api.py        # 核心封装 (Session, Timeout, Log, Allure, 脱敏)
│   ├── auth_api.py        # 鉴权模块 (登录/获取当前用户/刷新 token)
│   ├── product_api.py     # 商品模块
│   ├── cart_api.py        # 购物车模块
│   ├── users_api.py       # 用户模块
│   ├── posts_api.py       # 帖子模块
│   ├── comments_api.py    # 评论模块
│   ├── todos_api.py       # 待办模块
│   └── recipes_api.py     # 菜谱模块
├── config/
│   └── env.yaml           # 多环境配置 (dev/test，含 base_url/用户名/密码)
├── data/
│   ├── AUTH_login_cases.yaml     # 登录场景数据（正向+负向）
│   ├── AUTH_refresh_cases.yaml   # 刷新 token 场景
│   ├── PRODUCT_search_cases.yaml # 商品搜索场景（关键字/limit 等）
│   └── ...
├── logs/                  # 运行日志（按日期切分）
├── tests/
│   ├── conftest.py        # Fixture 管理 & CLI 参数 & Session 工厂
│   ├── test_auth_flow.py  # Auth 登录/鉴权/刷新 流程与用例集
│   ├── test_product_flow.py
│   ├── test_cart_flow.py
│   ├── test_users_flow.py
│   ├── test_posts_flow.py
│   ├── test_comments_flow.py
│   ├── test_todos_flow.py
│   ├── test_recipes_flow.py
│   └── ...
├── utils/
│   ├── log_util.py        # 日志封装
│   └── yaml_util.py       # YAML 读写工具
├── pytest.ini             # Pytest 配置（markers、默认参数等）
├── requirements.txt       # 依赖库
└── run.py                 # 启动入口（可选，封装 pytest.main）
📌 适用场景 & 可扩展方向
作为 接口自动化框架骨架，用于实际业务项目的快速迁移与二次开发；
结合 Fiddler/Charles，将 “header 开关 + 代理” 扩展为可控 Mock/弱网注入平台；
引入 JMeter/Gatling 等性能工具，与当前框架共享数据/Session，形成“功能 + 性能”的一体化测试仓库；
接入 CI（Jenkins / GitHub Actions），执行定时回归、冒烟、按标记分层执行等。
