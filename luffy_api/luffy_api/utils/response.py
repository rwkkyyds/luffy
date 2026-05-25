from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, status=100, msg='成功', http_status=None, template_name=None, headers=None, exception=False,
                 content_type=None, **kwargs):
        data = {
            'status': status,
            'msg': msg
        }
        if kwargs:
            data.update(kwargs)  # 这句话什么意思？{token:adfads,name:asdfa}

        super().__init__(data=data, status=http_status, template_name=template_name, headers=headers,
                         exception=exception, content_type=content_type)


# res=APIResponse(token='asdfadsf') # -->{status:100,msg:成功，token：asdfadsf}
# # res=APIResponse(result=[{},{},{}]) # -->{status:100,msg:成功，result：[{},{},{}]}
# res=APIResponse(status=101,msg='失败') # -->{status:101,msg:失败}
# res=APIResponse(status=101,msg='失败',http_status=201) # -->{status:101,msg:失败}