from django.db import models

# Create your models here.
# 轮播图接口---》轮播图表
from utils.model import BaseModel
class Banner(BaseModel):
    # 顺序，插入时间， 是否显示，是否删除。。。----》后期写课程的表也会用到这些字段--->仿AbstractUser,写一个基表，以后继承这个表
    # 继承过来，只需要写自有字段即可：title，image，info，link
    title = models.CharField(max_length=16, unique=True, verbose_name='名称')
    image = models.ImageField(upload_to='banner', verbose_name='图片')
    # 写接口---》app---》前端配合一个接口---》实现打开app，就有广告图片---》点击广告图片调整到app内部或者使用浏览器打开
    # 一打开app，先打开的页面是什么，写app的人写的---》整一张大图充满全屏即可--》配合一个接口，返回一张大图
    # app打开广告接口---》{code:100,msg:成功,img:{img:127.0.0.1/img/1.png,link:'www.baidu.com',type:2}}
    link = models.CharField(max_length=64, verbose_name='跳转链接') # 在前端点击图片，会跳转到某个地址
    info = models.TextField(verbose_name='详情')  # 也可以用详情表，宽高出处
    class Meta:
        db_table = 'luffy_banner'
        verbose_name_plural = '轮播图表'

    def __str__(self):
        return self.title






