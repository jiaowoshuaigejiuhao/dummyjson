from apis.base_api import BaseApi


class ProductApi(BaseApi):
    """
    商品模块接口封装
    crud服务器只会mock
    """
    def __init__(self, base_url, session):
        super().__init__(base_url, session)

    def get_all_products(self):
        """GET /products"""
        return self.request("GET", "/products")

    def get_single_product(self, product_id: int):
        """GET /products/{id}"""
        return self.request("GET", f"/products/{product_id}")

    def search_products(self, keyword, limit=None):
        """GET /products/search"""
        params = {"q": keyword}
        if limit is not None:
            params["limit"] = limit
        return self.request("GET", "/products/search", params=params)

    def limit_skip_products(self, limit: int, skip: int, select: list = None):
        """
        GET /products?limit={}&skip={}&select={}
        """
        params = {
            "limit": limit,
            "skip": skip
        }
        if select:
            # 关键修正：将 list 转为逗号分隔字符串，例如 "title,price"
            params["select"] = ",".join(select) if isinstance(select, list) else select

        return self.request("GET", "/products", params=params)

    def sort_products(self, sort_by: str, order: str = "asc"):
        """GET /products?sortBy={}&order={}"""
        params = {
            "sortBy": sort_by,
            "order": order
        }
        return self.request("GET", "/products", params=params)

    def get_all_categories(self):
        """GET /products/categories (获取分类列表)"""
        return self.request("GET", "/products/categories")

    def get_products_category_list(self):
        """
        GET /products/category-list
        """
        return self.request("GET", "/products/category-list")

    def get_products_by_category(self, category):
        """GET /products/category/{category}"""
        return self.request("GET", f"/products/category/{category}")

    def add_a_new_product(self, payload: dict):
        """POST /products/add"""
        return self.request("POST", "/products/add", json=payload)

    def update_a_product(self, product_id, payload: dict):
        """PUT /products/{product_id}"""
        return self.request("PUT", f"/products/{product_id}", json=payload)

    def delete_a_product(self, product_id):
        """DELETE /products/{product_id}"""
        return self.request("DELETE", f"/products/{product_id}")