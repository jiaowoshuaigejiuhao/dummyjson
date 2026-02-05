import pytest
import random
import allure
import jsonpath


@allure.feature("评论模块")
class TestCommentFlow:

    @allure.story("获取所有评论")
    def test_get_all_comments(self, comment_api):
        res = comment_api.get_all_comments()
        assert res.status_code == 200

        data = res.json()
        assert len(data['comments']) > 0
        assert data['total'] > 0
        # 默认 limit 30
        assert len(data['comments']) == 30

    @allure.story("获取单个评论")
    def test_get_a_single_comment(self, comment_api):
        # 随机取一个 ID
        comment_id = random.randint(1, 100)
        res = comment_api.get_a_single_comment(comment_id)


        if res.status_code == 404:
            pytest.skip(f"Comment ID {comment_id} not found")

        assert res.status_code == 200
        data = res.json()

        assert data['id'] == comment_id

        assert data['body'] is not None

        assert 'user' in data
        assert 'postId' in data

    @allure.story("分页与字段筛选")
    @pytest.mark.parametrize("limit, skip, select", [
        (5, 0, ["body", "postId"]),  # 只看内容和关联帖子
        (10, 5, ["user"]),  # 翻页，只看用户信息
        (0, 0, None)  # 全量
    ])
    def test_limit_skip_comments(self, comment_api, limit, skip, select):
        res = comment_api.limit_skip_comments(limit, skip, select)
        assert res.status_code == 200

        comments = res.json().get('comments', [])

        if limit != 0:
            assert len(comments) <= limit

        if select and comments:
            first_keys = comments[0].keys()
            for field in select:
                assert field in first_keys

    @allure.story("根据帖子ID查询评论")
    def test_get_comments_by_post_id(self, comment_api):
        """
        闭环验证：
        1. 先获取任意一个真实存在的评论。
        2. 提取该评论所属的 postId。
        3. 用这个 postId 去查，保证一定能查到数据。
        """
        all_res = comment_api.get_all_comments()
        all_comments = all_res.json().get('comments', [])
        target_comment = random.choice(all_comments)

        target_post_id = target_comment['postId']

        with allure.step(f"查询帖子 {target_post_id} 的所有评论"):
            res = comment_api.get_comments_by_post_id(target_post_id)
            assert res.status_code == 200

            post_comments = res.json().get('comments', [])
            assert len(post_comments) > 0

            for c in post_comments:
                assert c['postId'] == target_post_id

    @allure.story("添加评论(Mock)")
    def test_add_comment(self, comment_api):
        payload = {
            "body": "This is a great product/post!",
            "postId": 3,
            "userId": 5,
        }
        res = comment_api.add_comment(payload)
        assert res.status_code in [200, 201]

        data = res.json()
        assert data['body'] == payload['body']
        assert data['postId'] == payload['postId']
        assert data['user']['id'] == payload['userId']

    @allure.story("更新评论(Mock)")
    def test_update_comment(self, comment_api):
        comment_id = 1
        payload = {"body": "Updated comment text via API"}

        res = comment_api.update_comment(comment_id, payload)
        assert res.status_code == 200

        data = res.json()
        assert data['body'] == payload['body']
        assert data['id'] == comment_id

    @allure.story("删除评论(Mock)")
    def test_delete_comment(self, comment_api):
        comment_id = 1
        res = comment_api.delete_comment(comment_id)
        assert res.status_code == 200

        data = res.json()
        assert data['isDeleted'] is True
        assert data['deletedOn'] is not None