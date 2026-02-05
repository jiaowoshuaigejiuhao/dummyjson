import pytest
import random
import allure


@allure.feature("用户管理模块")
class TestUserFlow:

    @allure.story("获取所有用户")
    def test_get_all_users(self, users_api):
        res = users_api.get_all_users()
        assert res.status_code == 200

        data = res.json()
        users = data.get("users", [])
        assert len(users) > 0
        assert data['total'] > 0
        assert len(users) == 30

    @allure.story("获取单个用户")
    def test_get_a_single_user(self, users_api):
        user_id = random.randint(1, 100)
        res = users_api.get_a_single_user(user_id)
        assert res.status_code == 200

        data = res.json()
        assert data['id'] == user_id
        assert data['firstName'] is not None
        assert data['email'] is not None

    @allure.story("搜索用户")
    def test_search_users(self, users_api):
        user_list = users_api.get_all_users().json()['users']
        target_name = user_list[0]['firstName']

        res = users_api.search_users(target_name)
        assert res.status_code == 200

        search_results = res.json()['users']
        assert len(search_results) > 0
        # 验证结果里确实包含这个名字
        assert target_name in search_results[0]['firstName']

    @allure.story("筛选用户 (Filter)")
    def test_filter_users(self, users_api):
        # 筛选头发颜色为 Brown 的人
        key = "hair.color"
        value = "Brown"

        res = users_api.filter_users(key, value)
        assert res.status_code == 200

        filtered_users = res.json()['users']
        assert len(filtered_users) > 0

        # 验证结果确实都是 Brown
        for user in filtered_users:
            assert user['hair']['color'] == value

    @allure.story("用户分页与字段选择")
    @pytest.mark.parametrize("limit, skip, select", [
        (5, 0, ["firstName", "age"]),  # 只看名字和年龄
        (10, 10, ["email"]),  # 翻页
    ])
    def test_limit_skip_users(self, users_api, limit, skip, select):
        res = users_api.limit_skip_users(limit, skip, select)
        assert res.status_code == 200

        users = res.json()['users']
        assert len(users) <= limit

        if select and users:
            user_keys = users[0].keys()
            for field in select:
                assert field in user_keys

    @allure.story("用户排序")
    @pytest.mark.parametrize("sort_by, order", [
        ("age", "asc"),
        ("height", "desc")
    ])
    def test_sort_users(self, users_api, sort_by, order):
        res = users_api.sort_users(sort_by, order)
        assert res.status_code == 200
        assert len(res.json()['users']) > 0

    @allure.story("用户关联数据查询 (Carts/Posts/Todos)")
    def test_user_related_data(self, users_api):
        """
        一次性测试用户的关联数据：购物车、帖子、待办事项
        """
        user_id = 5

        with allure.step("查用户购物车"):
            res = users_api.get_users_carts(user_id)
            assert res.status_code == 200
            assert "carts" in res.json()

        with allure.step("查用户帖子"):
            res = users_api.get_users_posts(user_id)
            assert res.status_code == 200
            posts = res.json().get("posts", [])
            if posts:
                assert posts[0]['userId'] == user_id

        with allure.step("查用户待办"):
            res = users_api.get_users_todos(user_id)
            assert res.status_code == 200
            todos = res.json().get("todos", [])
            if todos:
                assert todos[0]['userId'] == user_id

    @allure.story("添加用户(Mock)")
    def test_add_user(self, users_api):
        payload = {
            "firstName": "Test",
            "lastName": "User",
            "age": 25,
        }
        res = users_api.add_user(payload)
        # 200 或 201
        assert res.status_code in [200, 201]

        data = res.json()
        assert data['firstName'] == "Test"
        assert data['id'] is not None

    @allure.story("更新用户(Mock)")
    def test_update_user(self, users_api):
        user_id = 1
        payload = {"age": 100}

        res = users_api.update_user(user_id, payload)
        assert res.status_code == 200

        data = res.json()
        assert data['age'] == 100
        assert data['id'] == user_id

    @allure.story("删除用户(Mock)")
    def test_delete_user(self, users_api):
        user_id = 1
        res = users_api.delete_user(user_id)
        assert res.status_code == 200

        data = res.json()
        assert data['isDeleted'] is True
        assert data['deletedOn'] is not None