"""
Date and time tools.
"""

#-------------------------------------------------------------------------------

import datetime
import re

import pytz
from   pytz import UTC

from   .util import if_none

#-------------------------------------------------------------------------------

def ensure_date(date):
    """
    Attempts to convert an object to a date.

    Accepts the following:
    - A `date` instance.
    - A `datetime` instance, as long as the time zone is set.
    - A YYYYMMDD `int`.
    - A YYYYMMDD `str`.
    - A YYYY-MM-DD `str`.
    - `"local-today"`, for today in the host's local time zone.
    - `"utc-today"`, for today in UTC.

    @rtype
      `datetime.date`
    """
    if isinstance(date, datetime.datetime):
        if date.tzinfo is None:
            # No matter what the datetime module may say, a datetime without a
            # timezone is not a date, nor does it specify one.
            raise TypeError(
                "can't convert datetime to date without a time zone")
        else:
            return date.date()
    if isinstance(date, datetime.date):
        return date

    if isinstance(date, int) and 18000000 <= date <= 30000000:
        # Assume it's YYYYMMDD-encoded.
        return datetime.date(date // 10000, (date % 10000) // 100, date % 100)

    if date == "local-today":
        return datetime.date.today()
    if date == "utc-today":
        return datetime.datetime.utcnow().date()

    def from_ymd(y, m, d):
        try:
            return datetime.date(y, m, d)
        except ValueError:
            raise TypeError("not a date: {!r}".format(date))

    if isinstance(date, str):
        match = re.match(r"([12]\d\d\d)([01]\d)([0-3]\d)$", date)
        if match is None:
            match = re.match(r"([12]\d\d\d)-([01]?\d)-([0-3]?\d)$", date)
        if match is not None:
            # It's "YYYYMMDD"-encoded.
            return from_ymd(*[ int(g) for g in match.groups() ])

    raise TypeError("not a date: {!r}".format(date))
        

def ensure_time(time):
    """
    Attempts to convert an object to a time (of day).

    @rtype
      `datetime.time`
    """
    if isinstance(time, datetime.datetime):
        return date.time()
    if isinstance(time, datetime.time):
        return time

    if time == "local-now":
        return datetime.datetime.now().time()
    if time == "utc-now":
        return datetime.datetime.utcnow().time()

    def from_parts(h, m, s=0):
        try:
            return datetime.time(h, m, s)
        except ValueError:
            raise TypeError("not a time: {!r}".format(time))

    if isinstance(time, str):
        match = re.match(r"(\d?\d):(\d\d):(\d\d)", time)
        if match is None:
            match = re.match(r"(\d?\d):(\d\d)", time)
        if match is not None:
            return from_parts(*[ int(g) for g in match.groups() ])

    raise TypeError("not a time: {!r}".format(time))


_DATETIME_REGEXES = [ 
    re.compile(r)
    for r in (
        r"(?P<ye>[12]\d\d\d)-(?P<mo>[01]?\d)-(?P<da>[0-3]?\d) (?P<ho>[0-2]?\d):(?P<mi>[0-5]\d):(?P<se>\d\d)?$",
        r"(?P<ye>[12]\d\d\d)-(?P<mo>[01]?\d)-(?P<da>[0-3]\d)T(?P<ho>[0-2]?\d):(?P<mi>[0-5]\d):(?P<se>\d\d)?Z$",
        )
    ]


def ensure_datetime(dt):
    """
    Attempts to convert an object to a UTC datetime.

    Accepts the following:
    - A `datetime` instance.
    - A `numpy.datetime64` instance.
    - `"now"`, for the current datetime.
    - A "YYYY-MM-DD HH:MM:SS" string, assumed to be UTC.
    - A "YYYY-MM-DDTHH:MM:SSZ" ISO 8601 string.
    """
    if isinstance(dt, datetime.datetime):
        return dt

    # Check for numpy.datetime64.  We just try to convert it like this to avoid
    # importing numpy, if it hasn't been yet.
    try:
        item = dt.item()
    except:
        pass
    else:
        if isinstance(item, datetime.datetime):
            return item.replace(tzinfo=UTC)

    if dt == "now":
        return datetime.datetime.utcnow().replace(tzinfo=UTC)
        
    def from_parts(ye, mo, da, ho=0, mi=0, se=0):
        try:
            return datetime.datetime(ye, mo, da, ho, mi, se, tzinfo=UTC)
        except ValueError:
            raise TypeError("not a datetime: {!r}".format(dt))

    if isinstance(dt, str):
        for regex in _DATETIME_REGEXES:
            match = regex.match(dt)
            if match is not None:
                ye = int(match.group("ye"))
                mo = int(match.group("mo"))
                da = int(match.group("da"))
                ho = int(if_none(match.group("ho"), 0))
                mi = int(if_none(match.group("mi"), 0))
                se = int(if_none(match.group("se"), 0))
                return from_parts(ye, mo, da, ho, mi, se)

    raise TypeError("not a datetime: {!r}".format(dt))


def ensure_timedelta(delta):
    """
    Attempts to convert an object to a time delta.

    @rtype
      `datetime.timedelta`
    """
    if isinstance(delta, datetime.timedelta):
        return delta

    if isinstance(delta, str):
        # FIXME
        match = re.match(r"(\d+) *(d|h|m|s)", delta)
        if match is not None:
            num, unit = match.groups()
            if unit == "d":
                return datetime.timedelta(int(num), 0)
            else:
                secs = int(num) * {"h": 3600, "m": 60, "s": 1}.get(unit)
                return datetime.timedelta(0, secs)

    raise TypeError("not a timedelta: {!r}".format(delta))


def ensure_tz(tz):
    """
    Attempts to convert an object to a time zone.

    @rtype
      `datetime.tzinfo`
    """
    if isinstance(tz, datetime.tzinfo):
        return tz

    if tz is None:
        return UTC

    if isinstance(tz, str):
        try:
            return pytz.timezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError("not a time zone: {}".format(tz))

    raise TypeError("not a time zone: {!r}".format(tz))


