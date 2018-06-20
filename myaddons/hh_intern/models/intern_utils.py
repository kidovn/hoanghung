# -*- coding: utf-8 -*-
import unicodedata
import re
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

ranges = [
  {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},         # compatibility ideographs
  {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},         # compatibility ideographs
  {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},         # compatibility ideographs
  # {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")}, # compatibility ideographs
  {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},         # Japanese Kana
  {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},         # cjk radicals supplement
  {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
  {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
  # {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
  # {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
  # {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
  # {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
]

def no_accent_vietnamese(s):
    # text = s.decode('utf-8')
    if check_han_language(s):
        return s
    text = re.sub(u'Đ', 'D', s)
    text = re.sub(u'đ', 'd', text)
    return unicodedata.normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')


def is_cjk(char):
    return any([range["from"] <= ord(char) <= range["to"] for range in ranges])

def check_han_language(s):
    i = 0
    while i < len(s):
        if is_cjk(s[i]):
            return True
        i += 1
    return False

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

def date_time_in_vn_lower(day = None,month = None, year = None):
    if not day:
        if not month:
            return u'năm %s'%year
        else:
            return u'tháng %s năm %s'%(month,year)
    else:
        return u'ngày %s tháng %s năm %s'%(day,month,year)

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

def get_age_jp(datecompare, day,month,year):
    if type(datecompare) is str:
        # _logger.info(datecompare)
        datecompare = datetime.strptime('%s'%datecompare,'%Y-%m-%d')
    if datecompare:
        tmp = datecompare.year - int(year)
        if datecompare.month == int(month):
            if datecompare.day < int(day):
                tmp = tmp-1
        elif datecompare.month < int(month):
            tmp = tmp-1
        return tmp
    return 0

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

def convert_to_docx_string(s):
    if s:
        s = s.replace(u'&',u'&amp;')
        return s
    else:
        return ""


