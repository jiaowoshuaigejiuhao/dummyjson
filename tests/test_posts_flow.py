import pytest
import random
import allure
import jsonpath


@allure.feature("帖子模块")
class TestPostFlow:

    @allure.story("获取所有帖子")
    def test_get_all_posts(self, posts_api):
        res = posts_api.get_all_posts()
        assert res.status_code == 200

        data = res.json()
        assert len(data['posts']) > 0
        assert data['total'] > 0
        # 默认 limit 30
        assert len(data['posts']) == 30

    @allure.story("获取单个帖子")
    def test_get_a_single_post(self, posts_api):
        post_id = random.randint(1, 150)
        res = posts_api.get_a_single_post(post_id)

        if res.status_code == 404:
            pytest.skip(f"Post ID {post_id} not found")

        assert res.status_code == 200
        data = res.json()
        assert data['id'] == post_id
        assert data['title'] is not None
        assert data['body'] is not None

    @allure.story("搜索帖子")
    def test_search_posts(self, posts_api):
        all_posts = posts_api.get_all_posts().json()['posts']
        target_title = all_posts[0]['title'].split(" ")[0]

        res = posts_api.search_posts(target_title)
        assert res.status_code == 200

        posts = res.json()['posts']
        assert len(posts) > 0

    @allure.story("分页与字段筛选")
    @pytest.mark.parametrize("limit, skip, select", [
        (5, 0, ["title", "reactions"]),  # 查标题和点赞数
        (10, 10, ["id", "userId"]),  # 翻页
    ])
    def test_limit_skip_posts(self, posts_api, limit, skip, select):
        res = posts_api.limit_skip_posts(limit, skip, select)
        assert res.status_code == 200

        posts = res.json()['posts']
        assert len(posts) <= limit

        if select and posts:
            first_keys = posts[0].keys()
            for field in select:
                assert field in first_keys

    @allure.story("帖子排序")
    @pytest.mark.parametrize("sort_by, order", [
        ("title", "asc"),
        ("views", "desc")  # 按阅读量降序
    ])
    def test_sort_posts(self, posts_api, sort_by, order):
        res = posts_api.sort_posts(sort_by, order)
        assert res.status_code == 200
        assert len(res.json()['posts']) > 0

    @allure.story("帖子标签流程")
    def test_post_tags_flow(self, posts_api):
        """
        链路：获取所有 Tag -> 随机选一个 -> 查该 Tag 的帖子
        """
        tags_res = posts_api.get_all_post_tags()
        assert tags_res.status_code == 200
        tags = tags_res.json()
        assert len(tags) > 0

        target_tag = random.choice(tags)
        tag_slug = target_tag['slug'] if isinstance(target_tag, dict) else target_tag

        # 查帖子
        res = posts_api.get_posts_by_tag(tag_slug)
        assert res.status_code == 200

        posts = res.json()['posts']
        if len(posts) > 0:
            # 验证返回的帖子确实包含这个 tag
            assert tag_slug in posts[0]['tags']

    @allure.story("帖子评论链路")
    def test_post_comment_chain(self, posts_api):
        """
        查看某个帖子的评论
        """
        post_id = 1
        res = posts_api.get_post_comments(post_id)
        assert res.status_code == 200

        comments = res.json().get('comments', [])
        # 如果该贴有评论，评论的 postId 必须是 1
        if comments:
            assert comments[0]['postId'] == post_id
            assert 'user' in comments[0]

    @allure.story("添加帖子(Mock)")
    def test_add_post(self, posts_api):
        payload = {
            "title": "Automated Testing is cool",
            "userId": 5,
            "tags": ["testing", "automation"]
        }
        res = posts_api.add_post(payload)
        assert res.status_code in [200, 201]

        data = res.json()
        assert data['title'] == payload['title']
        assert data['userId'] == 5
        assert data['tags'] == payload['tags']

    @allure.story("更新帖子(Mock)")
    def test_update_post(self, posts_api):
        post_id = 1
        payload = {"title": "Updated Title via API"}

        res = posts_api.update_post(post_id, payload)
        assert res.status_code == 200

        data = res.json()
        assert data['title'] == payload['title']
        assert data['id'] == post_id

    @allure.story("删除帖子(Mock)")
    def test_delete_post(self, posts_api):
        post_id = 1
        res = posts_api.delete_post(post_id)
        assert res.status_code == 200

        data = res.json()
        assert data['isDeleted'] is True