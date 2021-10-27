"""阿里云 SDK调用 封装"""
"""依赖模块: oss2, aliyun-python-sdk-viapiutils, viapi-utils, aliyun-python-sdk-imagerecog"""

import json

from conf import Config
from viapi.fileutils import FileUtils
from aliyunsdkcore.client import AcsClient
from aliyunsdkimagerecog.request.v20190930 import ClassifyingRubbishRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException


def oss_file(file, suffix, is_local: bool = True):
    """调用临时对象存储"""
    file_utils = FileUtils(Config.aliyun_key, Config.aliyun_secret)
    return file_utils.get_oss_url(file, suffix, is_local)


def garbage_search(img_url: str) -> dict:
    """搜索图片是否为垃圾"""
    client = AcsClient(Config.aliyun_key, Config.aliyun_secret, Config.aliyun_region_id)
    response = ClassifyingRubbishRequest.ClassifyingRubbishRequest()
    response.set_ImageURL(img_url)
    res: bytes = client.do_action_with_exception(response)
    return json.loads(res.decode('utf-8'))
