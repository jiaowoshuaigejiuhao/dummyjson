import random
import jsonpath
import pytest
import allure


@allure.feature("食谱模块")
class TestRecipeFlow:

    @allure.story("获取所有食谱")
    def test_get_all_recipes(self, recipes_api):
        res = recipes_api.get_all_recipes()
        assert res.status_code == 200
        data = res.json()
        # 断言列表不为空
        assert len(data['recipes']) > 0
        assert data['total'] > 0

    @allure.story("获取单个食谱")
    def test_get_a_single_recipe(self, recipes_api):
        recipe_id = random.randint(1, 30)
        res = recipes_api.get_a_single_recipe(recipe_id)
        assert res.status_code == 200
        data = res.json()
        assert data['id'] == recipe_id
        assert data['name'] is not None

    @allure.story("搜索食谱")
    def test_search_recipes(self, recipes_api):
        all_res = recipes_api.get_all_recipes()
        all_names = jsonpath.jsonpath(all_res.json(), "$..name")
        keyword = random.choice(all_names) if all_names else "Pizza"

        res = recipes_api.search_recipes(keyword=keyword)
        assert res.status_code == 200
        data = res.json()

        assert len(data['recipes']) > 0
        assert data['total'] > 0
        # 验证搜索结果确实包含 keyword
        assert keyword.lower() in data['recipes'][0]['name'].lower()

    @allure.story("分页与筛选")
    @pytest.mark.parametrize("limit, skip, select", [
        (10, 0, ["name", "mealType"]),
        (5, 5, ["id"]),
        (0, 0, None)
    ])
    def test_limit_skip_recipe(self, recipes_api, limit, skip, select):
        # 修正：调用 limit_skip_recipe 方法
        res = recipes_api.limit_skip_recipe(limit=limit, skip=skip, select=select)
        assert res.status_code == 200
        recipes = res.json().get("recipes", [])

        # 验证 limit
        if limit != 0:
            assert len(recipes) <= limit

        # 验证 select
        if select and recipes:
            first_key = list(recipes[0].keys())
            for field in select:
                assert field in first_key

    @allure.story("排序")
    @pytest.mark.parametrize("sort_by, order", [
        ("rating", "asc"),  # 修正为有效字段
        ("name", "desc"),  # 修正为有效字段
        ("caloriesPerServing", "asc")  # 修正为有效字段
    ])
    def test_sort_recipes(self, recipes_api, sort_by, order):
        res = recipes_api.sort_recipes(sort_by, order)
        assert res.status_code == 200
        assert len(res.json().get('recipes', [])) > 0

    @allure.story("食谱标签")
    def test_get_all_recipes_tag(self, recipes_api):
        res = recipes_api.get_all_recipes_tag()
        assert res.status_code == 200
        assert len(res.json()) > 0

    @allure.story("按标签查食谱")
    def test_get_recipes_by_a_tag(self, recipes_api):
        tags_res = recipes_api.get_all_recipes_tag()
        tags = tags_res.json()
        target_tag = random.choice(tags)

        res = recipes_api.get_recipes_by_a_tag(target_tag)
        assert res.status_code == 200

        data = res.json()
        assert data['total'] > 0
        # 验证返回的食谱里真的有这个 tag
        first_recipe_tags = data['recipes'][0]['tags']
        assert target_tag in first_recipe_tags

    @allure.story("按餐点类型查食谱")
    def test_get_recipes_by_a_meal(self, recipes_api):
        target_meal = 'Snack'
        res = recipes_api.get_recipes_by_a_meal(target_meal)
        assert res.status_code == 200

        data = res.json()
        assert data['total'] > 0
        # 验证
        first_recipe_meals = data['recipes'][0]['mealType']
        assert target_meal in first_recipe_meals

    @allure.story("添加食谱(Mock)")
    @pytest.mark.parametrize("meal_name", [
        'Tasty Pizza',
        'Special Soup'
    ])
    def test_add_recipe(self, recipes_api, meal_name):
        res = recipes_api.add_recipe({"name": meal_name})
        assert res.status_code in [200, 201]
        assert res.json()['name'] == meal_name
        assert res.json().get('id') is not None

    @allure.story("更新食谱(Mock)")
    def test_update_recipe(self, recipes_api):
        recipe_id = 1
        new_name = "Updated Pizza"
        res = recipes_api.update_recipe(recipe_id, {"name": new_name})
        assert res.status_code == 200
        assert res.json()['name'] == new_name

    @allure.story("删除食谱(Mock)")
    def test_delete_recipe(self, recipes_api):
        recipe_id = 1
        res = recipes_api.delete_recipe(recipe_id)
        assert res.status_code == 200
        assert res.json()['isDeleted'] is True