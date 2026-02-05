from apis.base_api import BaseApi

class TodoApi(BaseApi):
    def __init__(self, base_url, session=None):
        super().__init__(base_url, session)

    def get_all_todos(self):
        """GET /todos"""
        return self.request("GET", "/todos")

    def get_a_single_todo(self, todo_id):
        """GET /todos/{id}"""
        return self.request("GET", f"/todos/{todo_id}")

    def get_random_todo(self):
        """GET /todos/random"""
        return self.request("GET", "/todos/random")

    def limit_skip_todos(self, limit=None, skip=None):
        """GET /todos?limit=..&skip=.."""
        params = {}
        if limit is not None: params['limit'] = limit
        if skip is not None: params['skip'] = skip
        return self.request("GET", "/todos", params=params)

    def get_todos_by_user_id(self, user_id):
        """GET /todos/user/{userId}"""
        return self.request("GET", f"/todos/user/{user_id}")

    def add_todo(self, payload):
        """
        POST /todos/add
        """
        return self.request("POST", "/todos/add", json=payload)

    def update_todo(self, todo_id, payload):
        """PUT /todos/{id}"""
        return self.request("PUT", f"/todos/{todo_id}", json=payload)

    def delete_todo(self, todo_id):
        """DELETE /todos/{id}"""
        return self.request("DELETE", f"/todos/{todo_id}")