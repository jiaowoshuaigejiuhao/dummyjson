import jsonpath

from apis.base_api import BaseApi

class CartApi(BaseApi):
    """
    购物车模块封装
    """
    def __init__(self, base_url, session=None):
        super().__init__(base_url, session)

    def get_all_carts(self):
        """GET /carts"""
        return self.request('get', '/carts')

    def get_a_single_cart(self, cart_id):
        """GET /carts/{cart_id}"""
        return self.request('get', f'/carts/{cart_id}')

    def add_a_new_cart(self, payload):
        """POST /carts/add"""
        return self.request('post', '/carts/add', json=payload)

    def update_a_cart(self, cart_id, payload):
        """PUT /carts/{cart_id}"""
        return self.request('put', f'/carts/{cart_id}',json=payload)

    def delete_a_cart(self, cart_id):
        """DELETE /carts/{cart_id}"""
        return self.request('delete', f'/carts/{cart_id}')


add_payload = {
    "userId": 1,
    "products": [
      {
        "id": 1,
        "quantity": 2,
      },
      {
        "id": 98,
        "quantity": 1,
      },
    ]
  }
update_payload = {
    "merge": True,
    "products": [
      {
        "id": 1,
        "quantity": 1,
      },
    ]
  }
