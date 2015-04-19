"""
Text utilities.
"""

#-------------------------------------------------------------------------------

import six

#-------------------------------------------------------------------------------

def indent(string, indent):
    """
    Indents each line of a string.
    """
    return (
        "\n".join( indent + l for l in string.splitlines() ) 
        + ("\n" if string.endswith("\n") else ""))


def pad(string, length, pad=" ", left=False):
    """
    Pads a string to achieve a minimum length.

    @param pad
      The pad character.
    @param left
      If true, pad on the left; otherwise on the right.
    """
    if len(pad) != 1:
        raise ValueError("pad is not a character: {!r}".format(pad))

    if len(string) < length:
        pad = pad * (length - len(string))
        return pad + string if left else string + pad
    else:
        return string


def elide(string, max_length, ellipsis="...", position=1.0):
    """
    Elides characters to reduce a string to a maximum length.

    Replaces elided characters with an ellipsis. 

      >>> string = "Hello, world.  This is a test."
      >>> elide(string, 24)
      'Hello, world.  This i...'
      >>> elide(string, 24, ellipsis=" and more")
      'Hello, world.   and more'
      
    The position of the ellipsis is specified as a fraction of the total string
    length.
    
      >>> string = "Hello, world.  This is a test."
      >>> elide(string, 24, position=0)
      '...rld.  This is a test.'
      >>> elide(string, 24, position=0.7)
      'Hello, world.  ... test.'

    """
    assert max_length >= len(ellipsis)
    assert 0 <= position <= 1

    string = six.text_type(string)
    length = len(string)
    if length <= max_length:
        return string

    keep    = max_length - len(ellipsis)
    left    = int(round(position * keep))
    right   = keep - left
    left    = string[: left] if left > 0 else ""
    right   = string[-right :] if right > 0 else ""
    elided  = left + ellipsis + right
    assert len(elided) == max_length
    return elided


def palide(string, length, ellipsis="...", pad=" ", position=1.0, left=False):
    """
    A combination of `elide` and `pad`.
    """
    return globals()["pad"](
        elide(string, length, ellipsis=ellipsis, position=position), 
        length, pad=pad, left=left)


