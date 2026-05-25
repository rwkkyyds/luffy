from django.core.cache import cache
from utils.exception import LuffyException
from .models import CourseComment


class CommentService:
    """评论服务：反垃圾逻辑"""

    RATE_KEY = "comment_rate:{user_id}:{course_id}"
    RATE_LIMIT = 10       # 同一用户同一课程 5min 内最多 10 条
    RATE_TTL = 300        # 5 分钟

    @classmethod
    def create(cls, user_id, course_id, content, score, parent_id=None):
        """
        发表评论
        - 频率限制：同一用户同一课程 5min 内最多 10 条
        - 内容校验：长度 10-500 字
        - 如果是回复，校验父评论是否存在且属于同一课程
        """
        # 频率限制：同一用户同一课程 5min 内最多 10 条
        rate_key = cls.RATE_KEY.format(user_id=user_id, course_id=course_id)
        count = cache.get(rate_key, 0)
        if count >= cls.RATE_LIMIT:
            raise LuffyException(msg="评论过于频繁，请5分钟后再试", status=422)
        cache.set(rate_key, count + 1, cls.RATE_TTL)

        # 内容校验
        if len(content) < 10 or len(content) > 500:
            raise LuffyException(msg="评论内容长度需在10-500字之间", status=422)

        # 评分校验
        if score < 1 or score > 5:
            raise LuffyException(msg="评分需在1-5之间", status=422)

        # 回复校验
        parent = None
        if parent_id:
            parent = CourseComment.objects.filter(
                id=parent_id, course_id=course_id, is_delete=False
            ).first()
            if not parent:
                raise LuffyException(msg="父评论不存在", status=404)

        return CourseComment.objects.create(
            user_id=user_id,
            course_id=course_id,
            content=content,
            score=score,
            parent=parent,
        )

    @classmethod
    def delete(cls, comment_id, user_id):
        """删除自己的评论（软删除）"""
        comment = CourseComment.objects.filter(
            id=comment_id, is_delete=False
        ).first()
        if not comment:
            raise LuffyException(msg="评论不存在", status=404)
        if comment.user_id != user_id:
            raise LuffyException(msg="只能删除自己的评论", status=403)
        comment.is_delete = True
        comment.save(update_fields=['is_delete'])
