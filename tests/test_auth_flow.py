import pytest
import allure
import re
from apis.auth_api import AuthApi
from utils.log_util import logger
from utils.yaml_util import load_yaml

login_cases = load_yaml("data/AUTH_login_cases.yaml")
refresh_cases = load_yaml("data/AUTH_refresh_cases.yaml")

@allure.feature("鉴权模块")
@allure.suite("Auth Flow")
@pytest.mark.nondestructive
class TestAuthFlow:

    @allure.story("登录用例集（正向+负向）")
    @pytest.mark.parametrize("case", login_cases, ids=[c["case_name"] for c in login_cases])
    def test_login_cases(self, auth_api, case):
        """
        使用 auth_api 测试登录场景（由 YAML 数据驱动）
        断言：
          - 状态码
          - Token 存在性（accessToken/token）
          - 正向用例：用户名一致
          - 负向用例：错误信息包含指定关键字（可选）
        """
        payload = case["payload"]
        expect = case["expect"]

        username = payload.get("username")
        password = payload.get("password")

        with allure.step(f"登录用例: {case['case_name']}"):
            res = auth_api.login(username, password)

        # 1. 状态码断言
        assert res.status_code == expect["status_code"], (
            f"{case['case_name']}: expected status {expect['status_code']}, "
            f"got {res.status_code}, body={res.text}"
        )

        # 2. 解析 JSON
        try:
            data = res.json()
        except ValueError:
            data = {}

        # 3. Token 存在性
        token = data.get("accessToken") or data.get("token")
        has_token = bool(token)
        assert has_token == expect["has_token"], (
            f"{case['case_name']}: expected has_token={expect['has_token']}, "
            f"got {has_token}, body={data}"
        )

        # 4. 正向用例
        if expect.get("username") and has_token:
            assert data.get("username") == expect["username"], (
                f"{case['case_name']}: expected username={expect['username']}, "
                f"got {data.get('username')}"
            )

        # 5. 负向用例
        error_pattern = expect.get("error_msg_contains")
        if error_pattern:
            msg_raw = str(data.get("message", ""))
            msg = msg_raw.lower()
            pattern = error_pattern.lower()

            if pattern not in msg:
                logger.debug(
                    f"{case['case_name']}: error msg '{msg_raw}' "
                    f"not contains '{error_pattern}'"
                )

            assert pattern in msg, (
                f"{case['case_name']}: error msg '{msg_raw}' "
                f"not contains '{error_pattern}'"
            )

    @allure.story("核心登录成功场景")
    @pytest.mark.smoke
    def test_login_success(self, auth_api):
        """
        单条核心登录用例，独立于 YAML 方便 smoke 快速验证环境
        """
        username = "sophiab"
        password = "sophiabpass"

        res = auth_api.login(username, password)
        assert res.status_code == 200, f"login failed, status={res.status_code}, body={res.text}"

        data = res.json()
        token = data.get("accessToken") or data.get("token")
        assert token, "登录成功但未返回 token"
        assert data.get("username") == username

    @allure.story("未登录访问 /auth/me")
    @pytest.mark.negative
    def test_get_me_without_login(self, auth_api):
        """
        负向用例：未登录直接访问 /auth/me，应返回未授权错误
        """
        res = auth_api.get_me()

        assert res.status_code in (400, 401, 403), (
            f"expected 4xx for unauthenticated /auth/me, "
            f"got {res.status_code}, body={res.text}"
        )

        try:
            data = res.json()
        except ValueError:
            data = {}


    @allure.story("已登录访问 /auth/me")
    @pytest.mark.smoke
    def test_get_me_after_login(self, logged_in_auth_api, auth_credentials):
        """
        正向用例：在已登录会话下访问 /auth/me，返回当前用户信息
        """
        res = logged_in_auth_api.get_me()
        assert res.status_code == 200, f"/auth/me failed, status={res.status_code}, body={res.text}"

        data = res.json()
        # 简单字段存在性检查
        for key in ("id", "username", "email"):
            assert key in data, f"Key '{key}' not in /auth/me response: {data}"

        username, _ = auth_credentials
        assert data.get("username") == username


    @allure.story("Token 刷新/无效场景")
    @pytest.mark.parametrize("case", refresh_cases, ids=[c['case_name'] for c in refresh_cases])
    def test_refresh_cases(self, auth_api, config, case):
        """
        使用auth_api 防止污染

        """
        expect = case['expect']

        # 如果需要先登录
        if case.get('pre_login'):
            res = auth_api.login(config['username'], config['password'])

        # 2. 如果需要伪造 Token
        if case.get('fake_token'):
            auth_api.set_token(case['fake_token'])

        # 3. 刷新
        res = auth_api.refresh_token()

        # 4. 断言
        assert res.status_code == expect['status_code']

        if expect['has_token']:
            assert 'accessToken' in res.json()

        # 验证 Token 是否真的可用
        if res.status_code == 200:
            new_token = res.json()['accessToken']
            auth_api.set_token(new_token)  # 更新 fresh session 的 token
            me_res = auth_api.get_me()
            assert me_res.status_code == expect['get_me_status_code']