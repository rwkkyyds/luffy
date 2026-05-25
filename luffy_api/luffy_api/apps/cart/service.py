import json
from datetime import datetime
from django.core.cache import cache
from course.models import Course
from utils.exception import LuffyException


def _get_redis():
    """获取底层 Redis 连接（支持 Hash 操作），与 Django 缓存共用连接池"""
    return cache.client.get_client()


class CartService:
    """
    购物车服务：用 Redis Hash 存储

    key 格式：
      已登录 → cart:{user_id}          例 cart:42
      未登录 → cart:anonymous:{uuid}   例 cart:anonymous:abc123

    所有方法统一用 owner 参数，登录传 user_id，未登录传 cookie_id
    内部由 _resolve_key 统一生成 Redis key，零重复代码
    """
    CART_KEY = "cart:{user_id}"
    ANONYMOUS_PREFIX = "anonymous:"
    CART_TTL = 60 * 60 * 24 * 30  # 30天

    @classmethod
    def _resolve_key(cls, owner):
        """
        统一生成 Redis key
        owner 是 int → cart:{user_id}
        owner 是 str → cart:anonymous:{cookie_id}
        """
        if isinstance(owner, int):
            return cls.CART_KEY.format(user_id=owner)
        return cls.CART_KEY.format(user_id=f"{cls.ANONYMOUS_PREFIX}{owner}")

    @classmethod
    def add(cls, owner, course_id, price):
        """
        添加课程到购物车（登录/未登录通用）
        - owner: user_id(int) 或 cookie_id(str)
        - 课程已在购物车中 → 抛异常
        - 返回当前购物车商品数量
        """
        r = _get_redis()
        key = cls._resolve_key(owner)
        if r.hexists(key, course_id):
            raise LuffyException(msg="该课程已在购物车中", status=422)
        course = Course.objects.filter(id=course_id, is_delete=False).first()
        if not course:
            raise LuffyException(msg="课程不存在", status=404)
        data = json.dumps({
            "price": str(price),
            "added_at": datetime.now().isoformat()
        })
        r.hset(key, course_id, data)
        r.expire(key, cls.CART_TTL)
        return r.hlen(key)

    @classmethod
    def list(cls, owner):
        """
        获取购物车列表（登录/未登录通用）
        - 从 Redis 取出所有课程 ID
        - 批量查 Course 表获取详情（避免 N+1）
        - 合并 Redis 数据 + DB 数据返回
        """
        r = _get_redis()
        key = cls._resolve_key(owner)
        raw = r.hgetall(key)
        if not raw:
            return []
        course_ids = []
        for cid_bytes in raw.keys():
            try:
                course_ids.append(int(cid_bytes))
            except (ValueError, TypeError):
                continue  # 跳过非数字 field（脏数据）
        if not course_ids:
            return []
        courses = Course.objects.filter(
            id__in=course_ids, is_delete=False
        ).values('id', 'name', 'price', 'course_img')
        course_map = {c['id']: c for c in courses}
        result = []
        for cid_bytes, data_bytes in raw.items():
            try:
                cid = int(cid_bytes)
            except (ValueError, TypeError):
                continue
            if cid not in course_map:
                continue
            cart_data = json.loads(data_bytes)
            course_info = course_map[cid]
            result.append({
                "course_id": cid,
                "name": course_info['name'],
                "price": str(course_info['price']),
                "course_img": course_info['course_img'],
                "added_at": cart_data['added_at']
            })
        return result

    @classmethod
    def remove(cls, owner, course_id):
        """
        移除单个课程（登录/未登录通用）
        - HDEL 删除指定 field
        - 返回删除后购物车剩余数量
        """
        r = _get_redis()
        key = cls._resolve_key(owner)
        if not r.hexists(key, course_id):
            raise LuffyException(msg="该课程不在购物车中", status=404)
        r.hdel(key, course_id)
        return r.hlen(key)

    @classmethod
    def clear(cls, owner):
        """清空购物车（登录/未登录通用）"""
        r = _get_redis()
        key = cls._resolve_key(owner)
        r.delete(key)

    @classmethod
    def checkout(cls, owner):
        """
        结算：购物车 → 订单
        - 获取购物车所有课程
        - 返回课程列表和总价（实际创建订单在 views 层）
        """
        cart_items = cls.list(owner)
        if not cart_items:
            raise LuffyException(msg="购物车为空，无法结算", status=422)
        total_amount = sum(float(item['price']) for item in cart_items)
        course_ids = [item['course_id'] for item in cart_items]
        return {
            "course_ids": course_ids,
            "total_amount": total_amount,
            "cart_items": cart_items
        }

    @classmethod
    def merge_cart(cls, cookie_id, user_id):
        """
        合并购物车：用户登录后，把临时购物车（cookie）合并到正式购物车（user_id）

        合并策略：以正式购物车为准
          - 临时车有、正式车没有 → 合并过去
          - 两边都有同一课程 → 跳过（不覆盖）
          - 合并完删除临时购物车
        """
        r = _get_redis()
        anonymous_key = cls._resolve_key(cookie_id)
        user_key = cls._resolve_key(user_id)
        raw = r.hgetall(anonymous_key)
        if not raw:
            return
        for course_id_bytes, data_bytes in raw.items():
            try:
                course_id = int(course_id_bytes)
            except (ValueError, TypeError):
                continue
            if not r.hexists(user_key, course_id):
                r.hset(user_key, course_id, data_bytes)
        r.expire(user_key, cls.CART_TTL)
        r.delete(anonymous_key)
