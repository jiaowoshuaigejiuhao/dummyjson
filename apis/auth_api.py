from apis.base_api import BaseApi


class AuthApi(BaseApi):
    def __init__(self, base_url, session=None, **kwargs):
        """
        Auth 模块 API 封装

        :param base_url: 服务基础地址
        :param session: 可复用的 requests.Session（用于共享登录态）
        :param kwargs: 透传给 BaseApi（如 timeout、重试配置等）
        """
        super().__init__(base_url=base_url, session=session, **kwargs)

    def login(self, username, password):
        """POST /auth/login"""
        payload = {
            "username": username,
            "password": password,
        }
        res = self.request("POST", "/auth/login", json=payload)

        if res.status_code == 200:
            data = res.json()
            token = data.get("accessToken") or data.get("token")
            if token:
                self.set_token(token)
        return res

    def get_me(self):
        """GET /auth/me"""
        return self.request("GET", "/auth/me")

    def refresh_token(self):
        """POST /auth/refresh"""
        return self.request("POST", "/auth/refresh")