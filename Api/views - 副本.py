from django.shortcuts import render

from Api.threadTools import sendEmailThread
from Api.tools import CrossDomainReturn, makeSession, encryptPwd, judgePwd, makeCheckCode, checkUserLogin, \
    makeRegisterCheckCode
from Api.models import *
from django.shortcuts import render
from django.views.generic.base import View
from django.core import serializers

from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.cache import cache
# Create your views here.


class register(View):
    '''
    注册函数
    '''

    def get(self, request):
        # print("get")
        result = {'state': 404, 'msg': "非法请求"}
        return CrossDomainReturn(result)

    def post(self, request):
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        nickname=request.POST.get("nickname",username)
        veriCode=str(request.POST.get("veriCode")) # 验证码
        password=encryptPwd(username, password)

        user = User.objects.filter(username=username)

        if (len(user) > 0):
            result = {'state': "-3", "msg": "该账号已被注册,请直接登录"}
        else:
            con = get_redis_connection("default")
            if con.exists(email) == 0:
                result = {'state': "-1", "msg": "验证码已过期"}
            else:
                trueCode=str(con.get(email))
                print(trueCode)
                print(veriCode)
                if(trueCode==veriCode):
                    con.set(email, None,1)
                    user=User.objects.create(username=username,email=email,password=password,nickName=nickname)
                    user.save()
                    result = {'state': "1", "session": makeSession(user.username), "msg": "注册成功"}
                else:
                    result = {'state': "-2", "msg": "验证码错误"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


class login(View):
    '''
        登录
        返回值
         statu -2 密码错误|-1 账号不存在| 0 未知错误 | 1 成功
         session 用户状态保留标志
    '''

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username)

        if (len(user) > 0):
            if judgePwd(username, password):  # 密码正确
                user = User.objects.get(username=username)
                session=makeSession(username)
                result = [{"statu": 1, "session": session, "nickName": user.nickName,
                           "registerTime": user.registerTime.strftime("%Y-%m-%d %H:%M:%S"),
                           "username": user.username,"headImage":str(user.headImage),
                           "email":user.email
                           }]
            else:
                result = [{"statu": -2, "msg": "密码不正确"}]

        else:
            result = [{"statu": -1, "msg": "账号不存在,请先注册"}]

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


class LookForPwd(View):
    """
    找回密码
    """

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")

        user = User.objects.filter(username=username,email=email)

        if (len(user) > 0):
            content = "小伙子你好,你本次修改密码的验证码为:" + makeCheckCode(username)
            sendMail = sendEmailThread('时光网-找回密码', content, email)
            sendMail.start()
            result = [{"statu": 1, "msg": "邮件发送成功"}]
        else:
            result = [{"statu": -1, "msg": "学号不存在或邮箱错误"}]

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


# 修改密码
class changePwd(View):
    '''修改密码'''
    def post(self, request):
        username = request.POST.get("username")
        code = request.POST.get("code","None")
        newPwd = request.POST.get("newPwd")


        user = User.objects.filter(username=username)
        if len(user) <= 0:
            result = [{"statu": -1, "msg": "该页面已过期"}]
        else:
            user=user[0]
            if user.checkCode == code and code != "None" and user.checkCode!="None":
                user.password = encryptPwd(username, newPwd)
                makeSession(username)
                user.checkCode = "None"
                user.save()
                result = [{"statu": 1, "msg": "修改成功!"}]
            else:
                result = [{"statu": -2, "msg": "验证码不正确"}]
        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


# 发送验证码
class sendCheckCode(View):
    '''修改密码'''
    def post(self, request):
        email = request.POST.get("email")
        user = User.objects.filter(email=email)
        if len(user) > 0:
            result = [{"statu": -1, "msg": "该邮箱已被注册"}]
        else:
            code=makeRegisterCheckCode(email)
            content ="你好,你本次操作的验证码为:" + str(code)
            sendMail = sendEmailThread("My_Android", content, email)
            sendMail.start()
            result = [{"statu": 1, "msg": "发送验证码成功!"}]

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 根据原密码修改密码
class changePwdByself(View):
    '''修改密码'''
    def post(self, request):
        oldPassword = request.POST.get("oldPassword")
        newPassword = request.POST.get("newPassword")
        username = request.POST.get("username")
        user = User.objects.filter(username=username)
        if len(user) > 0:
            result = [{"statu": -1, "msg": "账号不存在"}]
        else:
            user=user[0]
            if judgePwd(username, oldPassword):
                user.password = encryptPwd(username, newPassword)
                user.save()
                makeSession(username)
                result = [{"statu": 1, "msg": "修改成功,请重新登录!"}]
            else:

                result = [{"statu": -2, "msg": "原密码错误!"}]

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 修改头像
class changeHeadImage(View):
    '''修改头像'''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)

        heheadImage = request.FILES.get("headImage", "default/1.png")
        user.headImage = heheadImage
        user.save()
        result = {"state": 1, "msg": "修改成功", "imageHead": str(user.headImage)}
        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


# 修改昵称
class changeNickName(View):
    '''修改昵称'''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        nickName = request.POST.get("nickName",None)
        if nickName !=None and nickName!="":
            user.nickName = nickName
            user.save()
            result = {"state": 1, "msg": "修改成功", "nickName": str(user.nickName)}

        else:
            result = {"state": -2, "msg": "昵称长度不合法", "nickName": str(user.nickName)}
        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)



# 我的影评
class getMyFirmComment(View):
    ''''''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)

        posts=FilmReview.objects.filter(user=user).order_by("-create_time")


        result = []
        for one in posts:
            temp = {"id": one.id, "title": one.title, "firmName": one.firm.name,
                    "thumbnail":str(one.thumbnail),
                    "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
                    }
            result.append(temp)

        posts = serializers.serialize("json", posts)

        result = {"state": 1, "result": result}
        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 我的新闻评论
class getMyNewsComment(View):
    ''''''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)

        posts = NewsComment.objects.filter(user=user).order_by("-create_time")

        result = []
        for one in posts:
            temp = {"id": one.id, "title": one.title, "firmName": one.news.title,
                    "thumbnail": str(one.news.picture),
                    "create_time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
                    }
            result.append(temp)



        result = {"state": 1, "result": result}
        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


# 删除我的评论
class deleteMyNewsComment(View):
    ''''''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)

        id=request.POST.get("id") # 要删除对象的id
        type=str(request.POST.get("id",0)) # 要删除的评论类型,0是电影的,1是新闻的
        if type=='0':
            temp=FilmComment.objects.filter(id=id,author=user)
        elif type=="1":
            temp = NewsComment.objects.filter(id=id, author=user)
        else:
            temp = {"state": -3, "msg": "数据不全"}
            return CrossDomainReturn(temp)
        if len(temp) > 0:
            temp = temp[0]
            temp.delete()
            temp = {"state": 1, "msg": "删除成功"}
        else:
            temp = {"state": -2, "msg": "删除失败,无权或无文章"}


        return CrossDomainReturn(temp)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 获取新闻列表
class getNewsList(View):
    ''''''

    def get(self, request):
        headId = int(request.GET.get("head", 0))
        type = int(request.GET.get("type", 6))
        number = int(request.GET.get("number", 5))

        if headId != 0:

            posts = News.objects.filter( id__lt=headId).order_by("-create_time")[:number]
        else:
            posts = News.objects.all().order_by("-create_time")[:number]

        result = []
        for one in posts:
            temp = {"id": one.id, "author": one.author.nickName, "photo": str(one.picture),
                    "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")), "Title": one.title,
                    # "clickNum": one.hits, "replyNum": one.commented_members,
                    }
            result.append(temp)

        # posts = serializers.serialize("json", posts)

        result = {"state": 1, "result": result}
        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 获取指定id的新闻
class getPointNews(View):
    '''
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        operaType=int(request.POST.get("operaType", 0)) # 1点赞 0取消赞
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = News.objects.filter(id=id)
        if one.count()<= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)

        news=one[0]
        news.hits+=1
        news.save()


        isGood=False
        goods = NewsGoods.objects.filter(fromUser=user, toNews__id=id)

        if (goods.count() != 0):
            isGood=True



        replys = NewsComment.objects.filter(news__id=id)
        replyNum=replys.count()
        reply = []
        for one in replys:
            temp = {"id": one.id, "author": one.author.nickName,"autherHeadPhoto":str(one.author.headImage),
                    "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
                    "content":one.content
                    }
            reply.append(temp)

        one=news
        temp = {"id": one.id, "author": one.author.nickName, "photo": str(one.picture),
                "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")), "Title": one.title,
                "clickNum": one.hits, "replyNum": one.commented_members, "content": one.Content,
                "isGood":isGood,"replys": reply,"replyNum":replyNum,
                }


        result = {"state": 1, "result": temp}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 点赞指定id的新闻
class goodPointNews(View):
    '''
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        operaType=int(request.POST.get("operaType", 0)) # 1点赞 0取消赞
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = News.objects.filter(id=id)
        if one.count()<= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)

        news=one[0]

        goods=NewsGoods.objects.filter(fromUser=user,toNews__id=id)

        if(goods.count()==0):
            if(operaType==1):
                NewsGoods.objects.create(fromUser=user,toNews_id=id,isGood=True)
                news.goodNum+=1
                news.save()
        else:
            goods=goods[0]
            if(operaType==1):
                goods.isGood=True
                news.goodNum += 1
                news.save()
            else:
                goods.isGood=False
                news.goodNum -= 1
                news.save()
            goods.save()




        # if one.fromUser == user:  # 如果是本人登录的话,更新最后的已读访问
        #     one.lastDetectNum = one.replyNum
        #     aa = ReplyInfo.objects.filter(toPost=one)
        #     aa.update(isRead=True)
        # one.save()
        #
        #
        # replys = NewsComment.objects.filter(news__id=id)
        #
        # reply = []
        # for one in replys:
        #     temp = {"id": one.id, "author": one.author.nickName,
        #             "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
        #             "content":one.content
        #             }
        #     reply.append(temp)
        #
        # temp = {"id": one.id, "author": one.author.nickName, "photo": str(one.picture),
        #         "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")), "Title": one.title,
        #         "clickNum": one.hits, "replyNum": one.commented_members, "content": one.Content,
        #         "replys": reply
        #         }


        result = {"state": 1, "result": "成功"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 回复指定id的新闻
class replyPointNews(View):
    '''
    news = models.ForeignKey(News, verbose_name=u'新闻', on_delete=models.PROTECT)
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    content = models.CharField(max_length=1024, verbose_name=u'内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    active = models.BooleanField(default=True, verbose_name=u'情况')
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        operaType = int(request.POST.get("operaType", 0))  # 1点赞 0取消赞
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = News.objects.filter(id=id)
        if one.count() <= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)

        news = one[0]

        content=request.POST.get("content")
        NewsComment.objects.create(news=news,author=user,content=content)
        news.commented_members += 1
        news.save()

        result = {"state": 1, "result": "成功"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)





# 获取热门影评
class getHotFilmReview(View):
    def get(self, request):
        headId = int(request.GET.get("head", 0))
        number = int(request.GET.get("number", 10))

        if headId != 0:

            posts = FilmReview.objects.filter(id__lt=headId,active=True).order_by("-create_time")[:number]
        else:
            posts = FilmReview.objects.filter(active=True).order_by("-create_time")[:number]

        result = []
        for one in posts:
            temp = {'comment_id': one.id,
                'title': one.title,
                'subtitle': one.subtitle,
                'author_id': one.author.id,
                'author_name': one.author.username,
                'author_head': one.author.head_image.url,
                'comment_num': one.commented_members,
                'create_time': str(one.create_time.strftime('%Y-%m-%d %H:%M:%S')),
                'update_time': str(one.update_time.strftime('%Y-%m-%d %H:%M:%S')),
                'image': one.thumbnail.url,}
            result.append(temp)

        posts = serializers.serialize("json", posts)
        result = {"state": 1, "result": result}
        return CrossDomainReturn(result)

# 获取指定id的影评
class getPointFilmReview(View):
    '''
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))


        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = FilmReview.objects.filter(id=id, active=True)
        if one.count()<= 0:
            result = {"state": -2, "msg": "该影评不存在或已被删除"}
            return CrossDomainReturn(result)

        fileReview=one[0]
        fileReview.hits+=1
        fileReview.save()

        # if one.fromUser == user:  # 如果是本人登录的话,更新最后的已读访问
        #     one.lastDetectNum = one.replyNum
        #     aa = ReplyInfo.objects.filter(toPost=one)
        #     aa.update(isRead=True)

        isGood=False
        goods = FilmReviewGoods.objects.filter(fromUser=user, toNews__id=id)

        if (goods.count() != 0):
            isGood=True


        replys = FilmReviewComment.objects.filter(news__id=id,active=True)
        replyNum = replys.count()
        reply = []
        for one in replys:
            temp = {"id": one.id, "author": one.author.nickName,"autherHeadPhoto":str(one.author.headImage),
                    "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
                    "content":one.content
                    }
            reply.append(temp)

        one=fileReview
        temp = {"id": one.id, "author": one.author.nickName, "photo": str(one.picture),
                "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")), "Title": one.title,
                "clickNum": one.hits, "replyNum": one.commented_members, "content": one.Content,
                "isGood":isGood,"replys": reply,"replyNum":replyNum
                }


        result = {"state": 1, "result": temp}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 点赞指定id的影评
class goodPointFilmReview(View):
    '''
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        operaType=int(request.POST.get("operaType", 0)) # 1点赞 0取消赞
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = FilmReview.objects.filter(id=id)
        if one.count()<= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)

        news=one[0]

        goods=FilmReviewGoods.objects.filter(fromUser=user,toNews__id=id)

        if(goods.count()==0):
            if(operaType==1):
                FilmReviewGoods.objects.create(fromUser=user,toNews_id=id,isGood=True)
                news.goodNum+=1
                news.save()
        else:
            goods=goods[0]
            if(operaType==1):
                goods.isGood=True
                news.goodNum += 1
                news.save()
            else:
                goods.isGood=False
                news.goodNum -= 1
                news.save()
            goods.save()


        # if one.fromUser == user:  # 如果是本人登录的话,更新最后的已读访问
        #     one.lastDetectNum = one.replyNum
        #     aa = ReplyInfo.objects.filter(toPost=one)
        #     aa.update(isRead=True)
        # one.save()
        #
        #
        # replys = NewsComment.objects.filter(news__id=id)
        #
        # reply = []
        # for one in replys:
        #     temp = {"id": one.id, "author": one.author.nickName,
        #             "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
        #             "content":one.content
        #             }
        #     reply.append(temp)
        #
        # temp = {"id": one.id, "author": one.author.nickName, "photo": str(one.picture),
        #         "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")), "Title": one.title,
        #         "clickNum": one.hits, "replyNum": one.commented_members, "content": one.Content,
        #         "replys": reply
        #         }


        result = {"state": 1, "msg": "成功"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 回复指定id的影评
class replyPointFilmReview(View):
    '''
    news = models.ForeignKey(News, verbose_name=u'新闻', on_delete=models.PROTECT)
    author = models.ForeignKey(User, verbose_name=u'作者', on_delete=models.PROTECT)
    content = models.CharField(max_length=1024, verbose_name=u'内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    active = models.BooleanField(default=True, verbose_name=u'情况')
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        operaType = int(request.POST.get("operaType", 0))  # 1点赞 0取消赞
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = FilmReview.objects.filter(id=id)
        if one.count() <= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)

        news = one[0]

        content=request.POST.get("content")
        FilmReviewComment.objects.create(news=news,author=user,content=content)

        news.commented_members+=1
        news.save()
        result = {"state": 1, "result": "成功"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)




# 获取电影
class getFilmList(View):
    def get(self, request):
        headId = int(request.GET.get("head", 0))
        number = int(request.GET.get("number", 10))
        type = int(request.GET.get("type", 0)) # 0 未上映 1 上映
        isOnScreen=False if type==0 else True
        if headId != 0:
            posts = Film.objects.filter(id__lt=headId,active=True,isOnScreen=isOnScreen).order_by("-on_time")[:number]
        else:
            posts = Film.objects.filter(active=True,isOnScreen=isOnScreen).order_by("-on_time")[:number]

        result = []
        for one in posts:
            temp = {
                'title': one.name,
                'film_id': one.id,
                'image': one.head_image.url,
                'info': one.info,
                'release_date': str(one.on_time.strftime('%H:%M:%S')),
                'mark': one.score,
                'marked_members': one.marked_members,
                'commented_members': one.commented_member,}
            result.append(temp)

        posts = serializers.serialize("json", posts)
        result = {"state": 1, "result": result}
        return CrossDomainReturn(result)


# 获取指定id的影评
class getPointFilm(View):
    '''
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))


        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = Film.objects.filter(id=id, active=True)
        if one.count()<= 0:
            result = {"state": -2, "msg": "该电影不存在或已被删除"}
            return CrossDomainReturn(result)

        # fileReview=one[0]
        # fileReview.hits+=1
        # fileReview.save()

        # if one.fromUser == user:  # 如果是本人登录的话,更新最后的已读访问
        #     one.lastDetectNum = one.replyNum
        #     aa = ReplyInfo.objects.filter(toPost=one)
        #     aa.update(isRead=True)

        the_film = one[0]
        isGood=False
        goods = Mark.objects.filter(user=user, firm=the_film)

        if (goods.count() != 0):
            isGood=True

        replys = FilmReview.objects.filter(film__id=id, active=True)
        replyNum = replys.count()
        reply = []

        for one in replys:
            temp = {"id": one.id, "author": one.author.nickName, "autherHeadPhoto": str(one.author.headImage),
                    "Time": str(one.create_time.strftime("%Y-%m-%d %H:%M:%S")),
                    "title": one.title
                    }
            reply.append(temp)


        temp = {"id": the_film.id,
                'title': the_film.name,
                       'image': the_film.head_image.url,
                       'film_id': the_film.id,
                       'mark': the_film.score/the_film.marked_members,
                       'relase_date': str(the_film.on_time.strftime('%Y-%m-%d')),
                       'time': str(the_film.on_time.strftime('%H:%M:%S')),
                       'marked_members': the_film.marked_members,
                       'comment_members': the_film.commented_member,
                        "isMark":isGood,"replys":reply,"replyNum":replyNum
                }


        result = {"state": 1, "result": temp}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 评分指定id的影评
class scorePointFilm(View):
    '''
    '''

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        score=int(request.POST.get("score", 0))
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = FilmReview.objects.filter(id=id)
        if one.count()<= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)

        firm=one[0]

        isGood = False
        goods = Mark.objects.filter(user=user, firm__id=id)


        if(goods.count()==0):
            Mark.objects.create(user=user,firm=firm,score=score)
            firm.marked_members+=1
            firm.score+=score
            firm.save()
            result = {"state": 1, "msg": "成功"}
        else:
            result = {"state": -4, "msg": "无权"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)

# 给指定id的影评写影评
class reviewPointFilm(View):

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))

        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = Film.objects.filter(id=id)
        if one.count() <= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)
        firm=one[0]
        '''
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
        '''
        title = request.POST.get("title", "None")
        subtitle = request.POST.get("subtitle", "None")
        content = request.POST.get("content","None")
        thumbnail = request.File.get("thumbnail", "None")

        FilmReview.objects.create(active=True,author=user,title=title,firm=firm,subtitle=subtitle,
                                  content=content,thumbnail=thumbnail)
        firm.commented_member+=1
        firm.save()
        result = {"state": 1, "result": "成功"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)


# 给指定id的影评写短的评论
class replyPointFilm(View):

    def post(self, request):
        user = checkUserLogin(request)
        if not user:
            temp = {"state": -1, "msg": "尚未登陆"}
            return CrossDomainReturn(temp)
        id = int(request.POST.get("id", 0))
        if id == 0:
            result = {"state": -3, "msg": "错误请求"}
            return CrossDomainReturn(result)
        one = Film.objects.filter(id=id)
        if one.count() <= 0:
            result = {"state": -2, "msg": "该帖子不存在或已被删除"}
            return CrossDomainReturn(result)
        firm = one[0]

        title = request.POST.get("title", "None")
        content = request.POST.get("content", "None")

        FilmComment.objects.create(active=True, author=user, title=title, firm=firm,
                                  content=content)
        firm.commented_member += 1
        firm.save()
        result = {"state": 1, "result": "成功"}

        return CrossDomainReturn(result)

    def other(self, request):
        result = "非法请求"
        return CrossDomainReturn(result)