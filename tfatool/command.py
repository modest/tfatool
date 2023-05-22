import logging
import arrow

from pathlib import PurePosixPath
from collections import namedtuple
from . import cgi
from .info import DEFAULT_REMOTE_DIR
from .info import WifiMode, WifiModeOnBoot, ModeValue, Operation
from .info import FileInfo, RawFileInfo
from .connection import DEFAULT_CONNECTION


logger = logging.getLogger(__name__)

##################
# command.cgi API


def map_files(*filters, remote_dir=DEFAULT_REMOTE_DIR, connection=DEFAULT_CONNECTION):
    files = list_files(*filters, remote_dir=remote_dir, connection=connection)
    return {f.filename: f for f in files}


def list_files(*filters, remote_dir=DEFAULT_REMOTE_DIR, connection=DEFAULT_CONNECTION):
    response = _get(Operation.list_files, connection=connection, DIR=remote_dir)
    files = _split_file_list(response.text)
    return (f for f in files if all(filt(f) for filt in filters))


def map_files_raw(*filters, remote_dir=DEFAULT_REMOTE_DIR, connection=DEFAULT_CONNECTION):
    files = list_files_raw(*filters, remote_dir=remote_dir, connection=connection)
    return {f.filename: f for f in files}


def list_files_raw(*filters, remote_dir=DEFAULT_REMOTE_DIR, connection=DEFAULT_CONNECTION):
    response = _get(Operation.list_files, connection=connection, DIR=remote_dir)
    files = _split_file_list_raw(response.text)
    return (f for f in files if all(filt(f) for filt in filters))


def count_files(remote_dir=DEFAULT_REMOTE_DIR, connection=DEFAULT_CONNECTION):
    response = _get(Operation.count_files, connection=connection, DIR=remote_dir)
    return int(response.text)


def memory_changed(connection=DEFAULT_CONNECTION):
    """Returns True if memory has been written to, False otherwise"""
    response = _get(Operation.memory_changed, connection=connection)
    try:
        return int(response.text) == 1
    except ValueError:
        raise IOError("Likely no FlashAir connection, "
                      "memory changed CGI command failed")


def get_ssid(connection=DEFAULT_CONNECTION):
    return _get(Operation.get_ssid, connection=connection).text


def get_password(connection=DEFAULT_CONNECTION):
    return _get(Operation.get_password, connection=connection).text


def get_mac(connection=DEFAULT_CONNECTION):
    return _get(Operation.get_mac, connection=connection).text


def get_browser_lang(connection=DEFAULT_CONNECTION):
    return _get(Operation.get_browser_lang, connection=connection).text


def get_fw_version(connection=DEFAULT_CONNECTION):
    return _get(Operation.get_fw_version, connection=connection).text


def get_ctrl_image(connection=DEFAULT_CONNECTION):
    return _get(Operation.get_ctrl_image, connection=connection).text


def get_wifi_mode(connection=DEFAULT_CONNECTION) -> WifiMode:
    mode_value = int(_get(Operation.get_wifi_mode, connection=connection).text)
    all_modes = list(WifiMode) + list(WifiModeOnBoot)
    for mode in all_modes:
        if mode.value == mode_value:
            return mode
    raise ValueError("Uknown mode: {:d}".format(mode_value))


#####################
# API implementation

def _split_file_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            directory, filename, *remaining = groups
            remaining = map(int, remaining)
            size, attr_val, date_val, time_val = remaining
            timeinfo = _decode_time(date_val, time_val)
            attribute = _decode_attribute(attr_val)
            path = str(PurePosixPath(directory, filename))
            yield FileInfo(directory, filename, path,
                           size, attribute, timeinfo)


def _split_file_list_raw(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            directory, filename, size, *_ = groups
            path = str(PurePosixPath(directory, filename))
            yield RawFileInfo(directory, filename, path, int(size))


def _decode_time(date_val: int, time_val: int):
    year = (date_val >> 9) + 1980  # 0-val is the year 1980
    month = (date_val & (0b1111 << 5)) >> 5
    day = date_val & 0b11111
    hour = time_val >> 11
    minute = ((time_val >> 5) & 0b111111)
    second = (time_val & 0b11111) * 2
    try:
        decoded = arrow.get(year, month, day, hour,
                            minute, second, tzinfo="local")
    except ValueError:
        year = max(1980, year)  # FAT32 doesn't go higher
        month = min(max(1, month), 12)
        day = max(1, day)
        decoded = arrow.get(year, month, day, hour, minute, second)
    return decoded


AttrInfo = namedtuple(
    "AttrInfo", "archive directly volume system_file hidden_file read_only")

def _decode_attribute(attr_val: int):
    bit_positions = reversed(range(6))
    bit_flags = [bool(attr_val & (1 << bit)) for bit in bit_positions]
    return AttrInfo(*bit_flags)


########################################
# command.cgi request prepping, sending

def _get(operation: Operation, connection=DEFAULT_CONNECTION, **params):
    """HTTP GET of the FlashAir command.cgi entrypoint"""
    prepped_request = _prep_get(operation, connection, **params)
    return cgi.send(prepped_request)


def _prep_get(operation: Operation, connection=DEFAULT_CONNECTION, **params):
    params.update(op=int(operation))  # op param required
    return cgi.prep_get(cgi.Entrypoint.command, connection, **params)

