# (c) 2005 Clark C. Evans and contributors
# This module is part of the Python Paste Project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
# Some of this code was funded by: http://prometheusresearch.com
"""
Date, Time, and Timespan Parsing Utilities

This module contains parsing support to create "human friendly"
``datetime`` object parsing.  The explicit goal of these routines is
to provide a multi-format date/time support not unlike that found in
Microsoft Excel.  In most approaches, the input is very "strict" to
prevent errors -- however, this approach is much more liberal since we
are assuming the user-interface is parroting back the normalized value
and thus the user has immediate feedback if the data is not typed in
correctly.

  ``parse_date`` and ``normalize_date``

     These functions take a value like '9 jan 2007' and returns either an
     ``date`` object, or an ISO 8601 formatted date value such
     as '2007-01-09'.  There is an option to provide an Oracle database
     style output as well, ``09 JAN 2007``, but this is not the default.

     This module always treats '/' delimiters as using US date order
     (since the author's clients are US based), hence '1/9/2007' is
     January 9th.  Since this module treats the '-' as following
     European order this supports both modes of data-entry; together
     with immediate parroting back the result to the screen, the author
     has found this approach to work well in pratice.

  ``parse_time`` and ``normalize_time``

     These functions take a value like '1 pm' and returns either an
     ``time`` object, or an ISO 8601 formatted 24h clock time
     such as '13:00'.  There is an option to provide for US style time
     values, '1:00 PM', however this is not the default.

  ``parse_datetime`` and ``normalize_datetime``

     These functions take a value like '9 jan 2007 at 1 pm' and returns
     either an ``datetime`` object, or an ISO 8601 formatted
     return (without the T) such as '2007-01-09 13:00'. There is an
     option to provide for Oracle / US style, '09 JAN 2007 @ 1:00 PM',
     however this is not the default.

  ``parse_delta`` and ``normalize_delta``

     These functions take a value like '1h 15m' and returns either an
     ``timedelta`` object, or an 2-decimal fixed-point
     numerical value in hours, such as '1.25'.  The rationale is to
     support meeting or time-billing lengths, not to be an accurate
     representation in mili-seconds.  As such not all valid
     ``timedelta`` values will have a normalized representation.

"""
from datetime import timedelta, time, date, datetime
from time import localtime
import string

__all__ = ['parse_timedelta', 'normalize_timedelta',
           'parse_time', 'normalize_time',
           'parse_date', 'normalize_date']

def _number(val):
    try:
        return string.atoi(val)
    except:
        return None

#
# timedelta
#
def parse_timedelta(val):
    """
    returns a ``timedelta`` object, or None
    """
    if not val:
        return None
    val = string.lower(val)
    if "." in val:
        val = float(val)
        return timedelta(hours=int(val), minutes=60*(val % 1.0))
    fHour = ("h" in val or ":" in val)
    fMin  = ("m" in val or ":" in val)
    fFraction = "." in val
    for noise in "minu:teshour()":
        val = string.replace(val,noise,' ')
    val = string.strip(val)
    val = string.split(val)
    hr = 0.0
    mi = 0
    val.reverse()
    if fHour: hr = int(val.pop())
    if fMin:  mi = int(val.pop())
    if len(val) > 0 and not hr:
        hr = int(val.pop())
    return timedelta(hours=hr, minutes=mi)

def normalize_timedelta(val):
    """
    produces a normalized string value of the timedelta

    This module returns a normalized time span value consisting of the
    number of hours in fractional form. For example '1h 15min' is
    formatted as 01.25.
    """
    if type(val) == str:
        val = parse_timedelta(val)
    if not val:
        return ''
    hr = val.seconds/3600
    mn = (val.seconds % 3600)/60
    return "%02d.%02d" % (hr,mn*100/60)

#
# time
#
def parse_time(val):
    if not val:
        return None
    hr = mi = 0
    val = string.lower(val)
    amflag = (-1 != string.find(val,'a'))  # set if AM is found
    pmflag = (-1 != string.find(val,'p'))  # set if PM is found
    for noise in ":amp.":
        val = string.replace(val,noise,' ')
    val = string.split(val)
    if len(val) > 1:
        hr = int(val[0])
        mi = int(val[1])
    else:
        val = val[0]
        if len(val) < 1:
            pass
        elif 'now' == val:
            tm = localtime()
            hr = tm[3]
            mi = tm[4]
        elif 'noon' == val:
            hr = 12
        elif len(val) < 3:
            hr = int(val)
            if not amflag and not pmflag and hr < 7:
                hr += 12
        elif len(val) < 5:
            hr = int(val[:-2])
            mi = int(val[-2:])
        else:
            hr = int(val[:1])
    if amflag  and hr >= 12: hr = hr - 12
    if pmflag  and hr < 12 : hr = hr + 12
    return time(hr,mi)

def normalize_time(value, ampm):
    if not value:
        return ''
    if type(value) == str:
        value = parse_time(value)
    if not ampm:
        return "%02d:%02d" % (value.hour, value.minute)
    hr = value.hour
    am = "AM"
    if hr < 1 or hr > 23:
        hr = 12
    elif hr >= 12:
        am = "PM"
        if hr > 12:
            hr = hr - 12
    return "%02d:%02d %s" % (hr,value.minute,am)

#
# Date Processing
#

_one_day = timedelta(days=1)

_str2num = { 'jan':1, 'feb':2, 'mar':3, 'apr':4,  'may':5, 'jun':6,
            'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12 }
def _month(val):
    for (key,mon) in _str2num.items():
        if key in val:
            return mon
    return None

_days_in_month = {1:31,2:28,3:31,4:30,5:31,6:30,
                 7:31,8:31,9:30,10:31,11:30,12:31 }
num2str = { 1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
            7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec' }
wkdy = ("mon","tue","wed","thu","fri","sat","sun" )

def _date(val):
    if not(val):
        return None
    dy = None
    yr = None
    mo = None
    # regular expressions would be good here...
    val = string.lower(val)
    chk = val[:3]
    now = None
    strict = val.split("-")
    if len(strict) == 3:
        (y,m,d) = strict
        if "+" in d:
            d = d.split("+")[0]
        if " " in d:
            d = d.split(" ")[0]
        now = date(int(y),int(m),int(d))
        val = "xxx" + val[10:]
    if not now and 'now' == chk:
        now = date.today()
    if not now and chk in wkdy:
        now = date.today()
        idx = list(wkdy).index(chk)
        while now.day_of_week != idx:
            now += _one_day
    if now:
        tail = val[3:].strip()
        tail = tail.replace("+"," +").replace("-"," -")
        for item in tail.split():
            try:
                days = int(item)
            except ValueError:
                pass
            else:
                now += timedelta(days=days)
        return (now.year,now.month,now.day,0, 0, 0, 0, 0, 0)
    #
    for noise in ('/','-',',','*'):
        val = string.replace(val,noise,' ')
    for noise in wkdy:
        val = string.replace(val,noise,' ')
    out = []
    last = False
    ldig = False
    for ch in val:
        if ch.isdigit():
            if last and not ldig:
               out.append(' ')
            last = ldig = True
        else:
            if ldig:
                out.append(' ')
                ldig = False
            last = True
        out.append(ch)
    val = string.split("".join(out))
    if 3 == len(val):
        a = _number(val[0])
        b = _number(val[1])
        c = _number(val[2])
        if len(val[0]) == 4:
            yr = a
            if b:  # 1999 6 23
                mo = b
                dy = c
            else:  # 1999 Jun 23
                mo = _month(val[1])
                dy = c
        elif a > 0:
            yr = c
            if len(val[2]) < 4:
                raise TypeError("four digit year required")
            if b: # 6 23 1999
                dy = b
                mo = a
            else: # 23 Jun 1999
                dy = a
                mo = _month(val[1])
        else: # Jun 23, 2000
            dy = b
            yr = c
            if len(val[2]) < 4:
                raise TypeError("four digit year required")
            mo = _month(val[0])
    elif 2 == len(val):
        a = _number(val[0])
        b = _number(val[1])
        if a > 999:
            yr = a
            dy = 1
            if b > 0: # 1999 6
                mo = b
            else: # 1999 Jun
                mo = _month(val[1])
        elif a > 0:
            if b > 999: # 6 1999
                mo = a
                yr = b
                dy = 1
            elif b > 0: # 6 23
                mo = a
                dy = b
            else: # 23 Jun
                dy = a
                mo = _month(val[1])
        else:
            if b > 999: # Jun 2001
                yr = b
                dy = 1
            else:  # Jun 23
                dy = b
            mo = _month(val[0])
    elif 1 == len(val):
        val = val[0]
        if not val.isdigit():
            mo = _month(val)
            if mo is not None:
                dy = 1
        else:
            v = _number(val)
            val = str(v)
            if 8 == len(val): # 20010623
                yr = _number(val[:4])
                mo = _number(val[4:6])
                dy = _number(val[6:])
            elif len(val) in (3,4):
                if v > 1300: # 2004
                    yr = v
                    mo = 1
                    dy = 1
                else:        # 1202
                    mo = _number(val[:-2])
                    dy = _number(val[-2:])
            elif v < 32:
                dy = v
            else:
                raise TypeError("four digit year required")
    tm = localtime()
    if mo is None: mo = tm[1]
    if dy is None: dy = tm[2]
    if yr is None: yr = tm[0]
    if mo > 12 or mo < 1: mo = 1
    if dy < 1: dy = 1
    max = _days_in_month[mo]
    if 2 == mo:
        if not(yr%400) or ( not(yr%4) and yr%100 ):
            max = 29
        else:
            max = 28
    if dy > max:
        raise TypeError("day too large for %s %s: '%s'" % \
               (num2str[mo], yr, dy))
    return (yr,mo,dy)

def _format_date(val, iso8601=True):
    if iso8601:
        return "%4d-%02d-%02d" % (val[0],val[1],val[2])
    return "%02d %s %4d" % (val[2],num2str[val[1]],val[0])

def parse_date(val, iso8601=True):
    if not val:
        return None
    (yr,mo,dy) = _date(val)
    return date(yr,mo,dy)

def normalize_date(val, iso8601=True):
    if not val:
        return ''
    return _format_date(_date(val),iso8601)


