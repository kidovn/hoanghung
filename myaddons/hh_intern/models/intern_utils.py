# -*- coding: utf-8 -*-
import unicodedata
import re
from datetime import datetime

def no_accent_vietnamese(s):
    # text = s.decode('utf-8')
    text = re.sub(u'Đ', 'D', s)
    text = re.sub(u'đ', 'd', text)
    return unicodedata.normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')

def date_time_in_jp(day = None,month = None, year = None):
    if not day:
        if not month:
            return u'%s年'%year
        else:
            return u'%s年%s月'%(year,month)
    else:
        return u'%s年%s月%s日'%(year,month,day)

def date_time_in_jp_missing(day ,month , year ):
    if not day:
        day = '...'
    if not month:
        month = '...'
    return u'%s年%s月%s日'%(year,month,day)

def date_time_in_vn(day = None,month = None, year = None):
    if not day:
        if not month:
            return u'Năm %s'%year
        else:
            return u'Tháng %s năm %s'%(month,year)
    else:
        return u'Ngày %s tháng %s năm %s'%(day,month,year)
def date_time_in_vn2(month,year):
    return u'Tháng %s/%s' % (month, year)

def date_time_in_en(day,month,year):
    return u'%s/%s/%s'%(day,month,year)

def date_time_in_en_missing(day,month,year):
    if not day:
        day = '...'
    if not month:
        month = '...'
    return u'%s/%s/%s'%(day,month,year)

def get_ages(year):
    return datetime.now().year - int(year)

def get_age_jp(day,month,year):
    tmp = datetime.now().year - int(year)
    if datetime.now().month == int(month):
        if datetime.now().day < int(day):
            tmp = tmp-1
    elif datetime.now().month < int(month):
        tmp = tmp-1
    return tmp

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

def format_number_in_vn(s):
    str1 = ""
    s1 = [elm for elm in s]
    if len(s1) % 3 == 0:
        for i in range(0, len(s1) - 3, 3):
            str1 += s1[i] + s1[i + 1] + s1[i + 2] + "."
        str1 += s1[i] + s1[i + 1] + s1[i + 2]
    else:
        rem = len(s1) % 3
        for i in range(rem):
            str1 += s1[i]
        for i in range(rem, len(s1) - 1, 3):
            str1 += "." + s1[i] + s1[i + 1] + s1[i + 2]

    return str1

def convert_to_vn_phone(s):
    if s.startswith('0'):
        s = s[1:]
    if '+84' not in s:
        s = '+84'+s
    s = s.replace('(','').replace(')','')
    return s