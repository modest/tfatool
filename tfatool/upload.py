import math
import os
import arrow

from functools import partial

from . import cgi
from .info import DEFAULT_REMOTE_DIR, DEFAULT_MASTERCODE
from .info import WriteProtectMode, Upload, ResponseCode
from .connection import Connection
from .connection import DEFAULT_CONNECTION
from requests import RequestException


def upload_file(local_path: str, connection=DEFAULT_CONNECTION, remote_dir=DEFAULT_REMOTE_DIR):
    set_write_protect(WriteProtectMode.on, connection=connection)
    set_upload_dir(remote_dir, connection=connection)
    set_creation_time(local_path, connection=connection)
    post_file(local_path, connection=connection)
    set_write_protect(WriteProtectMode.off, connection=connection)


def set_write_protect(mode: WriteProtectMode, connection=DEFAULT_CONNECTION):
    response = get(connection=connection, **{Upload.write_protect: mode})
    if response.text != ResponseCode.success:
        raise UploadError("Failed to set write protect", response)
    return response


def set_upload_dir(remote_dir: str, connection=DEFAULT_CONNECTION):
    response = get(connection=connection, **{Upload.directory: remote_dir})
    if response.text != ResponseCode.success:
        raise UploadError("Failed to set upload directory", response)
    return response


def set_creation_time(local_path: str, connection=DEFAULT_CONNECTION):
    mtime = os.stat(local_path).st_mtime
    fat_time = _encode_time(mtime)
    encoded_time = _str_encode_time(fat_time)
    response = get(connection=connection, **{Upload.creation_time: encoded_time})
    if response.text != ResponseCode.success:
        raise UploadError("Failed to set creation time", response)
    return response


def post_file(local_path: str, connection=DEFAULT_CONNECTION):
    files = {local_path: open(local_path, "rb")}
    response = post(connection=connection, req_kwargs=dict(files=files))
    if response.status_code != 200:
        raise UploadError("Failed to post file", response)
    return response


def delete_file(remote_file: str, connection=DEFAULT_CONNECTION):
    response = get(connection=connection, **{Upload.delete: remote_file})
    if response.status_code != 200:
        raise UploadError("Failed to delete file", response)
    return response


def post(connection=DEFAULT_CONNECTION, req_kwargs=None, **params):
    prepped_request = prep_post(connection, req_kwargs, **params)
    return cgi.send(prepped_request)


def get(connection=DEFAULT_CONNECTION, req_kwargs=None, **params):
    prepped_request = prep_get(connection, req_kwargs, **params)
    return cgi.send(prepped_request)


def prep_req(prep_method, connection=DEFAULT_CONNECTION, req_kwargs=None, **params):
    req_kwargs = req_kwargs or {}
    params = {key.value: value for key, value in params.items()}
    return prep_method(connection=connection, req_kwargs=req_kwargs, **params)


prep_get = partial(prep_req, partial(cgi.prep_get, cgi.Entrypoint.upload))
prep_post = partial(prep_req, partial(cgi.prep_post, cgi.Entrypoint.upload))


def _str_encode_time(encoded_time: int):
    return "{0:#0{1}x}".format(encoded_time, 10)


def _encode_time(mtime: float):
    """Encode a mtime float as a 32-bit FAT time"""
    dt = arrow.get(mtime)
    dt = dt.to("local")
    date_val = ((dt.year - 1980) << 9) | (dt.month << 5) | dt.day
    secs = dt.second + dt.microsecond / 10**6
    time_val = (dt.hour << 11) | (dt.minute << 5) | math.floor(secs / 2)
    return (date_val << 16) | time_val


class UploadError(RequestException):
    def __init__(self, msg, response):
        self.msg = msg
        self.response = response

    def __str__(self):
        return "{}: {}".format(self.msg, self.response)

    __repr__ = __str__

