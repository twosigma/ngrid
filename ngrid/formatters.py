"""
Formatters for rendering values as strings.
"""

#-------------------------------------------------------------------------------

import datetime
import math

from   pytz import UTC

from   . import text
from   .datetime import ensure_datetime

#-------------------------------------------------------------------------------

class BoolFormatter:

    def __init__(self, true='True', false='False', size=None, pad_left=False):
        if size is None:
            size = max(len(true), len(false))

        self.__true     = true
        self.__false    = false
        self.__size     = size
        self.__pad_left = pad_left


    @property
    def width(self):
        """
        The width of a formatted value.
        """
        return self.__size


    @property
    def size(self):
        return self.__size


    @property
    def pad_left(self):
        return self.__pad_left


    def changing(self, **kw_args):
        args = dict(
            size    =self.__size,
            pad_left=self.__pad_left,
            )
        args.update(kw_args)
        return self.__class__(self.__true, self.__false, **args)


    def format(self, value):
        """
        Formats a value.

        @type value
          `float`
        """
        return text.palide(
            self.__true if value else self.__false, self.__size,
            ellipsis="",
            pad     =" ",
            position=1.0,
            left    =self.__pad_left)


    __call__ = format



#-------------------------------------------------------------------------------

class IntFormatter:

    def __init__(self, size, pad=" ", sign="-"):
        """
        @param size
          The number of digits.
        @param pad
          Pad character for the integral part.  May be " " or "0".
        @param sign
          "-" for negative sign only, "+" for both.  If `None`, don't show
          a sign; only nonnegative numbers may be formatted.
        """
        assert size >= 0
        assert pad in "0 "
        assert sign in (None, "-", "+")
          
        width = size
        if sign in ("-", "+"):
            width += 1

        self.__size         = size
        self.__pad          = pad
        self.__sign         = sign
        self.__width        = width


    @property
    def size(self):
        return self.__size


    @property
    def pad(self):
        return self.__pad


    @property
    def sign(self):
        return self.__sign


    @property
    def width(self):
        """
        The width of a formatted value.
        """
        return self.__width


    def changing(self, **kw_args):
        args = dict(
            size        =self.__size,
            pad         =self.__pad,
            sign        =self.__sign)
        args.update(kw_args)
        return self.__class__(**args)


    def format(self, value):
        """
        Formats a value.

        @type value
          `int`
        """
        sign = (
            "" if self.__sign is None
            else "-" if value < 0
            else "+" if self.__sign == "+"
            else " ")

        result = str(abs(value))
        if len(result) > self.__size or value < 0 and self.__sign is None:
            # Doesn't fit.
            return "#" * self.__width
        if self.__pad == " ":
            # Space padding precedes the sign.
            result = text.pad(
                sign + result,
                self.__size + len(sign), pad=self.__pad, left=True)
        else:
            # The sign must precede zero padding.
            result = sign + text.pad(
                result, self.__size, pad=self.__pad, left=True)

        return result


    def __call__(self, value):
        """
        Converts a value to an int and formats it.
        """
        try:
            value = round(value)
        except TypeError:
            pass
        return self.format(int(value))



#-------------------------------------------------------------------------------

class FloatFormatter:

    def __init__(self, size, precision, pad=" ", sign="-", point=".",
                 nan_str="NaN", inf_str="Inf"):
        """
        @param size
          The number of digits for the integral part.
        @param precision
          The number of digits for the fractional part, or `None` to suppress
          the decimal point.
        @param pad
          Pad character for the integral part.  May be " " or "0".
        @param sign
          "-" for negative sign only, "+" for both.  If `None`, don't show
          a sign; only nonnegative numbers may be formatted.
        @param point
          The decimal point character.
        """
        assert size >= 0
        assert precision is None or precision >= 0
        assert pad in "0 "
        assert sign in (None, "-", "+")

        width = size
        if precision is not None:
            width += len(point) + precision
        assert len(nan_str) <= width
        assert len(inf_str) <= width
        if sign in ("-", "+"):
            width += 1

        self.__size         = size
        self.__precision    = precision
        self.__pad          = pad
        self.__sign         = sign
        self.__point        = point
        self.__nan_str      = nan_str
        self.__inf_str      = inf_str

        self.__multiplier   = None if precision is None else 10 ** precision
        self.__width        = width


    @property
    def size(self):
        return self.__size


    @property
    def precision(self):
        return self.__precision


    @property
    def pad(self):
        return self.__pad


    @property
    def sign(self):
        return self.__sign


    @property
    def point(self):
        return self.__point


    @property
    def nan_str(self):
        return self.__nan_str


    @property
    def inf_str(self):
        return self.__inf_str


    @property
    def width(self):
        """
        The width of a formatted value.
        """
        return self.__width


    def changing(self, **kw_args):
        args = dict(
            size        =self.__size,
            precision   =self.__precision,
            pad         =self.__pad,
            sign        =self.__sign,
            point       =self.__point,
            nan_str     =self.__nan_str,
            inf_str     =self.__inf_str)
        args.update(kw_args)
        return self.__class__(**args)


    def format(self, value):
        """
        Formats a value.

        @type value
          `float`
        """
        sign = (
            "" if self.__sign is None
            else "-" if value < 0
            else "+" if self.__sign == "+"
            else " ")

        if math.isnan(value):
            # Not a number.
            result = text.pad(self.__nan_str, self.__width, pad=" ", left=True)

        elif math.isinf(value):
            # Infinite value.
            if value < 0 and self.__sign is None:
                return "#" * self.__width
            else:
                result = text.pad(
                    sign + self.__inf_str, self.__width, pad=" ", left=True)

        else:
            # "Normal" number.
            precision = 0 if self.__precision is None else self.__precision
            rnd_value = round(value, precision)
            abs_value = abs(rnd_value)
            int_value = int(abs_value)
            result = str(int_value)
            if len(result) > self.__size or self.__sign is None and value < 0:
                # Doesn't fit.
                return "#" * self.__width

            if self.__pad == " ":
                # Space padding precedes the sign.
                result = text.pad(
                    sign + result,
                    self.__size + len(sign), pad=self.__pad, left=True)
            else:
                # The sign must precede zero padding.
                result = sign + text.pad(
                    result, self.__size, pad=self.__pad, left=True)

            if self.__precision is None:
                pass
            elif self.__precision == 0:
                result += self.__point
            else:
                frac = int(round((abs_value - int_value) * self.__multiplier))
                frac = str(frac)
                assert len(frac) <= precision
                frac = text.pad(frac, self.__precision, pad="0", left=True)
                result += self.__point + frac
        return result


    def __call__(self, value):
        """
        Converts a value to a float and formats it.
        """
        return self.format(float(value))



#-------------------------------------------------------------------------------

class ScientificFloatFormatter:

    def __init__(self, size, precision, pad=" ", sign="-", point=".",
                 exp="E", nan_str="NaN", inf_str="Inf"):
        """
        @param size
          The number of digits for the exponent.
        @param precision
          The number of digits for the fractional part, or `None` to suppress
          the decimal point.
        @param pad
          Pad character for the integral part.
        @param sign
          "-" for negative sign only, "+" for both, `None` for none.
        @param point
          The decimal point character.
        """
        assert size >= 0
        assert precision is None or precision >= 0
        assert len(pad) == 1
        assert sign in (None, "-", "+")

        width = 1 + len(point) + precision + len(exp) + 1 + size
        nan_str = text.pad(nan_str.strip()[: width], width)
        inf_str = text.pad(inf_str.strip()[: width], width)
        if sign in ("-", "+"):
            width += 1

        self.__size         = size
        self.__precision    = precision
        self.__pad          = pad
        self.__sign         = sign
        self.__point        = point
        self.__exp          = exp
        self.__nan_str      = nan_str
        self.__inf_str      = inf_str

        self.__multiplier   = None if precision is None else 10 ** precision
        self.__width        = width


    @property
    def size(self):
        return self.__size


    @property
    def precision(self):
        return self.__precision


    @property
    def pad(self):
        return self.__pad


    @property
    def sign(self):
        return self.__sign


    @property
    def point(self):
        return self.__point


    @property
    def exp(self):
        return self.__exp


    @property
    def nan_str(self):
        return self.__nan_str


    @property
    def inf_str(self):
        return self.__inf_str


    @property
    def width(self):
        """
        The width of a formatted value.
        """
        return self.__width


    def changing(self, **kw_args):
        args = dict(
            precision   =self.__precision,
            size        =self.__size,
            pad         =self.__pad,
            sign        =self.__sign,
            point       =self.__point,
            exp         =self.__exp,
            nan_str     =self.__nan_str,
            inf_str     =self.__inf_str)
        args.update(kw_args)
        return self.__class__(**args)


    def format(self, value):
        """
        Formats a value.

        @type value
          `float`
        """
        def add_sign(result):
            if self.__sign == "-":
                return ("-" if value < 0 else " ") + result
            elif self.__sign == "+":
                return ("-" if value < 0 else "+") + result
            else:
                return result

        if math.isnan(value):
            result = add_sign(self.__nan_str)
        elif math.isinf(value):
            result = add_sign(self.__inf_str)
        else:
            abs_value = abs(value)
            rnd_value = round(
                abs_value, 
                int(math.ceil(self.__precision - math.log10(abs_value))))
            exp = int(math.floor(math.log10(rnd_value)))
            mantissa = rnd_value / 10 ** exp
            int_value = int(mantissa)
            result = add_sign(str(int_value))
            if self.__precision is None:
                pass
            elif self.__precision == 0:
                result += self.__point
            else:
                frac = int(round((mantissa - int_value) * 10 ** self.__precision))
                frac = text.pad(str(frac), self.__precision, pad="0", left=True)
                result += self.__point + frac
            result += self.__exp
            result += "+" if exp >= 0 else "-"
            exp = text.pad(str(abs(exp)), self.__size, pad="0", left=True)
            if len(exp) > self.__size:
                # Doesn't fit.
                result += "#" * self.__size
            else:
                result += exp
        return result


    def __call__(self, value):
        """
        Converts a value to a float and formats it.
        """
        return self.format(float(value))



#-------------------------------------------------------------------------------

class StrFormatter:

    def __init__(self, size, ellipsis="...", pad=" ", position=1.0, 
                 pad_left=False):
        self.__size     = size
        self.__ellipsis = ellipsis
        self.__pad      = pad
        self.__position = position
        self.__pad_left = pad_left


    @property
    def size(self):
        return self.__size


    @property
    def ellipsis(self):
        return self.__ellipsis


    @property
    def pad(self):
        return self.__pad


    @property
    def position(self):
        return self.__position


    @property
    def pad_left(self):
        return self.__pad_left


    @property
    def width(self):
        """
        The width of a formatted value.
        """
        return self.__size


    def changing(self, **kw_args):
        args = dict(
            size        =self.__size,
            ellipsis    =self.__ellipsis,
            pad         =self.__pad,
            position    =self.__position,
            pad_left    =self.__pad_left)
        args.update(kw_args)
        return self.__class__(**args)


    def format(self, value):
        """
        Formats a value.

        @type value
          `str`.
        """
        return text.palide(
            str(value), self.__size, 
            ellipsis=self.__ellipsis[: self.__size], 
            pad     =self.__pad,
            position=self.__position, 
            left    =self.__pad_left)


    def __call__(self, value):
        """
        Converts a value to a string and formats it.
        """
        return self.format(str(value))



#-------------------------------------------------------------------------------

DATETIME_FORMATS = {
    "simple"            : "%Y-%m-%d %H:%M:%S",
    "ISO 8601 extended" : "%Y-%m-%dT%H:%M:%SZ",
    "ISO 8601"          : "%Y%m%dT%H%M%SZ",
    }

class DatetimeFormatter:

    def __init__(self, spec="ISO 8601 extended"):
        """
        @param spec
          A `strftime`-style format specification or name in `DATETIME_FORMATS`.
        """
        dt = datetime.datetime(2014, 9, 17, 10, 7, 53, 123456, UTC)
        spec = DATETIME_FORMATS.get(spec, spec)
        width = len(format(dt, spec))

        self.__spec = spec
        self.__width = width


    @property
    def width(self):
        """
        The width of a formatted value.
        """
        return self.__width


    def format(self, value):
        """
        Formats a value.

        @type value
          UTC `datetime`.
        """
        result = format(value, self.__spec)
        return result
        

    def __call__(self, value):
        """
        Converts a value to a UTC `datetime` and formats it.
        """
        return self.format(ensure_datetime(value))



