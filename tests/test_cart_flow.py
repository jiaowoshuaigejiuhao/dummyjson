import random

import jsonpath


class TestCartFlow:
    def test_get_all_carts(self, cart_api):
        res = cart_api.get_all_carts()
        data = res.json()
        assert res.status_code == 200
        assert len(data['carts']) > 0
        assert len(data['carts']) ==data['limit']
        assert len(data['carts']) <= data['total']

    def test_get_a_single_cart(self, cart_api):
        cart_id = random.randint(1, 30)
        res = cart_api.get_a_single_cart(cart_id)
        data = res.json()
        assert res.status_code == 200
        assert data['id'] == cart_id

    def test_add_a_new_cart(self, cart_api):
        user_id = random.randint(1, 30)
        payload = {
        "userId": user_id,
        "products": [
          {
            "id": 1,
            "quantity": 4,
          },
          {
            "id": 9,
            "quantity": 9,
          },
        ]
      }
        res = cart_api.add_a_new_cart(payload)
        data = res.json()
        assert res.status_code in [200, 201]
        assert data['userId'] == user_id
        assert len(data['products']) == len(payload['products'])
        product_ids = jsonpath.jsonpath(data, '$.products[*].id')
        for item in payload['products']:
            assert item['id'] in product_ids
            quantity = jsonpath.jsonpath(data, f"$.products[?(@.id=={item['id']})].quantity")
            assert quantity[0] == item['quantity']

    def test_update_a_cart(self, cart_api):
        cart_id = random.randint(1, 30)
        payload = {
        "merge": True,
        "products": [
          {
            "id": 1,
            "quantity": 1,
          },
        ]
      }
        res = cart_api.update_a_cart(cart_id, payload)
        data =res.json()
        assert res.status_code in [200, 201]
        assert data['id'] == cart_id

    def test_delete_a_cart(self, cart_api):
        cart_id = random.randint(1, 30)
        res = cart_api.delete_a_cart(cart_id)
        data = res.json()
        assert res.status_code in [200, 201]
        assert data['isDeleted'] == True
        assert data['deletedOn'] is not None