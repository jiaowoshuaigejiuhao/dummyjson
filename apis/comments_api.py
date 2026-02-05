from apis.base_api import BaseApi


class CommentApi(BaseApi):
    def __init__(self, base_url, session=None):
        super().__init__(base_url, session)

    def get_all_comments(self):
        """GET /comments"""
        return self.request("GET", "/comments")

    def get_a_single_comment(self, comment_id):
        """GET /comments/{id}"""
        return self.request("GET", f"/comments/{comment_id}")

    def limit_skip_comments(self, limit=None, skip=None, select=None):
        """GET /comments?limit=..&skip=..&select=.."""
        params = {}
        if limit is not None: params['limit'] = limit
        if skip is not None: params['skip'] = skip

        # 将 list 转为逗号分隔字符串
        if select:
            params['select'] = ",".join(select) if isinstance(select, list) else select

        return self.request("GET", "/comments", params=params)

    def get_comments_by_post_id(self, post_id):
        """GET /comments/post/{postId}"""
        return self.request("GET", f"/comments/post/{post_id}")

    def add_comment(self, payload):
        """
        POST /comments/add
        Payload 需要包含: body, postId, userId
        """
        return self.request("POST", "/comments/add", json=payload)

    def update_comment(self, comment_id, payload):
        """PUT /comments/{id}"""
        return self.request("PUT", f"/comments/{comment_id}", json=payload)

    def delete_comment(self, comment_id):
        """DELETE /comments/{id}"""
        return self.request("DELETE", f"/comments/{comment_id}")