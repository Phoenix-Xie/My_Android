
from . import views
from django.conf.urls import url,include
app_name='API'
from django.views.decorators.cache import cache_page


urlpatterns = [
    # 注册登录相关
    url(r'^register/', views.register.as_view(), name="register"), # 注册
    url(r'^login/', views.login.as_view(), name="login"), # 登录
    url(r'^LookForPwd/', views.LookForPwd.as_view(), name="LookForPwd"), # 找回密码
    url(r'^changePwd/', views.changePwd.as_view(), name="changePwd"),
    url(r'^sendCheckCode/', views.sendCheckCode.as_view(), name="sendCheckCode"), # 注册时发邮箱的验证码
    url(r'^changePwdByself/', views.changePwdByself.as_view(), name="changePwdByself"), # 已知密码时修改密码

    # 个人中心
    url(r'^changeHeadImage/', views.changeHeadImage.as_view(), name="changeHeadImage"), # 修改头像
    url(r'^changeNickName/', views.changeNickName.as_view(), name="changeNickName"), # 修改昵称
    ## 我的评论
    url(r'^getMyFirmComment/', views.getMyFirmComment.as_view(), name="getMyFirmComment"), # 我的影评
    url(r'^getMyNewsComment/', views.getMyNewsComment.as_view(), name="getMyNewsComment"), # 我的新闻评论
    url(r'^deleteMyNewsComment/', views.deleteMyNewsComment.as_view(), name="deleteMyNewsComment"), # 删除我的评论

    # url(r'^getMy/', views.changeNickName.as_view(), name="changeNickName"), # 修改昵称
    # url(r'^changeNickName/', views.changeNickName.as_view(), name="changeNickName"), # 修改昵称

    # 今日热点
    url(r'^getNewsList/', cache_page(10)(views.getNewsList.as_view()), name="getNewsList"),
    url(r'^getPointNews/',(views.getPointNews.as_view()), name="getPointNews"),
    url(r'^goodPointNews/',(views.goodPointNews.as_view()), name="goodPointNews"),
    url(r'^replyPointNews/',(views.replyPointNews.as_view()), name="replyPointNews"),

    # 影评
    url(r'^getHotFilmReview/', cache_page(10)(views.getHotFilmReview.as_view()), name="getHotFilmReview"),
    url(r'^getPointFilmReview/',(views.getPointFilmReview.as_view()), name="getPointFilmReview"),
    url(r'^goodPointFilmReview/',(views.goodPointFilmReview.as_view()), name="goodPointFilmReview"),
    url(r'^replyPointFilmReview/',(views.replyPointFilmReview.as_view()), name="replyPointFilmReview"),

    # 电影
    url(r'^getFilmList/', cache_page(10)(views.getFilmList.as_view()), name="getFilmList"),
    url(r'^getPointFilm/',(views.getPointFilm.as_view()), name="getPointFilm"),
    url(r'^scorePointFilm/',(views.scorePointFilm.as_view()), name="scorePointFilm"),
    url(r'^reviewPointFilm/',(views.reviewPointFilm.as_view()), name="reviewPointFilm"),# 发长影评,这个接口小伙子们不要了,辣鸡玩意

    url(r'^replyPointFilm/',(views.replyPointFilm.as_view()), name="replyPointFilm"),# 发短影评


    # 通用信息获取


]
