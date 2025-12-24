import os
import re
from unicodedata import normalize
from werkzeug.datastructures import FileStorage

def secure_filename(filename):
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                            'LPT2', 'LPT3', 'PRN', 'NUL')
    if isinstance(filename, FileStorage):
        filename = filename.filename
    filename = normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(filename.split()))).strip('._')
    if os.name == 'nt' and filename and filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename
    return filename