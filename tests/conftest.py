import os
import sys
import pytest
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from apis.cart_api import CartApi
from utils.log_util import logger
from utils.yaml_util import load_yaml
from apis.auth_api import AuthApi
from apis.product_api import ProductApi
from apis.recipes_api import RecipeApi
from apis.posts_api import PostsApi
from apis.users_api import UsersApi
from apis.comments_api import CommentApi
from apis.todos_api import TodoApi


def pytest_addoption(parser):
    parser.addoption('--env', action='store', default='dev', help="环境选择: dev / test")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def config(env):
    config_path = os.path.join(BASE_DIR, "config", "env.yaml")
    return load_yaml(config_path)[env]


@pytest.fixture(scope="session")
def global_session():
    """
    全局唯一的 Session 对象,只创建一次
    """
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture(scope="session")
def _auth_api_session(config, global_session):
    """
    仅用于在内部执行登录操作
    """
    return AuthApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="function")
def auth_api(config):
    """
    每次调用创建一个全新的 AuthApi和全新的 Session
    专门用来测试 登录失败、密码错误、Token 过期等
    """
    return AuthApi(base_url=config["base_url"])


@pytest.fixture(scope="session")
def logged_in_auth_api(_auth_api_session, config):
    """
    业务专用
        - 执行过登录的 AuthApi
        - 它持有的 global_session 此时已经含有 Token
    """
    username = config.get("username", "emilys")
    password = config.get("password", "emilyspass")

    res = _auth_api_session.login(username, password)
    assert res.status_code == 200, logger.error("全局登录失败: {res.text}")

    return _auth_api_session


@pytest.fixture(scope="session")
def product_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return ProductApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="session")
def cart_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return CartApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="session")
def recipes_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return RecipeApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="session")
def users_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return UsersApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="session")
def posts_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return PostsApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="session")
def comment_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return CommentApi(base_url=config["base_url"], session=global_session)

@pytest.fixture(scope="session")
def todo_api(config, global_session, logged_in_auth_api):
    """
    业务专用
        - 依赖 logged_in_auth_api，确保已经执行了登录动作
        - 传入 global_session，这个 session 里已有 Token
    """
    return TodoApi(base_url=config["base_url"], session=global_session)