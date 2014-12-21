"""
Terminal control.
"""

#-------------------------------------------------------------------------------

import fcntl
import os
import struct
import termios

#-------------------------------------------------------------------------------

def get_cgwinsz(fd):
    """
    Attempts to get window size from termios `TIOCGWINSZ` ioctl.

    @raise NotImplementedError
      The ioctl is not available.
    @raise IOError
      The fd is not a TTY.
    """
    try:
        TIOCGWINSZ = termios.TIOCGWINSZ
    except AttributeError:
        raise NotImplementedError("no TIOCGWINSZ")

    Winsize = struct.Struct("HHHH")
    winsz = fcntl.ioctl(fd, TIOCGWINSZ, " " * Winsize.size)
    height, width, _, _ = Winsize.unpack(winsz)
    return height, width


def get_terminal_size(default=(80, 25)):
    """
    Attempts to determine the terminal width and height.

    Returns:
      1. The values from environment variables 'COLUMNS' and 'LINES', if set 
         and integers.
      2. Else, the width of the TTY attached to any one stdin/stdout/stderr.
      3. Else, the default value.
    """
    def try_env(name):
        try:
            val = int(os.environ[name])
        except (KeyError, ValueError):
            pass
        else:
            if val > 0:
                return val
        return None

    width = try_env("COLUMNS")
    height = try_env("LINES")
    
    if width is None or height is None:
        # Try each of the original stdin, stdout, stderr for attached TTY.
        for fd in (0, 1, 2):
            try:
                winsz_height, winsz_width = get_cgwinsz(fd)
            except (NotImplementedError, IOError):
                pass
            else:
                if height is None:
                    height = winsz_height
                if width is None:
                    width = winsz_width
                break

    if width is None:
        width = default[0]
    if height is None:
        height = default[1]

    return width, height


def get_terminal_width(default=80):
    """
    Attempts to determine the terminal width.

    @deprecated
      Use `get_terminal_size()`.
    """
    width, _ = get_terminal_size(default=(default, 25))
    return width


