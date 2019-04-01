from django.db import models
import django
# Create your models here.


# 用户信息储存
class User(models.Model):
    username = models.CharField(verbose_name="用户ID", max_length=20, default="None")
    nickName = models.CharField(verbose_name="昵称", max_length=20, default="None", null=True, blank=True)
    password = models.CharField(verbose_name="密码", max_length=100, default="None", null=True, blank=True)


    registerTime = models.DateTimeField(verbose_name="注册时间", default=django.utils.timezone.now, blank=True)

    authSession = models.CharField(verbose_name="Session", max_length=30, default="000000", null=True, blank=True)
    email = models.CharField(verbose_name="邮箱", max_length=100, default="None", null=True, blank=True)
    headImage = models.ImageField(verbose_name="头像", upload_to='headImages', default='default/1.png', max_length=100)
    changePwdCode = models.CharField(verbose_name="验证码", max_length=5, default="None", null=True, blank=True)

    checkCode = models.CharField(max_length=6, verbose_name="验证码", default="None", null=True, blank=True)

    class Meta:
        verbose_name = r"用户"
        verbose_name_plural = r"用户"
        get_latest_by = "registerTime"



    def __str__(self):
        return self.username


# class Tags(models.Model):
#     tag = models.CharField(max_length=10, verbose_name=u'标签', unique=True)
#
#     class Meta:
#         verbose_name = u'标签'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.tag


class Film(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'电影名')
    info = models.CharField(max_length=1024, verbose_name=u'电影简介')
    on_time = models.DateTimeField(verbose_name=u'上映时间')
    # tag = models.ManyToManyField(Tags, verbose_name=u'标签')

    # 页面上的 宽海报
    poster = models.ImageField(verbose_name=u'海报', upload_to='upload')
    # 电影的头像
    head_image = models.ImageField(verbose_name=u'电影封面', upload_to='upload')

    score = models.FloatField(default=0.0, verbose_name=u'评分')
    marked_members = models.IntegerField(default=0, verbose_name=u'评分人数')
    commented_member = models.IntegerField(default=0, verbose_name=u'评论人数')
    active = models.BooleanField(default=True, verbose_name=u'情况')
    isOnScreen=models.BooleanField(verbose_name="是否上映",default=True)
    class Meta:
        verbose_name = u'电影'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 评分表
class Mark(models.Model):
    user = models.ForeignKey(User, verbose_name=u'评分人', on_delete=models.PROTECT)
    film = models.ForeignKey(Film, verbose_name=u'评分电影', on_delete=models.PROTECT)
    score = models.IntegerField(blank=False, verbose_name=u'分值')

    class Meta:
        verbose_name = u'评分'
        verbose_name_plural = verbose_name

    def __str__(self):
        return u'%s %s %s' % (self.film.name, self.score, self.user.username)



# 对电影的评论 短影评
class FilmComment(models.Model):
    film = models.ForeignKey(Film, verbose_name=u'电影', on_delete=models.PROTECT)
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    content = models.CharField(max_length=1024, verbose_name=u'评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    active = models.BooleanField(default=True, verbose_name=u'情况')

    class Meta:
        verbose_name = u'短影评'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.film.name


# 电影的影评 长影评
class FilmReview(models.Model):
    film = models.ForeignKey(Film, verbose_name=u'电影', on_delete=models.PROTECT)
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    title = models.CharField(max_length=50, verbose_name=u'标题')
    subtitle = models.CharField(max_length=50, verbose_name=u'副标题')
    content = models.TextField(verbose_name="内容")
    commented_members = models.IntegerField(default=0, verbose_name=u'评论人数')
    hits = models.IntegerField(default=0, verbose_name=u'点击量')
    thumbnail = models.ImageField(verbose_name=u'缩略图', upload_to='upload')
    active = models.BooleanField(default=True, verbose_name=u'情况')

    class Meta:
        verbose_name = u'长影评'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class FilmReviewComment(models.Model):
    film_review = models.ForeignKey(FilmReview, verbose_name=u'影评', on_delete=models.PROTECT)
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    content = models.CharField(max_length=1024, verbose_name=u'内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    active = models.BooleanField(default=True, verbose_name=u'情况')

    class Meta:
        verbose_name = u'影评评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return u'%s %s' % (self.film_review.title, self.author.username)


# check
class FilmReviewGoods(models.Model):
    toNews=models.ForeignKey(Film, verbose_name=u'影评', on_delete=models.PROTECT)
    fromUser=models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    isGood=models.BooleanField(verbose_name="是否点赞",default=False)
    time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    class Meta:
        verbose_name = u'点赞'
        verbose_name_plural = verbose_name

        ordering = ['time']


# check
class News(models.Model):
    title = models.CharField(max_length=200, verbose_name=u'新闻标题')
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    content = models.TextField(verbose_name=u'内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    hits = models.IntegerField(default=0, verbose_name=u'点击量')
    active = models.BooleanField(default=True, verbose_name=u'情况')
    goodNum = models.IntegerField(default=0, verbose_name=u'点赞数')
    commented_members = models.IntegerField(default=0, verbose_name=u'评论人数')
    picture = models.ImageField(verbose_name=u'图片', upload_to='upload')

    class Meta:
        verbose_name = u'新闻'
        verbose_name_plural = verbose_name

        ordering = ['-create_time']

    def __str__(self):
        return self.title

# check
class NewsComment(models.Model):
    news = models.ForeignKey(News, verbose_name=u'新闻', on_delete=models.PROTECT)
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    content = models.CharField(max_length=1024, verbose_name=u'内容')
    create_time = models.DateTimeField(verbose_name=u'评论时间', default=django.utils.timezone.now,)
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    active = models.BooleanField(default=True, verbose_name=u'情况')

    class Meta:
        verbose_name = u'新闻评论'
        verbose_name_plural = verbose_name

        ordering = ['create_time']

    def __str__(self):
        return u'%s %s' % (self.news.title, self.author.username)

# check
class NewsGoods(models.Model):
    toNews=models.ForeignKey(News, verbose_name=u'新闻', on_delete=models.PROTECT)
    fromUser=models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    isGood=models.BooleanField(verbose_name="是否点赞",default=False)
    time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    class Meta:
        verbose_name = u'点赞'
        verbose_name_plural = verbose_name

        ordering = ['time']