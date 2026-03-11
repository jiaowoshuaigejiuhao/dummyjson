# MiniShop API Automation Framework 🚀

基于 **Python + Pytest + Requests + Allure** 实现的接口自动化测试框架，针对 [DummyJSON](https://dummyjson.com) 模拟电商业务（Auth、Products、Carts、Users、Posts、Todos 等）完成了接口回归与部分端到端链路的自动化覆盖。

框架具备：

- 多环境切换、命令行参数控制（`--env / --baseurl / --timeout / --proxy / --insecure`）
- Session 全局共享 + 干净 Session 隔离
- YAML 数据驱动（登录、搜索、分页、刷新 token 等）
- 统一的 BaseApi 封装（超时、日志、Allure 附件、敏感字段脱敏）
- 可选 Fiddler Mock/弱网注入开关（基于 header + fixture）
- `smoke` / `negative` / `need_fiddler` 等用例分组能力

---

## 🏗 核心架构与技术栈

### 分层设计

- **BaseApi（基础封装层）**  
  - 封装 `requests.Session`  
  - URL 规范化（`base_url.rstrip("/") + "/"` + `urljoin`）  
  - 默认 `timeout`（支持命令行覆盖）  
  - 请求/响应日志  
  - Allure Request/Response 附件  
  - 敏感字段脱敏（`password / token / authorization`）  
  - `set_token()` 统一写入 `session.headers["Authorization"]`

- **业务 API 分层（ApiObject）**  
  - `AuthApi / ProductApi / CartApi / UsersApi / PostsApi / CommentsApi / TodosApi / RecipesApi`  
  - 构造函数统一为 `__init__(base_url, session=None, **kwargs)`，透传参数到 BaseApi，便于后续扩展（重试策略、默认 header 等）

- **测试用例层（Tests）**  
  - 按业务模块拆分：`test_auth_flow.py / test_product_flow.py / test_cart_flow.py ...`  
  - Auth 模块覆盖登录、获取当前用户、刷新 token 正/反向场景  
  - Product 模块覆盖搜索、分页、排序、分类到详情小链路等

### 主要技术栈

- **Pytest**
  - Fixture 生命周期管理（`session` / `function` scope）
  - `pytest_addoption` 自定义命令行参数：
    - `--env`：环境选择（dev/test）
    - `--baseurl`：临时覆盖 `env.yaml` 中的 `base_url`
    - `--proxy`：是否通过本机 Fiddler 代理
    - `--insecure`：关闭 SSL 校验（用于 HTTPS 抓包）
    - `--timeout`：统一超时（秒）
  - `parametrize` + YAML 数据驱动（登录、搜索、刷新等场景）
  - mark 分类：
    - `smoke`：核心业务链路
    - `negative`：负向/边界场景
    - `need_fiddler`：依赖 Fiddler Mock/弱网的用例

- **Requests**
  - 基于 `Session` 进行登录态复用（Authorization header）
  - 通过 BaseApi 的 `timeout` 参数控制网络策略

- **数据驱动**
  - YAML 管理测试数据：
    - `AUTH_login_cases.yaml`：登录正/反向场景
    - `AUTH_refresh_cases.yaml`：刷新 token 场景
    - `PRODUCT_search_cases.yaml`：商品搜索/分页/边界场景
  - 通过"先查后用"的动态关联策略避免硬编码 ID（userId/productId/cartId）

- **报告 & 日志**
  - Allure 2：按业务场景拆 step，附加 Request/Response（JSON/文本）  
  - 自定义 Logger：记录 Method/URL/脱敏后的参数、状态码、耗时

---

## ⚙️ 框架亮点实现

### 1. Session 共享 + 干净 Session 隔离

在 `tests/conftest.py` 中，通过 `session_factory + shared_session + clean_session` 构建两类 Session：

- `shared_session`（`session` 作用域）  
  - 业务回归使用：`logged_in_auth_api` 在会话级别登录一次，将 token 写入 `shared_session.headers["Authorization"]`。  
  - 其他 Api（`ProductApi / CartApi / UsersApi ...`）通过 `api_factory` 复用该 Session，实现"登录一次，全局复用"。

- `clean_session`（`function` 作用域）  
  - 负向/隔离场景使用：`auth_api` 使用独立 Session，测试错误密码、伪造 token 等，不会污染全局登录态。

### 2. BaseApi 工程化封装

`apis/base_api.py` 提供统一的请求入口：

- URL 拼接与规范化：`base_url.rstrip("/") + "/"` + `urljoin`  
- 默认 `timeout`：支持命令行 `--timeout` 覆盖，无需每个请求手动传  
- 日志 & Allure 附件：
  - Request：method/url/headers/json/data（敏感字段统一脱敏）
  - Response Meta：status_code/elapsed_ms/headers/url
  - Response Body：优先 JSON，异常时回退到 text
- 敏感字段脱敏：`password/token/authorization` 等字段自动替换为 `***`，防止日志和报告泄漏敏感信息
- `set_token(token, scheme="Bearer")`：统一注入 Authorization header

### 3. Auth 模块测试设计（登录/鉴权/刷新）

- **登录场景（`test_login_cases` + YAML）**
  - 覆盖：
    - 登录成功（示例账号）
    - 密码错误
    - 用户名不存在
    - 用户名/密码为空串
    - 缺少字段
    - 类型错误（数字类型用户名/密码）
  - 断言：
    - 状态码 == 预期  
    - 根据 YAML 中的 `has_token` 判断 token 存在性（兼容 `token/accessToken`）  
    - 正向用例校验 username 一致  
    - 负向用例 message 包含关键字（大小写不敏感，如 `"invalid"`、`"username"`）

- **核心登录链路（smoke）**
  - `test_login_success`：单条快速验证登录接口可用  
  - `test_get_me_after_login`：在已登录 session 下访问 `/auth/me`，验证返回当前用户信息（`id/username/email`）

- **未登录访问 `/auth/me`（negative）**
  - `test_get_me_without_login`：验证未授权访问受保护资源时返回 4xx

- **刷新 token 场景（`test_refresh_cases` + YAML）**
  - 通过 `pre_login + fake_token + expect` 组合：
    - 已登录有效 token 刷新成功
    - 未登录、无 token 刷新失败
    - 伪造 token、模拟过期 token 行为（根据 DummyJSON 实际行为调整期望）
  - 刷新成功时：
    - 从响应中取出新 token  
    - 写回 Session  
    - 再调 `/auth/me` 验证新 token 真的可用

### 4. 商品模块测试设计（搜索/分页/分类链路）

- **搜索场景（`test_search_products` + `PRODUCT_search_cases.yaml`）**
  - 典型用例：
    - 关键词：`iphone`、`samsung`、模糊 `phone`
    - 边界 limit：1、超过系统上限
    - 特殊字符 / 不存在关键词返回 0
  - YAML 字段：
    - `keyword` / `limit`
    - `expect.min_total`：`total >= min_total`
    - `expect.max_limit`：`len(products) <= max_limit`
    - `expect.total`：精确 total，例如 0 结果
    - `expect.has_field`：第一条商品需包含的字段（如 `title/price`）

- **分类到详情链路（小 E2E 流程）**
  - 先请求 `/products/category/{category}` 获取某分类下产品列表  
  - 选取其中一个产品的 `id/title`  
  - 再请求 `/products/{id}` 获取详情，对比 `id/title` 一致性

- **写操作（Demo 接口）**
  - 针对 `/products/add`、`/products/{id}` 删除等接口，验证 Demo 环境下的响应结构和状态码，并在注释中说明"不是真实 CRUD，仅供演示"。

### 5. Fiddler Mock / 弱网注入预埋

为了支持在本地通过 Fiddler 做 Mock/弱网测试，框架在 fixture 中预埋了 header 开关：

- `--proxy --insecure`：让所有请求通过 `127.0.0.1:8888` 代理，并关闭证书校验（用于 HTTPS 解密）
- `product_api_empty_list`：
  - 在 Session header 增加 `X-Mock-Scenario: products_empty`
  - 可通过 FiddlerScript 检测该 header 并对 `/products/search` 返回固定空列表
- `product_api_slow`：
  - 在 Session header 增加 `X-Simulate-SlowNet: true`
  - 可在 FiddlerScript 中对该请求加 trickle-delay/限速，模拟弱网

搭配 `@pytest.mark.need_fiddler` 标记相关用例，可实现金融/前端项目常用的：

- 空数据/异常数据 Mock
- 慢网/弱网下的接口和前端健壮性验证

---

## 📊 测试报告 & 日志

- 日志目录：`logs/`，按日期滚动记录每次运行的请求/响应摘要及错误堆栈。
- Allure 报告：
  - 每个测试用例按业务场景分多个 step（例如"登录"、"搜索商品"、"加入购物车"、"刷新 token"等）。
  - 每个 step 中附带：
    - Request：method/url/headers/body（已脱敏）
    - Response Meta：status/耗时/headers
    - Response Body：JSON 或 text

---

## 运行测试

**默认运行（dev 环境）：**

```bash
pytest
```bash

**指定环境：**

```bash
pytest --env=test
```bash
