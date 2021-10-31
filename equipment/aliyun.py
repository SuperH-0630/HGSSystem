"""阿里云 SDK调用 封装"""
"""依赖模块: oss2, aliyun-python-sdk-viapiutils, viapi-utils, aliyun-python-sdk-imagerecog"""

import json

from conf import Config
from tool.type_ import *
from viapi.fileutils import FileUtils
from aliyunsdkcore.client import AcsClient
from aliyunsdkimagerecog.request.v20190930 import ClassifyingRubbishRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException  # 外部需要使用


class AliyunClientException(ClientException):
    ...


class AliyunServerException(ServerException):
    ...


class Aliyun:
    def __init__(self,
                 key: Optional[str] = Config.aliyun_key,
                 secret: Optional[str] = Config.aliyun_secret,
                 region_id: Optional[str] = Config.aliyun_region_id):
        self._key = key
        self._secret = secret
        self._region_id = region_id

    def oss_file(self, file, suffix, is_local: bool = True):
        """调用临时对象存储"""
        file_utils = FileUtils(self._key, self._secret)
        return file_utils.get_oss_url(file, suffix, is_local)

    def garbage_search(self, img_url: str) -> dict:
        """搜索图片是否为垃圾"""
        client = AcsClient(self._key, self._secret, self._region_id)
        response = ClassifyingRubbishRequest.ClassifyingRubbishRequest()
        response.set_ImageURL(img_url)
        res: bytes = client.do_action_with_exception(response)
        return json.loads(res.decode('utf-8'))
