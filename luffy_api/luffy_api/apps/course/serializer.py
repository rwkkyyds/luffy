from rest_framework import serializers
from .models import CourseCategory, Course, Teacher, CourseChapter, CourseSection, CourseComment


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'role_name', 'title', 'signature', 'image', 'brief')


class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()  # 子序列化，单单条数据，直接子序列化

    class Meta:
        model = Course
        # fields = ['id', 'name']  # 这里要写很多，自定义字段
        fields = [
            'id',
            'name',
            'course_img',
            'brief',  # 课程介绍--->后面课程详情使用同一个序列化类
            'attachment_path',  # 课件
            'pub_sections',  # 发布的课时数
            'price',  # 价格
            'students',  # 学习人数
            'period',  # 学习周期
            'sections',  # 总课时数

            'course_type_name',  # choice字段---》表模型中写
            'level_name',  # choice字段---》表模型中写
            'status_name',  # choice字段---》表模型中写

            'teacher',  # 表模型中写，序列化类中写，子序列化
            'section_list',  # 表模型中写 -章节--->Course表中没有---》重写：序列类写，表模型中写
        ]


class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        fields = ['name', 'orders', 'section_link', 'duration', 'free_trail']


class CourseChapterSerializer(serializers.ModelSerializer):
    # 使用子序列化
    coursesections = CourseSectionSerializer(many=True)

    class Meta:
        model = CourseChapter
        # CourseChapter表中隐藏了一个coursesections字段，对象.coursesections
        fields = ['id', 'name', 'chapter', 'summary', 'coursesections']  # 返回该章节下的课时


class CommentCreateSerializer(serializers.Serializer):
    """发表评论的参数校验"""
    content = serializers.CharField(min_length=10, max_length=500, help_text='评论内容')
    score = serializers.IntegerField(min_value=1, max_value=5, help_text='评分1-5')
    parent_id = serializers.IntegerField(required=False, allow_null=True, help_text='父评论ID（回复时传）')


class CommentSerializer(serializers.ModelSerializer):
    """评论详情（嵌套用户信息 + 回复 + 回复对象用户名）"""
    username = serializers.CharField(source='user.username', read_only=True)
    icon = serializers.ImageField(source='user.icon', read_only=True, default=None)
    replies = serializers.SerializerMethodField()
    parent_username = serializers.SerializerMethodField()

    class Meta:
        model = CourseComment
        fields = ['id', 'content', 'score', 'username', 'icon', 'created_time', 'parent', 'parent_username', 'replies']

    def get_parent_username(self, obj):
        if obj.parent:
            return obj.parent.user.username
        return None

    def get_replies(self, obj):
        """只取前 3 条回复（带 select_related 避免 N+1）"""
        replies = obj.replies.filter(is_delete=False).select_related('user', 'parent__user')[:3]
        return CommentSerializer(replies, many=True, context=self.context).data


'''

> 是不是这样理解，刚开始，是qs父的序列化多个元素验证然后拿到各个父类评论然后父类的replies反向查询拿到各个子类对
  象然后接着序列化得到子类数据，子类数据中又replies反向查询。。。。。

● 对，理解完全正确。就是递归序列化：

  CourseComment.objects.filter(parent__isnull=True)  ← 取出所有顶级评论
    ↓ 序列化每个父评论时，调用 get_replies
    ├── 父评论1 → obj.replies.filter(...)[:3] → 取出子评论 → 再用 CommentSerializer 序列化
    │     ├── 子评论1.1 → get_replies → replies.filter(...) → ...
    │     └── 子评论1.2 → get_replies → replies.filter(...) → ...
    └── 父评论2 → obj.replies.filter(...)[:3] → ...
          └── 子评论2.1 → ...

  实际会自动停下来，因为：
  - 大多数回复下面没有再回复 → replies.filter(...) 返回空 → [] → 终止
  - [:3] 限制了每层最多 3 条，控制了展开宽度

  最终输出就是嵌套结构：

  [
      {
          "id": 1, "content": "父评论", "replies": [
              {"id": 2, "content": "回复1", "replies": []},
              {"id": 3, "content": "回复2", "replies": []}
          ]
      }
  ]

  就是一个树形结构，get_replies 递归展开每一层。

'''
