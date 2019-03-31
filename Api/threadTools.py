# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MathWeChat.settings")# project_name 项目名称
# django.setup()

##通过thread 实现django中
import threading
import time

from django.core.mail import send_mail
from MyAndroid.settings import DEFAULT_FROM_EMAIL as FromEmail

# 发送邮件
class sendEmailThread(threading.Thread):
    def __init__(self,title,content,toEmail):
        super(sendEmailThread, self).__init__()
        self.content=content
        self.title=title
        self.toEmail=toEmail

    def run(self):
        try:
            send_mail(self.title,self.content, FromEmail,
                      [self.toEmail], fail_silently=False)
        except:
            pass
            # print("发送邮件出错")




# def test(obj):
#     temp=improtUserInfo(100)
#     temp.start()
#     temp1 = improtUserInfo(1)
#     temp1.start()
#     # print("1231232")
#
#
# test("1")