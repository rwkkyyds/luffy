from rest_framework import serializers
from course.models import Course


class CartAddSerializer(serializers.Serializer):
    """
    添加购物车的序列化器
    - course_id: 课程ID（必填）
    - price: 课程价格（必填，前端传入用于校验）
    """
    course_id = serializers.IntegerField(required=True, help_text="课程ID")
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="课程价格")

    def validate_course_id(self, value):
        """校验课程是否存在"""
        course = Course.objects.filter(id=value, is_delete=False).first()
        if not course:
            raise serializers.ValidationError("课程不存在")
        return value

    def validate(self, attrs):
        """校验价格是否与数据库一致"""
        course = Course.objects.filter(id=attrs['course_id'], is_delete=False).first()
        if course and course.price != attrs['price']:
            raise serializers.ValidationError("价格不匹配，请刷新页面重试")
        return attrs


class CartRemoveSerializer(serializers.Serializer):
    """移除购物车课程的序列化器"""
    course_id = serializers.IntegerField(required=True, help_text="课程ID")
