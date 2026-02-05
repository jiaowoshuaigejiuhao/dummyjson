from apis.base_api import BaseApi


class AuthApi(BaseApi):
    def __init__(self, base_url, session=None):
        """
        鉴权模块疯封装
        接收 session 参数，并传给父类，保证与 ProductApi 共享同一个 Session
        """
        super().__init__(base_url, session)

    def login(self, username, password):
        """POST /auth/login"""
        payload = {
            "username": username,
            "password": password
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