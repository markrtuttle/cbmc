import os
import datetime

def date():
    return datetime.datetime.utcnow().isoformat()

def filedate(filename):
    ctime = os.path.getctime(filename)
    return datetime.datetime.utcfromtimestamp(ctime).isoformat()

def metadata(name, filename=None, root=None):
    meta = {'type': name, 'date': date()}
    if filename:
        meta['filename'] = filename
        meta['filedate'] = filedate(filename)
    if root:
        meta['root'] = root
    return meta
