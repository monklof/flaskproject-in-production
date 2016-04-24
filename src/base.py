# coding: utf-8
"""提供一些Flask Web的基本工具
"""

import os, sys
import datetime
import contextlib
import hashlib
import pytz
from tzlocal import get_localzone
from flask import jsonify, Flask
from flask.helpers import safe_join


def convert_datatype(val):
    """将python数据转换成json, 目前支持的有: 
    date/datetime -> iso字符串
    """
    if type(val) == dict:
        converted = {}
        for k in val:
            if type(k) != unicode and type(k) != str:
                raise TypeError('the key of dict must be strings.')
            converted[k] = convert_datatype(val[k])
        return converted
    elif type(val) == list or type(val) == set:
        converted = []
        for v in val:
            converted.append(convert_datatype(v))
        return converted
    elif type(val) == datetime.datetime or type(val) == datetime.date:
        return utc_isoformat(val)
    else:
        return val

local_tz = get_localzone()
def utc_isoformat(date):
    '''translate the date to utc ISO 8601 standard,
    so that the browser side can parse it simply (new Date(date_str))
    '''
    aware = local_tz.localize(date, is_dist=None)
    aware.astimezone(pytz.utc)
    return aware.isoformat()

# api接口调用协议, 返回json
# 调用成功: success=True, data=reponse
# 调用失败: success=False, msg = error msg
def send_success(data=None):
    ''' send success data to front end. 
    the key of data must be type `string`'''
    return jsonify({
        'success': True,
        'data': convert_datatype(data)})

def send_error(msg=""):
    return jsonify({
        'success': False,
        'msg': msg or "request failed on the server!"
        })

# from https://gist.github.com/monklof/917f4e4cdb1cd304d537df6cc62c35c7
# Injects an "h" parameter on the URLs of static files that contains a hash of
# the file.  This allows the use of aggressive cache settings on static files,
# while ensuring that content changes are reflected immediately due to the
# changed URLs.  Hashes are cached in-memory and only checked for updates when
# the file modtime changes.
class AddStaticFileHashFlask(Flask):
    def __init__(self, *args, **kwargs):
        super(AddStaticFileHashFlask, self).__init__(*args, **kwargs)
        self._file_hash_cache = {}
    def inject_url_defaults(self, endpoint, values):
        super(AddStaticFileHashFlask, self).inject_url_defaults(endpoint, values)
        if endpoint == "static" and "filename" in values:
            filepath = safe_join(self.static_folder, values["filename"])
            if os.path.isfile(filepath):
                cache = self._file_hash_cache.get(filepath)
                mtime = os.path.getmtime(filepath)
                if cache != None:
                    cached_mtime, cached_hash = cache
                    if cached_mtime == mtime:
                        values["h"] = cached_hash
                        return
                h = hashlib.md5()
                with contextlib.closing(open(filepath, "rb")) as f:
                    h.update(f.read())
                h = h.hexdigest()
                self._file_hash_cache[filepath] = (mtime, h)
                values["h"] = h

    
