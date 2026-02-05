from apis.base_api import BaseApi


class RecipeApi(BaseApi):
    def __init__(self, base_url, session=None):
        super().__init__(base_url, session)

    def get_all_recipes(self):
        """GET /recipes"""
        return self.request("GET", "/recipes")

    def get_a_single_recipe(self, recipe_id):
        """GET /recipes/{recipe_id}"""
        return self.request("GET", f"/recipes/{recipe_id}")

    def search_recipes(self, keyword, limit=None, skip=None):
        """GET /recipes/search"""
        params = {'q': keyword}
        if limit is not None: params['limit'] = limit
        if skip is not None: params['skip'] = skip
        return self.request("GET", "/recipes/search", params=params)

    def limit_skip_recipe(self, limit=None, skip=None, select=None):
        """GET /recipes"""
        params = {}
        if limit is not None: params['limit'] = limit
        if skip is not None: params['skip'] = skip

        if select:
            params['select'] = ",".join(select) if isinstance(select, list) else select

        return self.request("GET", "/recipes", params=params)

    def sort_recipes(self, sort_by, order="asc"):
        """GET /recipes"""
        params = {
            "sortBy": sort_by,
            "order": order
        }
        return self.request("GET", "/recipes", params=params)

    def get_all_recipes_tag(self):
        """GET /recipes/tags"""
        return self.request(method="GET", url="/recipes/tags")

    def get_recipes_by_a_tag(self, tag):
        """GET /recipes/tag/{tag}"""
        return self.request(method="GET", url=f"/recipes/tag/{tag}")

    def get_recipes_by_a_meal(self, meal):
        """GET /recipes/meal-type/{meal}"""
        return self.request(method="GET", url=f"/recipes/meal-type/{meal}")

    def add_recipe(self, payload):
        """POST /recipes/add"""
        return self.request(method="POST", url=f"/recipes/add", json=payload)

    def update_recipe(self, recipe_id, payload):
        """PUT /recipes/{recipe_id}"""
        return self.request(method='PUT', url=f"/recipes/{recipe_id}",json=payload)

    def delete_recipe(self, recipe_id):
        """DELETE /recipes/{recipe_id}"""
        return self.request(method="DELETE", url=f"/recipes/{recipe_id}")


