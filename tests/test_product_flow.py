import pytest
import random
import allure
from utils.yaml_util import load_yaml


search_cases = load_yaml('data/PRODUCT_product_cases.yaml')


@allure.feature("商品管理模块")
class TestProductFlow:

    @allure.story("获取所有商品")
    def test_get_all_products(self, product_api):
        res = product_api.get_all_products()
        assert res.status_code == 200

        # 断言 products 列表存在且不为空
        products = res.json().get("products", [])
        assert len(products) > 0

        # 默认 limit 是 30
        assert len(products) == 30

    @allure.story("获取单个商品")
    def test_get_single_product(self, product_api):
        # 随机找一个 ID (1-30之间)
        p_id = random.randint(1, 30)

        res = product_api.get_single_product(p_id)

        assert res.status_code == 200
        data = res.json()
        assert data['id'] == p_id
        assert "title" in data

    @allure.story("商品搜索")
    @pytest.mark.parametrize('case', search_cases, ids=[c['case_name'] for c in search_cases])
    def test_search_products(self, product_api, case):
        keyword = case['keyword']
        limit = case['limit']
        expect = case['expect']

        with allure.step(f"keyword: {keyword}, limit: {limit}"):
            res = product_api.search_products(keyword, limit)

        assert res.status_code == 200
        res_json = res.json()

        # 提取 products 列表
        products = res_json.get("products", [])

        # 检查 expect 字典里的 key
        if 'max_limit' in expect:
            assert len(products) <= expect['max_limit']

        if 'min_total' in expect:
            assert res_json['total'] >= expect['min_total']

        if 'has_field' in expect and products:
            assert expect['has_field'] in products[0]

    @allure.story("商品分页查询")
    @pytest.mark.parametrize("limit, skip, select", [
        (10, 0, ["title", "price"]),  # 查前10个，看标题价格
        (5, 5, ["id"]),  # 跳过前5个，取5个，看ID
        (0, 0, None)  # 全量查询
    ])
    def test_limit_skip_products(self, product_api, limit, skip, select):
        res = product_api.limit_skip_products(limit, skip, select)
        assert res.status_code == 200
        products = res.json().get("products", [])

        # 验证 limit
        if limit != 0:
            assert len(products) <= limit

        # 验证 select
        if select and products:
            first_item_keys = set(products[0].keys())
            for field in select:
                assert field in first_item_keys

    @allure.story("商品排序")
    @pytest.mark.parametrize("sort_by, order", [
        ("price", "asc"),
        ("title", "desc"),
        ("rating", "asc")
    ])
    def test_sort_products(self, product_api, sort_by, order):
        res = product_api.sort_products(sort_by, order)
        assert res.status_code == 200
        products = res.json().get("products", [])
        assert len(products) > 0

    @allure.story("商品分类链路测试")
    def test_category_workflow(self, product_api):
        """
        获取分类 -> 随机选一个 -> 查该分类商品
        """
        # 获取分类
        with allure.step("获取所有分类列表"):
            res_cat = product_api.get_all_categories()
            assert res_cat.status_code == 200
            categories = res_cat.json()
            # 不硬编码对比 list，而是验证结构
            assert isinstance(categories, list)
            assert len(categories) > 0

        # 随机选一个
        target_category = random.choice(categories)

        # 容错处理
        if isinstance(target_category, dict):
            target_category = target_category['slug']

        # 查该分类
        with allure.step(f"查询分类: {target_category}"):
            res_pro = product_api.get_products_by_category(target_category)
            assert res_pro.status_code == 200
            products = res_pro.json().get("products", [])
            assert len(products) > 0
            # 验证返回的每个商品 category 字段确实是目标分类
            assert products[0]['category'] == target_category

    @allure.story("添加商品(Mock)")
    def test_add_a_new_product(self, product_api):
        payload = {'title': 'New Phone', 'description': 'Best phone ever'}
        res = product_api.add_a_new_product(payload)
        assert res.status_code in [200, 201]
        assert res.json()['title'] == payload['title']
        # 验证产生了新 ID
        assert res.json().get('id') is not None

    @allure.story("删除商品(Mock)")
    def test_delete_a_product(self, product_api):
        res = product_api.delete_a_product(1)
        assert res.status_code == 200
        data = res.json()
        assert data['isDeleted'] is True
        assert data['deletedOn'] is not None