from django.db import models
from utils.model import BaseModel


# 课程分类表
class CourseCategory(BaseModel):
    """分类"""
    name = models.CharField(max_length=64, unique=True, verbose_name="分类名称")

    class Meta:
        db_table = "luffy_course_category"
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.name


# 实战课表
class Course(BaseModel):
    # choice
    course_type = (
        (0, '付费'),
        (1, '超级VIP专享'),

    )
    level_choices = (
        (0, '初级'),
        (1, '中级'),
        (2, '高级'),
        (3, '特高级'),
        (4, '超神'),
    )
    status_choices = (
        (0, '上线'),
        (1, '下线'),
        (2, '预上线'),
    )
    # 课程名
    name = models.CharField(max_length=128, verbose_name="课程名称")
    # 课程图片  null：数据库可以为空，blank:后台管理录入的时候可以不填，
    course_img = models.ImageField(upload_to="courses", max_length=255, verbose_name="封面图片", blank=True, null=True)
    # 付费类型
    course_type = models.SmallIntegerField(choices=course_type, default=0, verbose_name="付费类型")
    # 详情介绍--》课程详情页面---》TextField---》bbs项目的文章详情，html内容
    brief = models.TextField(max_length=2048, verbose_name="详情介绍", null=True, blank=True)
    # 难度等级
    level = models.SmallIntegerField(choices=level_choices, default=0, verbose_name="难度等级")
    # 发布日期  课程录入一个时间---》没有发布---》发布是在网站上可以看到了
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)
    # 建议学习周期
    period = models.IntegerField(verbose_name="建议学习周期(day)", default=7)
    # 课件路径--》课程有课件  ppt，png，md---》压缩成zip
    attachment_path = models.FileField(upload_to="attachment", max_length=128, verbose_name="课件路径", blank=True,
                                       null=True)
    # 课程状态
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="课程状态")
    # 学习人数 ---》优化字段，正常课程跟用户是有关系的，不需要关联查询统计用户个数了
    students = models.IntegerField(verbose_name="学习人数", default=0)
    # 总课时数量---3个章节20课时的内容
    sections = models.IntegerField(verbose_name="总课时数量", default=0)
    # 课时更新数量  ---》3个章节20课时的内容现在只更新了10个
    pub_sections = models.IntegerField(verbose_name="课时更新数量", default=0)
    # 课程原价
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程原价", default=0)

    ### 关联字段---》老师---》一个老师有多门课程，关联字段写在多的一方，写在课程中
    teacher = models.ForeignKey("Teacher", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name="授课老师")
    ###  关联字段---》课程分类--->一个分类下有多个课程，关联字段写在多的一方
    course_category = models.ForeignKey("CourseCategory", on_delete=models.SET_NULL, db_constraint=False, null=True,
                                        blank=True,
                                        verbose_name="课程分类")

    class Meta:
        db_table = "luffy_course"
        verbose_name = "课程"
        verbose_name_plural = "课程"

    def __str__(self):
        return "%s" % self.name

    @property  # 返回课程类型的中文，不这么写，它是一个数字
    def course_type_name(self):
        return self.get_course_type_display()

    def level_name(self):
        return self.get_level_display()

    def status_name(self):
        return self.get_status_display()
    @property
    def section_list(self):
        sections = []
        # 如果课时小于等于四条，返回总课时，如果大于4条，最多返回4条
        # 第一步：通过课程拿到所有章节
        # course_chapter_list=self.coursechapter_set.all() # 不需要
        course_chapter_list = self.coursechapters.all()
        # 第二步：循环所有章节
        for course_chapter in course_chapter_list:
            # 第三步：通过章节，拿到该章节的所有课时
            course_section_list = course_chapter.coursesections.all()
            # 第四步：循环取出所有章节，追加到一个列表中，准备返回
            for course_section in course_section_list:
                sections.append({
                    'name': course_section.name,
                    'section_link': course_section.section_link,
                    'duration': course_section.duration,
                    'free_trail': course_section.free_trail,
                })
                if len(sections) == 4:
                    return sections
        # 在for循环外层
        return sections


# 课程章节
class CourseChapter(BaseModel):
    # 一对多，写在多的一方
    course = models.ForeignKey("Course", related_name='coursechapters', on_delete=models.CASCADE, verbose_name="课程名称")
    # 章节数字--->第几章
    chapter = models.SmallIntegerField(verbose_name="第几章", default=1)
    # 章节标题
    name = models.CharField(max_length=128, verbose_name="章节标题")
    # 章节介绍
    summary = models.TextField(verbose_name="章节介绍", blank=True, null=True)
    # 发布日期
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)

    class Meta:
        db_table = "luffy_course_chapter"
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s:(第%s章)%s" % (self.course, self.chapter, self.name)


# 课时表
class CourseSection(BaseModel):
    """课时"""
    section_type_choices = (
        (0, '文档'),
        (1, '练习'),
        (2, '视频')
    )
    # 跟章节一对多，关联字段写在多的一方
    chapter = models.ForeignKey("CourseChapter", related_name='coursesections', on_delete=models.CASCADE,
                                verbose_name="课程章节")

    # 课时名
    name = models.CharField(max_length=128, verbose_name="课时标题")
    # 重写字段
    orders = models.PositiveSmallIntegerField(verbose_name="课时排序")
    # 课时种类：视频，文档，练习
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices, verbose_name="课时种类")
    # 课时链接：视频地址，文档地址
    section_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="课时链接",
                                    help_text="若是video，填vid,若是文档，填link")
    # 视频时长 ，仅在前端展示使用
    duration = models.CharField(verbose_name="视频时长", blank=True, null=True, max_length=32)
    # 发布时间
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    # 是否可试看  允许免费看几个视频
    free_trail = models.BooleanField(verbose_name="是否可试看", default=False)

    class Meta:
        db_table = "luffy_course_section"
        verbose_name = "课时"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s-%s" % (self.chapter, self.name)


# 课程评论表
class CourseComment(BaseModel):
    """课程评论（支持回复：parent 指向父评论）"""
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='comments', verbose_name='用户')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='comments', verbose_name='课程')
    content = models.TextField(verbose_name='评论内容')
    score = models.IntegerField(verbose_name='评分', default=5)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='replies', verbose_name='父评论')
    orders = models.IntegerField(verbose_name='优先级', default=0)  # 评论不需要排序，覆盖默认值

    class Meta:
        db_table = 'luffy_course_comment'
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'


# 老师表

class Teacher(BaseModel):
    """导师"""
    role_choices = (
        (0, '讲师'),
        (1, '导师'),
        (2, '班主任'),
    )
    # 老师名
    name = models.CharField(max_length=32, verbose_name="导师名")
    # 老师身份---》讲师，导师，班主任
    role = models.SmallIntegerField(choices=role_choices, default=0, verbose_name="导师身份")
    # 职位、职称
    title = models.CharField(max_length=64, verbose_name="职位、职称")
    # 导师签名
    signature = models.CharField(max_length=255, verbose_name="导师签名", help_text="导师签名", blank=True, null=True)
    # 老师图片
    image = models.ImageField(upload_to="teacher", null=True, verbose_name="导师封面")
    # 导师描述-->很详细-->html
    brief = models.TextField(max_length=1024, verbose_name="导师描述")

    class Meta:
        db_table = "luffy_teacher"
        verbose_name = "导师"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.name

    def role_name(self):
        return self.get_role_display()
