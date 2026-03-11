import os
import sys
import pytest
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.yaml_util import load_yaml
from utils.log_util import logger

from apis.auth_api import AuthApi
from apis.product_api import ProductApi
from apis.cart_api import CartApi
from apis.recipes_api import RecipeApi
from apis.posts_api import PostsApi
from apis.users_api import UsersApi
from apis.comments_api import CommentApi
from apis.todos_api import TodoApi


# ---------- CLI Options ----------
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev", help="环境选择: dev/test")
    parser.addoption("--baseurl", action="store", default=None, help="临时覆盖 base_url")
    parser.addoption("--proxy", action="store_true", default=False, help="通过 Fiddler 代理抓包(127.0.0.1:8888)")
    parser.addoption("--insecure", action="store_true", default=False, help="关闭 SSL 校验(配合代理/HTTPS 抓包)")
    parser.addoption("--timeout", action="store", type=float, default=10.0, help="requests timeout(秒)")


# ---------- Config ----------
@pytest.fixture(scope="session")
def env(request) -> str:
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def config(env, request) -> dict:
    config_path = os.path.join(BASE_DIR, "config", "env.yaml")
    all_cfg = load_yaml(config_path)

    if env not in all_cfg:
        raise KeyError(f"env.yaml 中未找到环境: {env}, 当前可用: {list(all_cfg.keys())}")

    cfg = all_cfg[env]

    # 支持命令行覆盖 base_url
    base_url_override = request.config.getoption("--baseurl")
    if base_url_override:
        cfg["base_url"] = base_url_override

    return cfg


@pytest.fixture(scope="session")
def base_url(config) -> str:
    return config["base_url"]


# ---------- Session Factory ----------
@pytest.fixture(scope="session")
def session_factory(request):
    """
    统一管理 Session 的创建
    """
    use_proxy = request.config.getoption("--proxy")
    insecure = request.config.getoption("--insecure")

    def _create() -> requests.Session:
        s = requests.Session()

        if use_proxy:
            s.proxies.update({
                "http": "http://127.0.0.1:8888",
                "https": "http://127.0.0.1:8888",
            })
            logger.info("Proxy enabled: 127.0.0.1:8888 (Fiddler)")

        if insecure:
            s.verify = False
            logger.warning("SSL verify disabled (--insecure). Only for local debug/proxy.")

        return s

    return _create


@pytest.fixture(scope="session")
def shared_session(session_factory):
    """
    回归专用：全局共享 Session
    """
    s = session_factory()
    yield s
    s.close()


@pytest.fixture(scope="function")
def clean_session(session_factory):
    """
    负向/隔离专用：每条用例一个干净 Session
    """
    s = session_factory()
    yield s
    s.close()


# ---------- Auth ----------
@pytest.fixture(scope="session")
def auth_credentials(config) -> tuple[str, str]:
    # 用 env.yaml 配置；没有就给默认值
    username = config.get("username", "emilys")
    password = config.get("password", "emilyspass")
    return username, password


@pytest.fixture(scope="session")
def auth_api_shared(base_url, shared_session, request):
    timeout = request.config.getoption("--timeout")
    return AuthApi(base_url=base_url, session=shared_session, timeout=timeout)


@pytest.fixture(scope="session")
def logged_in_auth_api(auth_api_shared, auth_credentials, request):
    """
    业务回归专用：session 级别登录一次
    """
    username, password = auth_credentials
    res = auth_api_shared.login(username, password)

    if res.status_code != 200:
        logger.error(f"全局登录失败: status={res.status_code}, body={res.text}")
    assert res.status_code == 200, f"全局登录失败: status={res.status_code}, body={res.text}"

    return auth_api_shared


@pytest.fixture(scope="function")
def auth_api(base_url, clean_session, request):
    timeout = request.config.getoption("--timeout")
    return AuthApi(base_url=base_url, session=clean_session, timeout=timeout)


@pytest.fixture(scope="session")
def api_factory(base_url, shared_session, logged_in_auth_api, request):
    timeout = request.config.getoption("--timeout")

    def _factory(api_cls):
        return api_cls(base_url=base_url, session=shared_session, timeout=timeout)

    return _factory


@pytest.fixture(scope="session")
def product_api(api_factory):
    return api_factory(ProductApi)


@pytest.fixture(scope="session")
def cart_api(api_factory):
    return api_factory(CartApi)


@pytest.fixture(scope="session")
def recipes_api(api_factory):
    return api_factory(RecipeApi)


@pytest.fixture(scope="session")
def users_api(api_factory):
    return api_factory(UsersApi)


@pytest.fixture(scope="session")
def posts_api(api_factory):
    return api_factory(PostsApi)


@pytest.fixture(scope="session")
def comment_api(api_factory):
    return api_factory(CommentApi)

@pytest.fixture(scope="session")
def todo_api(api_factory):
    return api_factory(TodoApi)

@pytest.fixture(scope="session")
def product_api_empty_list(api_factory):
    """
    带 Mock header 的 ProductApi，用于触发 Fiddler 中配置的空列表场景
    """
    api = api_factory(ProductApi)
    api.session.headers.update({"X-Mock-Scenario": "products_empty"})
    return api

@pytest.fixture(scope="session")
def product_api_slow(api_factory):
    """
    带弱网标记的 ProductApi，用于在 FiddlerScript 中加 trickle-delay
    """
    api = api_factory(ProductApi)
    api.session.headers.update({"X-Simulate-SlowNet": "true"})
    return api

#--------mock和弱网----------
def _with_extra_headers(api, headers: dict):
    """
    给已有 Api 对象增加一些全局 header（Mock/弱网开关）
    """
    api.session.headers.update(headers)
    return api

@pytest.fixture(scope="session")
def product_api_empty_list(api_factory):
    """
    带 Mock header 的 ProductApi，用于触发 Fiddler 配置的“空列表”场景
    """
    api = api_factory(ProductApi)
    return _with_extra_headers(api, {"X-Mock-Scenario": "products_empty"})


@pytest.fixture(scope="session")
def product_api_slow(api_factory):
    """
    带弱网 header 的 ProductApi，用于在 FiddlerScript 中加 delay/限速
    """
    api = api_factory(ProductApi)
    return _with_extra_headers(api, {"X-Simulate-SlowNet": "true"})