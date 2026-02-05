from apis.base_api import BaseApi

class UsersApi(BaseApi):
    def __init__(self, base_url, session=None):
        super().__init__(base_url, session)

    def get_all_users(self):
        """GET /users"""
        return self.request("GET", "/users")

    def get_a_single_user(self, user_id):
        """GET /users/{user_id}"""
        return self.request("GET", f"/users/{user_id}")

    def search_users(self, keyword):
        """GET /users/search?q={keyword}"""
        params = {'q': keyword}
        return self.request("GET", "/users/search", params=params)

    def filter_users(self, key, value):
        """GET /users/filter?key={key}&value={value}"""
        params = {'key': key, 'value': value}
        return self.request("GET", "/users/filter", params=params)

    def limit_skip_users(self, limit=None, skip=None, select=None):
        """GET /users?limit=..&skip=..&select=.."""
        params = {}
        if limit is not None: params['limit'] = limit
        if skip is not None: params['skip'] = skip
        if select:
            params['select'] = ",".join(select) if isinstance(select, list) else select
        return self.request("GET", "/users", params=params)

    def sort_users(self, sort_by, order="asc"):
        """GET /users?sortBy=..&order=.."""
        params = {'sortBy': sort_by, 'order': order}
        return self.request("GET", "/users", params=params)

    def get_users_carts(self, user_id):
        """GET /users/{id}/carts"""
        return self.request("GET", f"/users/{user_id}/carts")

    def get_users_posts(self, user_id):
        """GET /users/{id}/posts"""
        return self.request("GET", f"/users/{user_id}/posts")

    def get_users_todos(self, user_id):
        """GET /users/{id}/todos"""
        return self.request("GET", f"/users/{user_id}/todos")

    def add_user(self, payload):
        """POST /users/add"""
        return self.request("POST", "/users/add", json=payload)

    def update_user(self, user_id, payload):
        """PUT /users/{id}"""
        return self.request("PUT", f"/users/{user_id}", json=payload)

    def delete_user(self, user_id):
        """DELETE /users/{id}"""
        return self.request("DELETE", f"/users/{user_id}")