from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CourseCategoryView, CourseView, CourseChapterView, CourseSearchView, CommentView

router = SimpleRouter()
router.register('category', CourseCategoryView, 'category')
router.register('actual', CourseView, 'actual')
router.register('chapter', CourseChapterView, 'chapter')
router.register('search', CourseSearchView, 'search')
router.register('comment', CommentView, 'comment')

urlpatterns = [
    path('', include(router.urls)),
]
