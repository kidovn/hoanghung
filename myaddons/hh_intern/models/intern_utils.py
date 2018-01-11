# -*- coding: utf-8 -*-
import unicodedata
import re

def no_accent_vietnamese(s):
    # text = s.decode('utf-8')
    text = re.sub(u'Đ', 'D', s)
    text = re.sub(u'đ', 'd', text)
    return unicodedata.normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')

def date_time_in_jp(day = None,month = None, year = None):
    if day is None:
        if month is None:
            return u'%s年'%year
        else:
            return u'%s年%s月'%(year,month)
    else:
        return u'%s年%s月%s日'%(year,month,day)


def no_accent_vietnamese2(s):
    # s = s.decode('utf-8')
    text = re.sub(u'Đ', 'XX', s)
    text = re.sub(u'đ', 'XX', text)
    # return s.encode('utf-8')
    return unicodedata.normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')

def fix_accent_2(s):
    return s.replace('XX','Đ')

def name_with_underscore(s):
    temp = no_accent_vietnamese(s)
    return temp.replace(" ","_")