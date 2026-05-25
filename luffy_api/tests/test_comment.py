"""
测试评论模块（apps/course/ — 评论部分）
============================================================

测试什么：
  1. CommentService —— create（反垃圾）、delete（软删除）
  2. CommentView API —— 4个接口

接口路由（注册在 router.register('comment', ...) 下）：
  POST   /api/v1/course/comment/{course_id}/comment/   发表评论
  GET    /api/v1/course/comment/{course_id}/comments/   课程评论列表
  GET    /api/v1/course/comment/{comment_id}/replies/   回复列表
  DELETE /api/v1/course/comment/{id}/delete/            删除评论
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from user.models import User
from course.models import Course, Teacher, CourseComment
from course.service import CommentService


# ============================================================
# fixtures
# ============================================================

@pytest.fixture
def comment_data(db):
    """创建评论所需的用户 + 课程"""
    user = User.objects.create_user(username='commenter', password='123', mobile='13900000001')
    teacher = Teacher.objects.create(name='T', role=0, title='讲师', brief='b', orders=1)
    course = Course.objects.create(
        name='评论测试课程', price=Decimal('99.00'), teacher=teacher, orders=1,
    )
    return {'user': user, 'course': course}


@pytest.fixture
def mock_cache():
    """mock Redis cache（评论频率限制用）"""
    storage = {}
    mock = MagicMock()
    mock.get.side_effect = lambda key, default=None: storage.get(key, default)
    mock.set.side_effect = lambda key, value, ttl=None: storage.__setitem__(key, value)
    with patch('course.service.cache', mock):
        yield mock, storage


# ============================================================
# 测试 CommentService
# ============================================================

class TestCommentServiceCreate:
    @pytest.mark.django_db
    def test_create_success(self, comment_data, mock_cache):
        """正常发表评论 → 返回评论对象"""
        comment = CommentService.create(
            user_id=comment_data['user'].id,
            course_id=comment_data['course'].id,
            content='这个课程非常棒，老师讲得很清楚！',
            score=5,
        )
        assert comment.id is not None
        assert comment.content == '这个课程非常棒，老师讲得很清楚！'
        assert comment.score == 5
        assert comment.parent is None

    @pytest.mark.django_db
    def test_create_reply(self, comment_data, mock_cache):
        """回复评论 → parent 指向父评论"""
        parent = CommentService.create(
            user_id=comment_data['user'].id,
            course_id=comment_data['course'].id,
            content='这是父评论，内容足够长！',
            score=4,
        )
        reply = CommentService.create(
            user_id=comment_data['user'].id,
            course_id=comment_data['course'].id,
            content='这是回复评论，内容也足够长！',
            score=5,
            parent_id=parent.id,
        )
        assert reply.parent_id == parent.id

    @pytest.mark.django_db
    def test_create_content_too_short(self, comment_data, mock_cache):
        """内容太短 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException) as exc:
            CommentService.create(
                user_id=comment_data['user'].id,
                course_id=comment_data['course'].id,
                content='太短',
                score=5,
            )
        assert '10-500' in str(exc.value)

    @pytest.mark.django_db
    def test_create_content_too_long(self, comment_data, mock_cache):
        """内容太长 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException) as exc:
            CommentService.create(
                user_id=comment_data['user'].id,
                course_id=comment_data['course'].id,
                content='x' * 501,
                score=5,
            )
        assert '10-500' in str(exc.value)

    @pytest.mark.django_db
    def test_create_invalid_score(self, comment_data, mock_cache):
        """评分超出范围 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException) as exc:
            CommentService.create(
                user_id=comment_data['user'].id,
                course_id=comment_data['course'].id,
                content='评分测试评论，内容足够长！',
                score=6,
            )
        assert '1-5' in str(exc.value)

    @pytest.mark.django_db
    def test_create_rate_limit(self, comment_data, mock_cache):
        """5min内超过10条 → 抛异常"""
        from utils.exception import LuffyException
        uid = comment_data['user'].id
        cid = comment_data['course'].id
        for i in range(10):
            CommentService.create(
                user_id=uid, course_id=cid,
                content=f'第{i+1}条评论内容，足够长！', score=5,
            )
        with pytest.raises(LuffyException) as exc:
            CommentService.create(
                user_id=uid, course_id=cid,
                content='第11条评论，应该被限制！', score=5,
            )
        assert '频繁' in str(exc.value)

    @pytest.mark.django_db
    def test_create_reply_to_nonexistent_parent(self, comment_data, mock_cache):
        """回复不存在的父评论 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException) as exc:
            CommentService.create(
                user_id=comment_data['user'].id,
                course_id=comment_data['course'].id,
                content='回复一个不存在的评论！',
                score=5,
                parent_id=99999,
            )
        assert '不存在' in str(exc.value)


class TestCommentServiceDelete:
    @pytest.mark.django_db
    def test_delete_success(self, comment_data, mock_cache):
        """删除自己的评论 → 软删除"""
        comment = CommentService.create(
            user_id=comment_data['user'].id,
            course_id=comment_data['course'].id,
            content='要删除的评论，内容足够长！',
            score=5,
        )
        CommentService.delete(comment.id, comment_data['user'].id)
        comment.refresh_from_db()
        assert comment.is_delete is True

    @pytest.mark.django_db
    def test_delete_not_found(self, comment_data, mock_cache):
        """删除不存在的评论 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException):
            CommentService.delete(99999, comment_data['user'].id)

    @pytest.mark.django_db
    def test_delete_others_comment(self, db, mock_cache):
        """删除别人的评论 → 抛异常"""
        user1 = User.objects.create_user(username='u1', password='123', mobile='13900000001')
        user2 = User.objects.create_user(username='u2', password='123', mobile='13900000002')
        teacher = Teacher.objects.create(name='T', role=0, title='讲师', brief='b', orders=1)
        course = Course.objects.create(name='C', price=Decimal('10.00'), teacher=teacher, orders=1)
        comment = CommentService.create(
            user_id=user1.id, course_id=course.id,
            content='这是user1的评论，内容足够长！', score=5,
        )
        from utils.exception import LuffyException
        with pytest.raises(LuffyException) as exc:
            CommentService.delete(comment.id, user2.id)
        assert '自己的' in str(exc.value)


# ============================================================
# 测试 CommentView API
# ============================================================

class TestCommentAPICreate:
    @pytest.mark.django_db
    def test_create_requires_auth(self, api_client):
        """未登录发表评论 → 401"""
        resp = api_client.post('/api/v1/course/comment/1/comment/', {
            'content': '测试评论内容足够长！', 'score': 5,
        })
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_create_success(self, auth_client, comment_data):
        """已登录发表评论 → 成功"""
        with patch('course.views.CommentService') as mock_service, \
             patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            mock_comment = MagicMock()
            mock_comment.id = 1
            mock_service.create.return_value = mock_comment
            resp = auth_client.post(
                f'/api/v1/course/comment/{comment_data["course"].id}/comment/',
                {'content': '测试评论内容足够长！', 'score': 5},
            )
            assert resp.data['status'] == 100
            assert '评论成功' in resp.data['msg']


class TestCommentAPIList:
    @pytest.mark.django_db
    def test_list_no_auth_ok(self, api_client, comment_data):
        """未登录也能查看评论列表"""
        resp = api_client.get(f'/api/v1/course/comment/{comment_data["course"].id}/comments/')
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_list_returns_comments(self, api_client, comment_data, mock_cache):
        """评论列表返回评论数据"""
        CommentService.create(
            user_id=comment_data['user'].id,
            course_id=comment_data['course'].id,
            content='测试评论内容足够长！', score=5,
        )
        resp = api_client.get(f'/api/v1/course/comment/{comment_data["course"].id}/comments/')
        assert resp.status_code == 200


class TestCommentAPIReplies:
    @pytest.mark.django_db
    def test_replies_no_auth_ok(self, api_client, comment_data, mock_cache):
        """未登录也能查看回复"""
        parent = CommentService.create(
            user_id=comment_data['user'].id,
            course_id=comment_data['course'].id,
            content='这是一条父评论内容足够长的测试！', score=5,
        )
        resp = api_client.get(f'/api/v1/course/comment/{parent.id}/replies/')
        assert resp.status_code == 200


class TestCommentAPIDelete:
    @pytest.mark.django_db
    def test_delete_requires_auth(self, api_client):
        """未登录删除评论 → 401"""
        resp = api_client.delete('/api/v1/course/comment/1/delete/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_delete_success(self, auth_client, comment_data):
        """已登录删除自己的评论 → 成功"""
        with patch('course.views.CommentService') as mock_service, \
             patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            mock_service.delete.return_value = None
            resp = auth_client.delete('/api/v1/course/comment/1/delete/')
            assert resp.data['status'] == 100
            assert '删除成功' in resp.data['msg']
