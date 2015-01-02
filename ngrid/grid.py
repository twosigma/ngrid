"""
Interactive console tool for viewing tabular data.

Based on ngrid.py by smyang.
"""

#-------------------------------------------------------------------------------

from   __future__ import absolute_import, division

from   contextlib import closing
import csv
import curses
from   datetime import datetime
from   math import floor, ceil, log10, isnan, isinf
import os
import re
import sys

import numpy as np

from   . import text, formatters
from   .terminal import get_terminal_size

#-------------------------------------------------------------------------------

SAMPLELINES = 200
DELIMS = [',', ' ', '|', '\t']

QUOTE_CHAR = '"'

# Types, ordered from most specific to least specific.
TYPES = [bool, int, float, str]

HEADER = True

NAN = float("NaN")

SEPARATORS = [" ", "\u250a", "  ", "   ", " \u250a ", ]

DEFAULT_CFG = {
    "precision_min"     : "1",
    "precision_max"     : "6",
    "str_width_min"     : "4",
    "str_width_max"     : "32",
    "nan_string"        : "NaN",
    "inf_string"        : "\u221e",
    "ellipsis"          : "\u2026",
    "separator"         : " ",
    "show_header"       : "True",
    "show_footer"       : "True",
    "show_cursor"       : "False",
    }

#-------------------------------------------------------------------------------

def clip(min, val, max):
    """
    Returns `val` clipped to `min` and `max`.
    """
    return min if val < min else max if val > max else val


def as_bool(value):
    # FIXME: Guess more leniently?
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lower = value.lower()
        if lower == "true":
            return True
        elif lower == "false":
            return False
        else:
            raise ValueError("not a bool: {}".format(value))
    
    raise TypeError("not a bool: {}".format(value))


def as_float(value):
    if isinstance(value, float):
        return value
    if value == "":
        return NAN
    return float(value)


TYPE_CONVERTERS = {
    bool: as_bool,
    float: as_float,
    }
    

def guess_type(values):
    """
    Returns the most specific type that represents all values.

    @return
      The type and a convert function.
    """
    for type in TYPES:
        convert = TYPE_CONVERTERS.get(type, type)
        try:
            for value in values:
                convert(value)
        except (TypeError, ValueError):
            pass
        else:
            return type, convert
    raise RuntimeError("can't guess type")


def get_size(value):
    """
    Finds the number of digits required to represent the positive integer part.
    """
    if value == 0:
        return 1
    else:
        return max(int(floor(log10(abs(value)) + 1)), 1)


def get_default_formatter(type, values, cfg={}):
    """
    Chooses a default formatter based on type and values.

    @param values
      A sequence or `ndarray` of values.
    """
    values = np.array(values)

    if type is int:
        # Int types.
        size = get_size(abs(values).max())
        return formatters.IntFormatter(size)

    elif type is float:
        # Float types.
        vals = values[~(np.isnan(values) | np.isinf(values))]
        size = 1 if len(vals) == 0 else get_size(abs(vals).max())
        # Guess precision.  Try progressively higher precision until we find
        # one where rounding there won't leave any residuals larger than
        # we are willing to represent at all.
        precision_min = int(cfg["precision_min"])
        precision_max = int(cfg["precision_max"])
        tol = (10 ** -precision_max) / 2
        for precision in range(precision_min, precision_max + 1):
            if (abs(np.round(vals, precision) - vals) < tol).all():
                break
        return formatters.FloatFormatter(
            size, precision, 
            nan_str=cfg["nan_string"],
            inf_str=cfg["inf_string"])

    elif type is str:
        width = np.vectorize(len)(np.vectorize(str)(values)).max()
        str_width_min = int(cfg["str_width_min"])
        str_width_max = int(cfg["str_width_max"])
        width = clip(str_width_min, width, str_width_max)
        return formatters.StrFormatter(width, ellipsis=cfg["ellipsis"])

    elif type is bool:
        return formatters.BoolFormatter("T", "F")

    elif type is datetime:
        # FIXME: Use which datetime format by default?
        return formatters.DatetimeFormatter(formatters.DATETIME_FORMATS["TS"])

    else:
        raise NotImplementedError("type: {}".format(type))
        

def guess_delimiter(lines, delims=None):
    """
    Guesses the delimiter for lines of delimited data.

    @param delims
      Delimiters to try; if `None`, uses `DELIMS`.
    """
    delims = DELIMS if delims is None else delims

    def get_count(delim):
        # Read lines as delimited.
        rows = csv.reader(lines, delimiter=delim, quotechar='"')
        # Return the row length, as long as all are the same.
        count = len(next(rows))
        return count if all( len(r) == count for r in rows ) else 0

    # Get the row length for all delimiters.
    counts = [ (get_count(d), d) for d in delims ]
    # Choose the best.
    _, delim = sorted(counts)[-1]
    return delim


#-------------------------------------------------------------------------------

class DelimitedFileModel:
    """
    Data model that reads incrementally from a delimited (e.g. CSV) file.
    """

    @staticmethod
    def clean_line(line):
        """
        Performs initial cleanup on an incoming line.

        @type line
          `str`.
        @rtype
          `str`.
        """
        return line.replace("\0", "").strip()


    @staticmethod
    def clean_row(row):
        """
        Cleans up values in a parsed row.

        @param row
          The values in a row.
        @type row
          Sequence of `str`.
        @rtype
          Same as `row`.
        """
        return tuple( v.strip(" \"") for v in row )


    def __init__(self, lines, has_header, num_sample, delim, comment_prefix, 
                 filename):
        """
        @type lines
          Iterable of `str`, such as a file object.
        @param has_header
          True to read a column header.
        @param num_sample
          Number of sample lines to read.
        """
        num_sample = max(num_sample, 2)

        # Clean up the incoming lines.
        lines = ( self.clean_line(l) for l in lines )

        self.__lines = lines
        self.__comment_prefix = comment_prefix

        sample_lines, title_comments = self.__read_sample_lines(num_sample)
        self.title_lines = title_comments
        if len(sample_lines) == 0:
            raise EOFError("no data") 

        if delim is None:
            delim = guess_delimiter(sample_lines)

        # Now that we have a delimiter, sanitize the sample rows.
        sample_rows = csv.reader(
            sample_lines, delimiter=delim, quotechar=QUOTE_CHAR)
        self.__rows = [ self.clean_row(r) for r in sample_rows ]

        # Set up to read additional rows.
        more_lines = ( l for l in lines if not self.__is_comment(l) )
        more_rows = csv.reader(
            more_lines, delimiter=delim, quotechar=QUOTE_CHAR)
        self.__more_rows = ( self.clean_row(r) for r in more_rows )

        self.delimiter = delim
        self.done = False
        self.filename = filename

        if has_header:
            self.names = tuple(self.__rows[0])
            self.num_cols = len(self.names)
            self.__rows = self.__rows[1 :]
        else:
            self.num_cols = len(self.__rows[0])
            self.names = tuple( 
                "col{}".format(i + 1) for i in range(self.num_cols) )

        # Transpose the sample lines into columns.
        cols = tuple(zip(*self.__rows))
        # Guess the types for each.
        self.types, self.converts = zip(*[ guess_type(c) for c in cols ])


    def get_default_formatters(self, cfg={}):
        cols = tuple(zip(*self.__rows))
        return [ 
            get_default_formatter(t, [ cv(v) for v in col ], cfg) 
            for t, cv, col in zip(self.types, self.converts, cols) 
            ]


    def __is_comment(self, line):
        return (
            self.__comment_prefix is not None 
            and line.startswith(self.__comment_prefix))


    def __read_sample_lines(self, max_lines):
        """
        Returns samples lines and comment lines before the first useful line.

        @param max_lines
          The number of sample lines to read.
        """
        if max_lines == 0:
            return [], []

        comments = []
        lines = []
        count = 0

        # Read comments from the top.
        line = next(self.__lines)
        while len(line) > 0 and self.__is_comment(line):
            comments.append(line)
            line = self.__read_line()

        # Handle the remaining line from above.
        if len(line) > 0:
            lines.append(line)
            if not self.__is_comment(line):
                count += 1

        # Keep reading.
        while count < max_lines:
            try:
                line = next(self.__lines)
            except StopIteration:
                break
            lines.append(line)
            if not self.__is_comment(line):
                count += 1

        return lines, comments


    @property
    def num_rows(self):
        return len(self.__rows)


    def get_row(self, idx):
        row = self.__rows[idx]
        row = [ c(v) for c, v in zip(self.converts, row) ]
        return row


    def ensure_rows(self, max_row):
        if not self.done:
            while self.num_rows < max_row + SAMPLELINES:
                try:
                    row = next(self.__more_rows)
                except StopIteration:
                    self.done = True
                    break
                else:
                    self.__rows.append(row)
            # FIXME: Check that the new values fit in existing types; adjust
            # types otherwise.
        return min(max_row, self.num_rows)



#-------------------------------------------------------------------------------

class DataFrameModel:
    """
    Data model backed by a Pandas `DataFrame`.
    """

    # We don't load incrementally.
    done = True

    # No title lines available.
    title_lines = []

    def __init__(self, df, filename=None):
        self.__df = df
        self.__filename = filename


    @property
    def num_rows(self):
        return len(self.__df)


    def get_row(self, idx):
        return (self.__df.index[idx], ) + tuple(self.__df.iloc[idx])


    def ensure_rows(self, max_row):
        # We don't load incrementally; nothing to do.
        return len(self.__df)


    @property
    def num_cols(self):
        return 1 + len(self.__df.columns)


    @property
    def names(self):
        return (self.__df.index.name, ) + tuple(self.__df.columns)


    @property
    def filename(self):
        return self.__filename


    # Mapping from dtype kind to dtype.
    TYPE_MAP = {
        "O" : str,
        "b" : bool,
        "f" : float,
        "i" : int,
        "M" : datetime,
        "u" : int,
        }


    def get_default_formatters(self, cfg={}):
        series = (self.__df.index, ) \
            + tuple( self.__df[n] for n in self.__df.columns )
        return tuple(
            get_default_formatter(
                self.TYPE_MAP[s.dtype.kind],
                s.values,
                cfg)
            for s in series )
        


#-------------------------------------------------------------------------------

class GridView:
    """
    View (and controller) for tabular data models.
    """

    def __init__(self, model, cfg={}, num_frozen=0):
        """
        @param num_frozen
          The number of frozen columns on the left.
        """
        self.__model = model
        self.__cfg = cfg
        self.__formatters = list(model.get_default_formatters(cfg))

        self.__num_frozen = num_frozen

        self.__col0 = self.__num_frozen
        self.__idx0 = 0
        self.__cursor = [0, 0]
        self.__show_cursor = as_bool(self.__cfg["show_cursor"])

        self.__screen = None
        self.searchTerm = None
        self.flash = None

        # FIXME: These movement methods needs to be CLEANED UP.
        self.keymap = { 
            ord('p')    : lambda: self.__move_to(0),
            ord('g')    : lambda: self.__move_to(0),
            ord('P')    : lambda: (self.__move_to(0), self.__move_to_col(0)),
            262         : lambda: self.__move("top", 0), # Home
            362         : lambda: self.__move("top", 0), # Home

            ord('e')    : lambda: self.__move_by(1),
            ord('j')    : lambda: self.__move_by(1),
            ord('\n')   : lambda: self.__move_by(1),
            258         : lambda: self.__move(+1, 0), # Down arrow

            ord('y')    : lambda: self.__move_by(-1),
            ord('k')    : lambda: self.__move_by(-1),
            259         : lambda: self.__move(-1, 0), # Up arrow

            ord(' ')    : lambda: self.__move_by(self.__num_rows),
            ord('f')    : lambda: self.__move_by(self.__num_rows),
            ord('z')    : lambda: self.__move_by(self.__num_rows),
            338         : lambda: self.__move_by(self.__num_rows), # PgDn

            ord('b')    : lambda: self.__move_by(-self.__num_rows),
            ord('w')    : lambda: self.__move_by(-self.__num_rows),
            339         : lambda: self.__move_by(-self.__num_rows), # PgUp

            ord('d')    : lambda: self.__move_by(self.__num_rows / 2),
            ord('u')    : lambda: self.__move_by(-self.__num_rows / 2),

            260         : lambda: self.__move(0, -1), # Left arrow
            261         : lambda: self.__move(0, +1), # Right arrow

            ord('G')    : lambda: self.__move_to_end(),
            360         : lambda: self.__move("bottom", 0), # End
            385         : lambda: self.__move("bottom", 0), # End

            # FIXME: Not implemented.
            # ord('F')    : lambda: self.__tail(),

            ord('/')    : lambda: self.__do_search(1),
            ord('?')    : lambda: self.__do_search(-1),
            ord('n')    : lambda: self._nextSearchOccurrence(1),
            ord('N')    : lambda: self._nextSearchOccurrence(-1),
            ord('c')    : lambda: self._nextSearchOccurrence(1, scanToColumn=True),
            ord('C')    : lambda: self._nextSearchOccurrence(-1, scanToColumn=True),
            ord('h')    : lambda: self.__show_help(),

            curses.KEY_IC
                        : lambda: self.__toggle_cursor(),
            ord('|')    : lambda: self.__toggle_sep(),
            ord('H')    : lambda: self.__toggle_header(),
            ord('F')    : lambda: self.__toggle_footer(),

            ord(',')    : lambda: self.__change_size(-1),
            ord('.')    : lambda: self.__change_size(+1),
            ord('<')    : lambda: self.__change_precision(-1),
            ord('>')    : lambda: self.__change_precision(+1),

            410         : lambda: self.__set_geometry() # Window resize
            }

        self.__set_geometry()


    def set_screen(self, scr):
        self.__screen = scr


    def __set_geometry(self):
        self.__screen_width, self.__screen_height = get_terminal_size()

        xtra = 0
        if as_bool(self.__cfg["show_header"]):
            xtra += 1 + len(self.__model.title_lines)
        if as_bool(self.__cfg["show_footer"]):
            xtra += 1

        self.__num_extra_lines = xtra
        self.__num_rows = self.__screen_height - xtra
        self.__idx1 = self.__idx0 + self.__num_rows
        

    def __get_last_col(self):
        sep = len(self.__cfg["separator"])
        x = sum( f.width + sep for f in self.__formatters[: self.__num_frozen] )
        for c in range(self.__col0, self.__model.num_cols):
            x += self.__formatters[c].width + sep
            if x > self.__screen_width:
                return c - 1
        else:
            return self.__model.num_cols - 1


    def __move(self, dr, dc):
        if self.__show_cursor:
            r, c = self.__cursor
            if dr == "top":
                dr = -r
            elif dr == "bottom":
                dr = self.__model.num_rows - 1 - r
            r = clip(0, r + dr, self.__model.num_rows - 1)
            c = clip(0, c + dc, self.__model.num_cols - 1)
            if r < self.__idx0:
                self.__move_by(r - self.__idx0)
            elif r >= self.__idx1:
                self.__move_by(r - self.__idx1 + 1)
            if c < self.__col0:
                self.__move_to_col(c)
            while self.__get_last_col() < c:
                self.__move_to_col(self.__col0 + 1)
            self.__cursor[:] = r, c
        else:
            if dr == "top":
                dr = -self.__idx0
            elif dr == "bottom":
                dr = self.__model.num_rows - self.__num_rows
            if dr != 0:
                self.__move_by(dr)
            if dc != 0:
                self.__move_to_col(self.__col0 + dc)


    def __move_to(self, line):
        self.__idx0 = max(0, line)
        self.__idx1 = self.__idx0 + self.__num_rows
        if self.__model.done:
            self.__idx1 = min(self.__idx1, self.__model.num_rows)
            self.__idx0 = min(self.__idx0, self.__idx1 - 1)
        self.__cursor[0] = clip(self.__idx0, self.__cursor[0], self.__idx1 - 1)


    def __move_by(self, lines):
        self.__move_to(self.__idx0 + lines)


    def __move_to_col(self, col):
        self.__col0 = clip(self.__num_frozen, col, self.__model.num_cols - 1)
        col1 = self.__get_last_col()
        self.__cursor[1] = clip(self.__col0, self.__cursor[1], col1)


    def __toggle_cursor(self):
        self.__show_cursor = not self.__show_cursor

        
    def __toggle_sep(self):
        sep = self.__cfg["separator"]
        try:
            i = SEPARATORS.index(sep)
        except ValueError:
            i = -1
        self.__cfg["separator"] = SEPARATORS[(i + 1) % len(SEPARATORS)]


    def __toggle_header(self):
        self.__cfg["show_header"] = str(not as_bool(self.__cfg["show_header"]))
        self.__set_geometry()


    def __toggle_footer(self):
        self.__cfg["show_footer"] = str(not as_bool(self.__cfg["show_footer"]))
        self.__set_geometry()


    def __change_size(self, dw):
        if self.__show_cursor:
            _, col = self.__cursor
            formatter = self.__formatters[col]
            try:
                size = formatter.size
            except AttributeError:
                pass
            else:
                size = max(size + dw, 1)
                self.__formatters[col] = formatter.changing(size=size)


    def __change_precision(self, dp):
        if self.__show_cursor:
            _, col = self.__cursor
            formatter = self.__formatters[col]
            try:
                precision = formatter.precision
            except AttributeError:
                pass
            else:
                precision = (0 if precision is None else precision) + dp
                precision = None if precision <= 0 else precision
                self.__formatters[col] = formatter.changing(precision=precision)


    def show(self):
        while True:
            if self.__idx1 >= self.__model.num_rows:
                self.__idx1 = self.__model.ensure_rows(self.__idx1)
                self.__idx0 = min(self.__idx0, self.__idx1 - 1)

            self.__print()

            self.lastChar = self._processKeyboard()
            if self.lastChar == ord('q') or self.lastChar == ord('Q'):
                break


    def _processKeyboard(self):
        c = self.__screen.getch()
        if c in self.keymap:
            self.keymap[c]()
        return c


    def __do_search(self, dir):
        self.__screen.addstr(
            self.__screen_height - 1, 0, 
            ("/" if dir == 1 else "?") + " " * (self.__screen_width - 2),
            curses.A_REVERSE)
        curses.echo()
        pattern = self.__screen.getstr(self.__screen_height -1 , 1)
        curses.noecho()
        if len(pattern) > 0:
            self.searchTerm = re.compile(pattern)
            self._nextSearchOccurrence(dir, includeCurrentLine=True)
        else:
            self.searchTerm = None


    def _nextSearchOccurrence(self, dir,
                              includeCurrentLine=False, scanToColumn=False):
        if self.searchTerm is None:
            return
        i = self.__idx0 + (0 if includeCurrentLine or scanToColumn else dir)
        while True:
            if i < 0:
                self._showNoOccurrencesFound()
                return
            if i >= self.num_rows:
                self._ensureLines(self.num_rows)
                if i >= self.num_rows:
                    self._showNoOccurrencesFound()
                    return

            cols = len(self.sampleMatrix[i])
            rng = range(cols) if dir == 1 else range(cols-1, -1, -1)
            for j in rng:
                if scanToColumn and i == self.__idx0 and j <= self.__col0:
                    continue
                cell = self.columns[j].getPaddedString(self.sampleMatrix[i][j])
                if self.searchTerm.search(cell):
                    self.__move_to(i)
                    if scanToColumn:
                        self.__move_to_col(j)
                    return
            i += dir


    def _showNoOccurrencesFound(self):
        self.flash = "Pattern not found"


    def __move_to_end(self):
        idx = self.__model.ensure_rows(sys.maxsize)
        self.__move_to(idx - self.__num_rows)


    def __tail(self):
        raise NotImplementedError("tail")


    def __print(self):
        """
        @param idx
          The row index.
        @param y
          The disply y position.
        """
        self.__screen.erase()

        width   = self.__screen_width
        height  = self.__screen_height
        x       = 0
        y       = 0
        blank   = " " * width
        attrs   = [ curses.color_pair(i) for i in range(1, 8) ]

        def write(string, attr):
            length = width - x - (1 if y == height - 1 else 0)
            self.__screen.addnstr(y, x, string, length, attr)
            return len(string)

        num_frozen  = self.__num_frozen
        col0        = self.__col0
        num_cols    = len(self.__model.names)
        cursor      = self.__cursor
        
        show_cursor = self.__show_cursor
        sep         = self.__cfg["separator"]
        ellipsis    = self.__cfg["ellipsis"]

        # Print title lines first.
        for line in self.__model.title_lines:
            x = write(line)
            y += 1

        # The header.
        if as_bool(self.__cfg["show_header"]):
            x = 0
            for c in list(range(num_frozen)) + list(range(col0, num_cols)):
                frozen = c < num_frozen
                at_cursor = show_cursor and c == cursor[1]

                col = self.__model.names[c]
                col = "" if col is None else col
                fmt = self.__formatters[c]
                col = text.palide(
                    col, fmt.width,
                    ellipsis=ellipsis[: fmt.width], position=0.7, 
                    left=True)

                attr = (
                    attrs[6] if frozen and at_cursor
                    else attrs[4] if at_cursor
                    else attrs[1] if frozen
                    else attrs[0])
                attr |= curses.A_UNDERLINE | curses.A_BOLD
                x += write(col, attr)
                if x >= width:
                    break

                x += write(sep, attrs[2])
                if x >= width:
                    break

            # Next line.
            y += 1

        # Data.
        for i in range(self.__num_rows):
            x   = 0
            idx = self.__idx0 + i
            row = (
                self.__model.get_row(idx) 
                if idx < self.__model.num_rows 
                else None)
            for c in list(range(num_frozen)) + list(range(col0, num_cols)):
                frozen = c < num_frozen
                at_cursor = show_cursor and (idx == cursor[0] or c == cursor[1])
                at_select = show_cursor and (idx == cursor[0] and c == cursor[1])

                if row is None:
                    col = "~" if c == 0 else ""
                else:
                    col = self.__formatters[c](row[c])

                attr = (
                    attrs[5] if at_select
                    else attrs[6] if frozen and at_cursor
                    else attrs[4] if at_cursor
                    else attrs[1] if frozen
                    else attrs[0])
                x += write(col, attr)
                if x >= width:
                    break

                attr = (
                    attrs[4] if show_cursor and idx == cursor[0]
                    else attrs[2])
                x += write(sep, attr)
                if x >= width:
                    break

            y += 1

        # Footer.
        if as_bool(self.__cfg["show_footer"]):
            x = 0
            if self.flash is not None:
                status = self.flash
                self.flash = None
            else:
                filename = str(self.__model.filename)
                status = "{}{}lines {}-{}/{}".format(
                    filename,
                    " " if len(filename) > 0 else "",
                    self.__idx0,
                    self.__idx1,
                    self.__model.num_rows)
                if self.__model.done:
                    frac = self.__idx1 / self.__model.num_rows
                    status += " {:.0f}%".format(100 * frac)
                else:
                    status += "+"
            if self.__show_cursor:
                r, c = self.__cursor
                value = str(self.__model.get_row(r)[c])
                value = text.elide(
                    value, width - len(status) - 4, 
                    ellipsis=self.__cfg["ellipsis"])
            else:
                value = ""
            status += " " * (width - len(status) - len(value) - 1) + value
            x += write(status, attrs[3] | curses.A_REVERSE)


    def __show_help(self):
        bar = "-"*71
        content = ["",
                   "*                       SUMMARY OF NGRID COMMANDS",
                   "",
                   "  h                  Display this help",
                   "  q Q                Exit",
                   bar,
                   "",
                   "*                              MOVING",
                   "",
                   "  e j DownArrow RET  Forward  one line",
                   "  y k UpArrow        Backward one line",
                   "  f z PgDn SPACE     Forward  one window",
                   "  b w PgUp           Backward one window",
                   "  d                  Forward  one half-window",
                   "  u                  Backward one half-window",
                   "  p g Home           Jump to first row",
                   "  P                  Jump to first row and leftmost column",
                   "  G                  Jump to last row of file",
                   "  End                Jump to last row read in so far",
                   "  F                  Forward forever; like \"tail -f\" (not implemented)",
                   bar,
                   "",
                   "*                             SEARCHING",
                   "",
                   " /pattern            Search forward for next matching line",
                   " ?pattern            Search backward for previous matching line",
                   " n                   Repeat previous search forwards",
                   " N                   Repeat previous search backwards",
                   " c                   Search forwards and scan to matching column",
                   " C                   Search backwards and scan to matching column",
                   "",
                   "",
                   "Press any key when done."]

        while True:
            self.__screen.clear()
            for i in range(len(content)):
                if i >= self.__screen_height:
                    break
                line = content[i]
                mode = curses.A_NORMAL
                if len(line) > 0 and line[0] == '*':
                    mode = curses.A_BOLD
                    line = re.sub("\*", " ", line, 1)
                width = self.__screen_width if i < self.__screen_height-1 else self.__screen_width - 1
                self.__screen.addstr(i, 0, line[:width], mode)

            if self.__screen.getch() == 410:
                self.__set_geometry()
                self.__screen.getch() # extra -1
            else:
                break



#-------------------------------------------------------------------------------

def show_model(model, cfg={}, num_frozen=0):
    """
    Shows an interactive view of the model on a connected TTY.

    @type model
      A model instance from this module.
    """
    full_cfg = dict(DEFAULT_CFG)
    full_cfg.update(cfg)
    cfg = full_cfg

    view = GridView(model, cfg, num_frozen=num_frozen)
    scr = curses.initscr()

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, -1, -1)                                     # normal
    curses.init_pair(2, curses.COLOR_BLUE, -1)                      # frozen
    curses.init_pair(3, -1, -1)                                     # separator
    curses.init_pair(4, -1, -1)                                     # footer
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)     # cursor
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)      # selection
    curses.init_pair(7, curses.COLOR_BLUE,  curses.COLOR_WHITE)     # frz sel

    try:
        curses.noecho()
        curses.cbreak()
        scr.keypad(1)
        view.set_screen(scr)
        view.show()
    finally:
        curses.nocbreak()
        scr.keypad(0)
        curses.echo()
        curses.endwin()


def show_dataframe(df, cfg={}, filename=None, **kw_args):
    """
    Shows an interactive view of the dataframe on a connected TTY.
    """
    model = DataFrameModel(df, filename=filename)
    show_model(model, cfg, **kw_args)


