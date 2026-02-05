import pytest
import random
import allure
import jsonpath


@allure.feature("待办事项(Todo)模块")
class TestTodoFlow:

    @allure.story("获取所有待办")
    def test_get_all_todos(self, todo_api):
        res = todo_api.get_all_todos()
        assert res.status_code == 200

        data = res.json()
        assert len(data['todos']) > 0
        assert data['total'] > 0
        # 默认 limit 是 30
        assert len(data['todos']) == 30

    @allure.story("获取单个待办")
    def test_get_a_single_todo(self, todo_api):

        todo_id = random.randint(1, 150)
        res = todo_api.get_a_single_todo(todo_id)

        if res.status_code == 404:
            pytest.skip(f"Todo ID {todo_id} not found")

        assert res.status_code == 200
        data = res.json()
        assert data['id'] == todo_id
        assert data['todo'] is not None

        assert isinstance(data['completed'], bool)

    @allure.story("获取随机待办")
    def test_get_random_todo(self, todo_api):
        res = todo_api.get_random_todo()
        assert res.status_code == 200
        data = res.json()
        assert 'id' in data
        assert 'todo' in data

    @allure.story("分页查询")
    @pytest.mark.parametrize("limit, skip", [
        (5, 0),
        (10, 5),
        (0, 0)
    ])
    def test_limit_skip_todos(self, todo_api, limit, skip):
        res = todo_api.limit_skip_todos(limit, skip)
        assert res.status_code == 200

        todos = res.json().get('todos', [])

        if limit != 0:
            assert len(todos) <= limit

    @allure.story("获取用户的待办 (闭环验证)")
    def test_get_todos_by_user_id(self, todo_api):

        all_res = todo_api.get_all_todos()
        all_todos = all_res.json().get('todos', [])

        target_todo = random.choice(all_todos)
        target_user_id = target_todo['userId']

        with allure.step(f"查询用户 {target_user_id} 的待办列表"):

            res = todo_api.get_todos_by_user_id(target_user_id)
            assert res.status_code == 200

            user_todos = res.json().get('todos', [])
            assert len(user_todos) > 0


            for todo in user_todos:
                assert todo['userId'] == target_user_id

    @allure.story("添加待办(Mock)")
    def test_add_todo(self, todo_api):
        payload = {
            "todo": "Finish the API automation framework",
            "completed": False,
            "userId": 5
        }
        res = todo_api.add_todo(payload)
        assert res.status_code in [200, 201]

        data = res.json()
        assert data['todo'] == payload['todo']
        assert data['completed'] is False
        assert data['userId'] == 5

    @allure.story("更新待办(Mock)")
    def test_update_todo(self, todo_api):
        todo_id = 1

        payload = {"completed": True}

        res = todo_api.update_todo(todo_id, payload)
        assert res.status_code == 200

        data = res.json()
        assert data['completed'] is True
        assert data['id'] == todo_id

    @allure.story("删除待办(Mock)")
    def test_delete_todo(self, todo_api):
        todo_id = 1
        res = todo_api.delete_todo(todo_id)
        assert res.status_code == 200

        data = res.json()
        assert data['isDeleted'] is True
        assert data['deletedOn'] is not None