import pytest
import allure
import re
from apis.auth_api import AuthApi
from utils.log_util import logger
from utils.yaml_util import load_yaml

login_cases = load_yaml("data/AUTH_login_cases.yaml")
refresh_cases = load_yaml("data/AUTH_refresh_cases.yaml")


@allure.feature("用户认证模块")
class TestAuthFlow:

    @allure.story("登录场景")
    @pytest.mark.parametrize("case", login_cases, ids=[c['case_name'] for c in login_cases])
    def test_login_cases(self, auth_api, case):
        """
        使用auth_api测试登录
        断言：
            - 状态码
            - Token 存在性
            - 错误信息
        """
        payload = case['payload']
        expect = case['expect']

        res = auth_api.login(payload.get('username'), payload.get('password'))

        # 断言状态码
        assert res.status_code == expect['status_code']

        # 断言 Token 存在性
        data = res.json()
        has_token = 'accessToken' in data
        assert has_token == expect['has_token']

        # 断言错误信息
        if expect.get('error_msg_contains'):
            msg = data.get('message', '')
            assert re.search(expect['error_msg_contains'],
                             msg), logger.debug(f"Error msg '{msg}' not match '{expect['error_msg_contains']}'")

    @allure.story("获取个人信息-未登录")
    def test_get_me_without_login(self, auth_api):
        """
        未登录直接调接口
        断言：
            - 状态码
            - 错误提示
        """
        res = auth_api.get_me()
        assert res.status_code == 401
        # 断言错误提示
        assert "Access Token" in res.json().get("message", "")

    @allure.story("获取个人信息-登录后")
    def test_get_me_after_login(self, logged_in_auth_api, config):
        """
        使用 logged_in_auth_api
        验证登录态是否有效
        断言：
            - 返回的是当前登录用户
        """
        res = logged_in_auth_api.get_me()
        assert res.status_code == 200

        data = res.json()
        # 验证返回的是当前登录用户
        assert data['username'] == config['username']


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