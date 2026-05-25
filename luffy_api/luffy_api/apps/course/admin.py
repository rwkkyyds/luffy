from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Teacher)
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(CourseChapter)
admin.site.register(CourseSection)