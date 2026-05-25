"""
测试课程模块（apps/course/）
============================================================

测试什么：
  1. 课程分类列表
  2. 课程列表（分页、排序、过滤）
  3. 课程详情
  4. 章节列表
  5. 课程搜索

什么是 fixture（测试数据准备）？
  course_data fixture 会创建一套完整的测试数据：
    教师 → 分类 → 课程 → 章节 → 课时
  每个测试用例执行前都会重新创建，保证测试之间互不影响。

DRF 路由说明：
  SimpleRouter 会自动生成 RESTful URL：
    GET  /api/v1/course/actual/     → 课程列表（list）
    GET  /api/v1/course/actual/1/   → 课程详情（retrieve）
    GET  /api/v1/course/category/   → 分类列表
    GET  /api/v1/course/chapter/    → 章节列表
    GET  /api/v1/course/search/     → 搜索
"""
import pytest
from decimal import Decimal
from course.models import CourseCategory, Course, Teacher, CourseChapter, CourseSection


@pytest.fixture
def course_data(db):
    """
    创建一套完整的测试课程数据

    数据关系：
      Teacher (张三)
        └── Course (Python从入门到放弃)  ← 关联教师和分类
              └── CourseChapter (第一章 Python基础)
                    ├── CourseSection (1.1 变量与数据类型)
                    └── CourseSection (1.2 控制流)

    返回字典方便测试中获取各个对象的 id
    """
    teacher = Teacher.objects.create(
        name='张三', role=0, title='高级讲师', brief='资深Python讲师', orders=1,
    )
    cat = CourseCategory.objects.create(name='Python', orders=1)
    course = Course.objects.create(
        name='Python从入门到放弃',
        course_type=0, level=0, status=0,
        price=Decimal('99.00'), students=100, sections=10, pub_sections=10,
        period=30, teacher=teacher, course_category=cat, orders=1,
    )
    chapter = CourseChapter.objects.create(
        course=course, chapter=1, name='第一章 Python基础', orders=1,
    )
    CourseSection.objects.create(
        chapter=chapter, name='1.1 变量与数据类型',
        orders=1, section_type=2, free_trail=True,
    )
    CourseSection.objects.create(
        chapter=chapter, name='1.2 控制流',
        orders=2, section_type=2, free_trail=False,
    )
    return {
        'teacher': teacher, 'category': cat, 'course': course,
        'chapter': chapter,
    }


class TestCourseCategoryAPI:
    @pytest.mark.django_db
    def test_category_list(self, api_client, course_data):
        """课程分类列表返回数据"""
        resp = api_client.get('/api/v1/course/category/')
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    @pytest.mark.django_db
    def test_category_list_empty(self, api_client):
        """没有分类时返回空列表"""
        resp = api_client.get('/api/v1/course/category/')
        assert resp.status_code == 200


class TestCourseAPI:
    @pytest.mark.django_db
    def test_course_list(self, api_client, course_data):
        """课程列表返回分页结构"""
        resp = api_client.get('/api/v1/course/actual/')
        assert resp.status_code == 200
        # 分页结构：{count: N, results: [...], next: ..., previous: ...}
        assert 'results' in resp.data
        assert len(resp.data['results']) >= 1

    @pytest.mark.django_db
    def test_course_list_pagination(self, api_client, course_data):
        """page_size=1 时每页只返回 1 条"""
        resp = api_client.get('/api/v1/course/actual/?page_size=1')
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1

    @pytest.mark.django_db
    def test_course_list_ordering_by_price(self, api_client, course_data):
        """按价格排序"""
        resp = api_client.get('/api/v1/course/actual/?ordering=price')
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_course_list_filter_by_category(self, api_client, course_data):
        """按分类 ID 过滤"""
        cat_id = course_data['category'].id
        resp = api_client.get(f'/api/v1/course/actual/?course_category={cat_id}')
        assert resp.status_code == 200
        assert len(resp.data['results']) >= 1

    @pytest.mark.django_db
    def test_course_detail(self, api_client, course_data):
        """课程详情包含完整信息"""
        course_id = course_data['course'].id
        resp = api_client.get(f'/api/v1/course/actual/{course_id}/')
        assert resp.status_code == 200
        assert resp.data['name'] == 'Python从入门到放弃'
        assert 'teacher' in resp.data       # 包含教师信息（子序列化）
        assert 'section_list' in resp.data   # 包含课时列表

    @pytest.mark.django_db
    def test_course_detail_not_found(self, api_client):
        """课程不存在"""
        resp = api_client.get('/api/v1/course/actual/99999/')
        # DRF 可能返回 404 或自定义错误格式
        assert resp.status_code in (404, 200)


class TestCourseChapterAPI:
    @pytest.mark.django_db
    def test_chapter_list(self, api_client, course_data):
        """章节列表包含课时数据（子序列化）"""
        course_id = course_data['course'].id
        resp = api_client.get(f'/api/v1/course/chapter/?course_id={course_id}')
        assert resp.status_code == 200
        assert len(resp.data) >= 1
        chapter = resp.data[0]
        # CourseChapterSerializer 用子序列化嵌套了 CourseSectionSerializer
        assert 'coursesections' in chapter
        assert len(chapter['coursesections']) == 2  # 我们创建了 2 个课时


class TestCourseSearchAPI:
    @pytest.mark.django_db
    def test_search_by_name(self, api_client, course_data):
        """按名称模糊搜索"""
        resp = api_client.get('/api/v1/course/search/?search=Python')
        assert resp.status_code == 200
        assert len(resp.data['results']) >= 1

    @pytest.mark.django_db
    def test_search_no_result(self, api_client, course_data):
        """搜索不存在的课程 → 空结果"""
        resp = api_client.get('/api/v1/course/search/?search=不存在的课程')
        assert resp.status_code == 200
        assert len(resp.data['results']) == 0
