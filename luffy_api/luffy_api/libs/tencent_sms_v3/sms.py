import random
from . import settings
from utils.log import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.sms.v20210111 import sms_client, models

# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile


# 写两个函数，
# 获取验证码的函数
def get_code(count=4):
    code_str = ''
    for i in range(count):
        num = random.randint(0, 9)
        code_str += str(num)
    return code_str


# 发送短信的函数

def send_sms(phone, code):
    try:
        cred = credential.Credential(settings.SECRETID, settings.SECRETKEY)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过。
        httpProfile = HttpProfile()
        httpProfile.reqMethod = "POST"  # post请求(默认为post请求)
        httpProfile.reqTimeout = 30  # 请求超时时间，单位为秒(默认60秒)
        httpProfile.endpoint = "sms.tencentcloudapi.com"  # 指定接入地域域名(默认就近接入)
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
        clientProfile.language = "en-US"
        clientProfile.httpProfile = httpProfile
        client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)
        req = models.SendSmsRequest()
        req.SmsSdkAppId = settings.APPID
        req.SignName = settings.SIGNAME
        req.TemplateId = settings.TemplateId
        req.TemplateParamSet = [code,]
        req.PhoneNumberSet = ["+86%s"%phone,]
        req.SessionContext = ""
        req.ExtendCode = ""
        req.SenderId = ""
        client.SendSms(req)
        # print(resp.to_json_string(indent=2))
        return True
    except TencentCloudSDKException as err:
        # 如果短信发送失败，记录一下日志--》一旦使用了记录日志，使用的是django 的日志，以后这个包，给别的框架用，要改日志
        logger.error('手机号为：%s发送短信失败，失败原因：%s', phone, str(err))