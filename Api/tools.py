import requests
from .models import *
from django.http import HttpResponse
import random, string, json
from django.contrib.auth.hashers import make_password, check_password
from django_redis import get_redis_connection
from django.core.cache import cache


def CrossDomainReturn(result):
    response = HttpResponse(json.dumps(result), content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Max-Age'] = '1000'
    response['Access-Control-Allow-Headers'] = '*'
    return response


# 生成密码
def encryptPwd(username, pwd):
    return make_password(str(pwd) + str(username), None, 'pbkdf2_sha256')


# 判断用户是否注册

def judgeExist(username):
    user = User.objects.filter(username=username)
    if len(user):
        return True
    else:
        return False


# 判断密码是否正确
def judgePwd(username, pwd):
    user = User.objects.get(username=username)
    truePwd = user.password
    check = check_password(str(pwd) + str(username), truePwd)
    return check


# 生成Session串
def makeSession(username):
    user = User.objects.get(username=username)
    session = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
    temp = User.objects.filter(authSession=session)
    while (len(temp) > 0):
        session = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
        temp = User.objects.filter(authSession=session)
    user.authSession = session
    user.save()
    return session


def makeRegisterCheckCode(email):

    code = ''.join(str(random.randint(1000,9999)))
    con = get_redis_connection("default")
    con.set(email,code)
    return code


# print("重新获取")


# 发消息
def sendMessage(fromUser, toUser, content, isPhoto):
    if isPhoto == "True":
        newMessage = Message.objects.create(fromUser_id=fromUser, toUser_id=toUser, image=content,
                                            Time=datetime.datetime.now())
        result = {"state": 1, "msg": "发送成功","image":str(newMessage.image)}
    else:
        newMessage = Message.objects.create(fromUser_id=fromUser, toUser_id=toUser, Content=content,
                                            Time=datetime.datetime.now())
        result = {"state": 1, "msg": "发送成功"}
    newMessage.save()
    return result



# 发帖子
def postPost(fromUser, title, content):
    newPost = MathCommunication.objects.create(fromUser=fromUser, Title=title, Content=content,
                                               Time=datetime.datetime.now())
    newPost.save()


# 查看消息
def getMessage(stuCode, messageId):
    message = Message.objects.get(id=messageId)
    message.isRead = True
    message.save()
    return message


def getTwoUserNewInfo(fromId, toId):
    msgs = Message.objects.filter(fromUser_id=fromId, toUser_id=toId, isRead=False)
    result = []
    for temp in msgs:
        one = {"Content": temp.Content, "Time": temp.Time.strftime("%Y-%m-%d %H:%M:%S"), "image": str(temp.image)}
        temp.isRead = True
        temp.save()
        result.append(one)
    return result


# 查看帖子
def getPostContent(stuCode, postId):
    post = MathCommunication.objects.get(id=postId)
    if (post.fromUser.stuCode == stuCode):  # 若查看的人是发帖的人,则更新其最后一次查看的访客量
        post.lastDetectNum = post.replyNum
        post.save()
    return post


def getUserBySession(session):
    user = User.objects.filter(authSession=session)
    if len(user) <= 0:
        return None
    else:
        return user[0]


# 判断用户是否登录
def checkUserLogin(request):
    try:
        session = request.POST.get("session")
        result = getUserBySession(session)
        if result == None:
            return False
        else:
            return result
    except:
        return False


    # try:
    #     session = request.POST.get("session")
    #     if cache.has_key("usersessionis" + str(session)):
    #         result = cache.get("usersessionis" + str(session))
    #     else:
    #         result = getUserBySession(session)
    #         if result == None:
    #             return False
    #         else:
    #             cache.set("usersessionis" + str(session),result,60*10)
    #     return result
    # except:
    #     return False


# 生成验证码
def makeCheckCode(username):
    user = User.objects.get(username=username)
    code = "".join(random.sample(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], 5)).replace(" ", "")
    user.checkCode = code
    user.save()
    return code


# 生成随机文件名
def makeRandomFileName(stuCode):
    import datetime
    import random
    for i in range(0, 1):
        nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前的时间
        randomNum = random.randint(0, 100)  # 生成随机数n,其中0<=n<=100
        if randomNum <= 10:
            randomNum = str(0) + str(randomNum)
        uniqueNum = str(nowTime) + str(randomNum)
    return "" + str(uniqueNum) + "-" + str(stuCode)


# 推送消息
def pushMsg(sendUser:User,toUser:User,message):
    if sendUser.isGroupUser==False: # 判断是否为管理员信息
        return False
    result=True

    while(result):
        formId=useFormId(toUser.openid)
        if formId==False:
            break

        #url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=ACCESS_TOKEN"
        data = {
            "touser": toUser.openid,
            "template_id": template_id,
            "page": page,
            "form_id": formId,
            "data": {"keyword1": {"value": sendUser.nickName},
                     "keyword2": {"value": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) },
                     "keyword3": {"value": message}
                     },
            "emphasis_keyword": 'keyword1.DATA'
        }
        accessTokenDead = True
        while accessTokenDead:
            access_token =get_access_token()
            if access_token==False:
                return
            # # print("token is:"+access_token)
            push_url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={}'.format(access_token)
            response=requests.post(push_url, json=data, timeout=3, verify=False)
            # print("推送的返回结果:"+response.text)
            #errcode =requests.post(push_url, json=data, timeout=3, verify=False).json()["errcode"]
            errcode=response.json()["errcode"]

            if errcode==40001: #token过期
                get_access_token()
            accessTokenDead=False
            if errcode==0:
                result=False

# base 推送
def basePushMsg(sendName,toUser:User,message):
    result=True

    while(result):
        formId=useFormId(toUser.openid)
        if formId==False:
            break

        #url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=ACCESS_TOKEN"
        data = {
            "touser": toUser.openid,
            "template_id": template_id,
            "page": page,
            "form_id": formId,
            "data": {"keyword1": {"value": sendName},
                     "keyword2": {"value": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) },
                     "keyword3": {"value": message}
                     },
            "emphasis_keyword": 'keyword1.DATA'
        }
        accessTokenDead = True
        while accessTokenDead:
            access_token =get_access_token()
            if access_token==False:
                return
            # # print("token is:"+access_token)
            push_url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={}'.format(access_token)
            response=requests.post(push_url, json=data, timeout=3, verify=False)
            # print("推送的返回结果:"+response.text)
            #errcode =requests.post(push_url, json=data, timeout=3, verify=False).json()["errcode"]
            errcode=response.json()["errcode"]

            if errcode==40001: #token过期
                get_access_token()
            accessTokenDead=False
            if errcode==0:
                result=False

# 获取access_token 两小时生效时间
def get_access_token():
    try:
        con = get_redis_connection("default")
        url = "https://api.weixin.qq.com/cgi-bin/token"
        param = {"grant_type": "client_credential",
                 "appid": appid,
                 "secret": appsecret,
                 }
        result = requests.get(url, params=param)
        result = result.json()
        result = result["access_token"]
        # print(result)
        con.set('access_token', result)
        con.expire('access_token', 60 * 60 * 2 - 30)
        return result
    except:
        return False

    # try:
    #     con = get_redis_connection("default")
    #     if con.exists('access_token') == 0:
    #         # print("重新获取")
    #         # url="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxed8a4944bd0f9654&secret=fc9cf79c84ee4c2064b88d655b65d2d9"
    #         url = "https://api.weixin.qq.com/cgi-bin/token"
    #         param = {"grant_type": "client_credential",
    #                  "appid": appid,
    #                  "secret": appsecret,
    #                  }
    #         result = requests.get(url, params=param)
    #         result = result.json()
    #         result = result["access_token"]
    #         # print(result)
    #         con.set('access_token', result)
    #         con.expire('access_token', 60 * 60 * 2 - 30)
    #
    #     else:
    #         result=con.get("access_token")
    #     return result
    # except:
    #     return False

# 收集用户的formId
def collectFormId(openId,formId):
    try:
        con = get_redis_connection("default")
        con.lpush(openId,formId)
        con.expire(openId, 60 * 60 * 24 * 7-30)
        # print("收集用户formId成功"+openId)
    except:
        # print("收集用户formId失败" + openId)
        return False


# 使用用户FormId
def useFormId(openId):
    try:
        con = get_redis_connection("default")
        if con.exists(openId)==0:
            return False
        result=con.rpop(openId)
        return result
    except:
        return False


def getOpenId(jscode):
    try:
        if cache.has_key(jscode):
            # print("mu有jscode")
            result=cache.get(jscode)
        else:
            # print("有jscode")
            url = "https://api.weixin.qq.com/sns/jscode2session"
            param = {"grant_type": "authorization_code",
                     "appid": appid,
                     "secret": appsecret,
                     "js_code": jscode,
                     }
            result = requests.get(url, params=param)
            # print("这," + str(result.content))
            result = result.json()

            result = result["openid"]
            cache.set(jscode, result)
        return result
    except:
        return None


def getPublicAccessToken():
    url = "https://api.weixin.qq.com/cgi-bin/token"
    param = {"grant_type": "client_credential",
                "appid": PublicAppid,
                "secret": PublicAppsecret,
                }
    result = requests.get(url, params=param)
    result = result.json()
    # print(result)
    result = result["access_token"]
    return result


def getPublicPushArticles(start=0,num=20):
    ACCESS_TOKEN = getPublicAccessToken()
    url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=" + ACCESS_TOKEN
    param = {"type": "news",
             "offset": start,
             "count": num,
             }
    param = json.dumps(param)
    result = requests.post(url, data=param)
    # # print(str(result.content, 'utf-8'))
    result =json.loads(str(result.content, 'utf-8'))
    # result = result.json()
    return result

def getAllPublicArticles():
    whetherContinue=True
    start=0
    while whetherContinue:
        results=getPublicPushArticles(start,20)
        if results["item_count"]<20:
            whetherContinue=False
        else:
            start+=20
        # print(results["item_count"])
        if results["item_count"]>0:
            # print("到门口了")
            for temp in results["item"]:
                # print("进来一次")
                news=temp["content"]
                create_time=news["create_time"]
                update_time=news["update_time"]
                news=news["news_item"]
                Dtime = datetime.datetime.fromtimestamp(create_time)

                #TODO 判断是否重复,需验证是否时间逆序
                if PushArticle.objects.filter(Time=create_time).count() > 0:
                    whetherContinue = False
                    break

                for article in news:

                    types = article["title"].split("|")
                    type = "None"
                    Title = types[0]

                    # 根据标签分类
                    if len(types) > 1:
                        type = types[0].replace(" ", "")
                        Title = types[1]
                        types = types[1].split(" ")
                        length = len(types) - 1

                        for temp in range(length):
                            type += types[temp].replace(" ", "")

                    # 判断是否重复
                    if PushArticle.objects.filter(Title=Title,Time=create_time).count()>0:
                        break
                    # print(Title)
                    PushArticle.objects.create(Title=Title,Link=article["url"],CoverLink=article["thumb_url"],Time=create_time,DateTime=Dtime,Tag=type)