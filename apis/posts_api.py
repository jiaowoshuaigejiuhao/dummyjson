from apis.base_api import BaseApi


class PostsApi(BaseApi):
    def __init__(self, base_url, session=None):
        super().__init__(base_url, session)

    def get_all_posts(self):
        """GET /posts"""
        return self.request("GET", "/posts")

    def get_a_single_post(self, post_id):
        """GET /posts/{id}"""
        return self.request("GET", f"/posts/{post_id}")

    def search_posts(self, keyword):
        """GET /posts/search?q={keyword}"""
        params = {'q': keyword}
        return self.request("GET", "/posts/search", params=params)

    def limit_skip_posts(self, limit=None, skip=None, select=None):
        """GET /posts?limit=..&skip=..&select=.."""
        params = {}
        if limit is not None: params['limit'] = limit
        if skip is not None: params['skip'] = skip

        if select:
            params['select'] = ",".join(select) if isinstance(select, list) else select

        return self.request("GET", "/posts", params=params)

    def sort_posts(self, sort_by, order="asc"):
        """GET /posts?sortBy=..&order=.."""
        params = {'sortBy': sort_by, 'order': order}
        return self.request("GET", "/posts", params=params)

    def get_all_post_tags(self):
        """GET /posts/tags"""
        return self.request("GET", "/posts/tags")

    def get_posts_by_tag(self, tag):
        """GET /posts/tag/{tag}"""
        return self.request("GET", f"/posts/tag/{tag}")

    def get_post_comments(self, post_id):
        """GET /posts/{id}/comments"""
        return self.request("GET", f"/posts/{post_id}/comments")

    def add_post(self, payload):
        """POST /posts/add"""
        return self.request("POST", "/posts/add", json=payload)

    def update_post(self, post_id, payload):
        """PUT /posts/{id}"""
        return self.request("PUT", f"/posts/{post_id}", json=payload)

    def delete_post(self, post_id):
        """DELETE /posts/{id}"""
        return self.request("DELETE", f"/posts/{post_id}")