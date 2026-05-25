from django.shortcuts import render
# Create your views here.
from utils.response import APIResponse
from .models import CourseCategory, Course, CourseChapter, CourseComment
from .serializer import CourseCategorySerializer, CourseSerializer, CourseChapterSerializer, CommentSerializer, CommentCreateSerializer
from .service import CommentService
from .pagination import CommonPageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from utils.authentication import BlacklistJWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema(tags=['课程'], summary='课程分类列表')
class CourseCategoryView(GenericViewSet, ListModelMixin):
    queryset = CourseCategory.objects.all().filter(is_delete=False, is_show=True).order_by('orders')
    serializer_class = CourseCategorySerializer


@extend_schema_view(
    list=extend_schema(tags=['课程'], summary='课程列表', description='分页返回实战课程列表，支持按分类过滤和按价格/学习人数排序。'),
    retrieve=extend_schema(tags=['课程'], summary='课程详情', description='返回单门课程的完整信息，包括章节和课时。'),
)
class CourseView(GenericViewSet, ListModelMixin,RetrieveModelMixin):
    # 优化前（注释保留便于对比）：
    # queryset = Course.objects.all().filter(is_delete=False, is_show=True).order_by('orders')
    # 优化后：select_related 消除 teacher 外键 N+1，prefetch_related 消除 章节→课时 两层 N+1
    queryset = Course.objects.filter(is_delete=False, is_show=True).select_related('teacher').prefetch_related('coursechapters__coursesections').order_by('orders')
    serializer_class = CourseSerializer
    # 加入分页---》随着课程越来越多，要分页
    pagination_class = CommonPageNumberPagination
    # 加入排序
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['price', 'students']
    # 加入过滤---》不是按名字搜索的这种过滤，而是按课程分类过滤--》第三方django-filter
    filterset_fields = ['course_category']


@extend_schema(tags=['课程'], summary='课程章节列表', description='按课程 ID 过滤，返回该课程的所有章节及课时。')
class CourseChapterView(GenericViewSet, ListModelMixin):
    # 优化前（注释保留便于对比）：
    # queryset = CourseChapter.objects.all().filter(is_show=True,is_delete=False).order_by('orders')
    # 优化后：prefetch_related 消除 coursesections 反向关系 N+1（序列化器中 many=True 子序列化）
    queryset = CourseChapter.objects.filter(is_show=True,is_delete=False).prefetch_related('coursesections').order_by('orders')
    serializer_class =CourseChapterSerializer
    filter_backends = [DjangoFilterBackend]
    # 加入过滤---》按照课程id过滤--》第三方django-filter
    filter_fields = ['course_id']


@extend_schema(tags=['课程'], summary='课程搜索', description='按课程名称模糊搜索，支持分页。')
class CourseSearchView(GenericViewSet, ListModelMixin):
    # 优化前（注释保留便于对比）：
    # queryset = Course.objects.all().filter(is_delete=False, is_show=True).order_by('orders')
    # 优化后：select_related 消除 teacher 外键 N+1（搜索列表也展示老师信息）
    queryset = Course.objects.filter(is_delete=False, is_show=True).select_related('teacher').order_by('orders')
    serializer_class = CourseSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name',]
    pagination_class = CommonPageNumberPagination


    # 方便后期扩展
    # def list(self, request, *args, **kwargs):
    #     # 这个查的是实战课
    #     res=super().list(request, *args, **kwargs)
    #     # res2=查询免费课
    #     # res3=查询轻课
    #
    #     # 上面全是取数据库查询
    #     # 后期改成取es中查询，
    #     return APIResponse(result={'free_course':'字典','actual_course':res.data})


@extend_schema(tags=['评论'])
class CommentView(GenericViewSet):
    """
    评论视图集（注册在 router.register('comment', ...) 下）
    - POST  /api/v1/course/comment/{course_id}/comment/    发表评论（JWT）
    - GET   /api/v1/course/comment/{course_id}/comments/   课程评论列表
    - GET   /api/v1/course/comment/{comment_id}/replies/   评论回复列表
    - DELETE /api/v1/course/comment/{id}/delete/           删除自己的评论（JWT）

    ── 评论树递归序列化原理 ──
    CourseComment.parent 外键指向自身（自引用），related_name='replies'。
    CommentSerializer 的 replies 字段是 SerializerMethodField，
    get_replies() 中通过 obj.replies（反向关系管理器）取出子评论，
    再用同一个 CommentSerializer 序列化 → 递归展开，直到子评论为空停止。

    数据结构：
        父评论 (parent=None)
          └── obj.replies.filter(...)[:3]    ← get_replies 取子评论
                ├── 子评论1 → get_replies → replies → []  (终止)
                └── 子评论2 → get_replies → replies → []  (终止)

    两个接口的区别仅在于起点：
        course_comments: parent__isnull=True → 从所有顶级评论开始递归
        replies:        parent_id=X         → 从指定评论开始递归
    """
    authentication_classes = [BlacklistJWTAuthentication]

    @extend_schema(summary='发表评论', description='对课程发表评论或回复。需要JWT认证。24小时内同一课程最多3条。')
    @action(methods=['post'], detail=False, url_path=r'(?P<course_id>\d+)/comment',
            permission_classes=[IsAuthenticated])
    def create_comment(self, request, course_id=None):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = CommentService.create(
            user_id=request.user.id,
            course_id=int(course_id),
            content=serializer.validated_data['content'],
            score=serializer.validated_data['score'],
            parent_id=serializer.validated_data.get('parent_id'),
        )
        return APIResponse(msg="评论成功", comment_id=comment.id)

    @extend_schema(summary='课程评论列表', description='获取课程的顶级评论列表（分页）。无认证。')
    @action(methods=['get'], detail=False, url_path=r'(?P<course_id>\d+)/comments',
            permission_classes=[AllowAny])
    def course_comments(self, request, course_id=None):
        qs = CourseComment.objects.filter(
            course_id=course_id, parent__isnull=True, is_delete=False   # parent__isnull=True 筛选parent 字段为空的数据
        ).select_related('user')  #join user表，消除外键 N+1
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(qs, many=True, context={'request': request})
        return APIResponse(data=serializer.data)

    @extend_schema(summary='评论回复列表', description='获取某条评论的回复列表。无认证。')
    @action(methods=['get'], detail=False, url_path=r'(?P<comment_id>\d+)/replies',
            permission_classes=[AllowAny])
    def replies(self, request, comment_id=None):
        qs = CourseComment.objects.filter(
            parent_id=comment_id, is_delete=False
        ).select_related('user')
        serializer = CommentSerializer(qs, many=True, context={'request': request})
        return APIResponse(data=serializer.data)
    

# 这两个是不是其实一样的，一个从顶级父评论出发一个是从某个父出发往下递归

# ● 对，本质一样。区别只是起点不同：

# course_comments:  从"根"开始 → parent__isnull=True → 取所有顶级评论
#                 ↓ 序列化时 get_replies 递归展开
#                 父评论1
#                     ├── 子评论1.1
#                     └── 子评论1.2
#                 父评论2
#                     └── 子评论2.1

# replies:          从"某个节点"开始 → parent_id=comment_id → 取指定评论的子评论
#                 ↓ 序列化时 get_replies 递归展开
#                 子评论X
#                     ├── 子子评论X.1
#                     └── 子子评论X.2

# 两者都用 CommentSerializer，都会通过 get_replies 往下递归。唯一的差别是 SQL 的 WHERE
# 条件不同，决定了从树的哪一层开始取数据。

    @extend_schema(summary='删除评论', description='删除自己的评论（软删除）。需要JWT认证。')
    @action(methods=['delete'], detail=True, url_path='delete',
            permission_classes=[IsAuthenticated])
    def destroy_comment(self, request, pk=None):
        CommentService.delete(comment_id=pk, user_id=request.user.id)
        return APIResponse(msg="删除成功")
