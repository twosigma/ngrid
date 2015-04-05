from   __future__ import absolute_import

from   contextlib import closing
import locale
import optparse
import os
import sys

from   six import print_

from   . import grid

#-------------------------------------------------------------------------------

class OutputSaver:
    """
    Captures `sys.stdout` and `sys.stderr` and prints it on close.
    """

    def __init__(self):
        self.__text = ""
        self.__old_stdout = sys.stdout
        self.__old_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self


    def write(self, text):
        self.__text += text


    def close(self):
        sys.stdout = self.__old_stdout
        sys.stderr = self.__old_stderr
        print_(self.__text)



#-------------------------------------------------------------------------------

def main():
    # Set the default locale.  This is required for ncurses to decode encoded
    # strings.  Hopefully, the encoding supports the characters we use.
    locale.setlocale(locale.LC_ALL, "")

    parser = optparse.OptionParser()

    parser.set_defaults(hasHeader=True, commentString=None)
    parser.add_option(
        "-n", "--no_header",
        action="store_false", dest="hasHeader",
        help="assume no header row")

    parser.set_defaults(frozenCols=1)
    parser.add_option(
        "-f", "--frozen_cols", metavar="NCOLS",
        action="store", type="int", dest="frozenCols",
        help=("freeze NCOLS columns on the left [default: 1]"))
    
    parser.set_defaults(bufferSize=100)
    parser.add_option(
        "-b", "--buffer_size", metavar="NROWS",
        action="store", type="int", dest="bufferSize",
        help=("read NROWS rows to guess data types [default: 100]"))

    parser.add_option(
        "-d", "--delimiter", metavar="CHAR",
        action="store", type="string", dest="delim",
        help="use CHAR as the column delimiter")

    parser.add_option(
        "-c", "--comment", metavar="PREFIX",
        action="store", type="string", dest="commentString",
        help=("treat lines starting with PREFIX as comments"))

    parser.add_option(
        "-D", "--dataframe",
        action="store_true", dest="dataframe", default=False,
        help=("load input into dataframe"))

    options, args = parser.parse_args()

    if len(args) < 1:
        file = os.fdopen(os.dup(0), 'r')
        os.close(0)
        sys.stdin = os.open("/dev/tty", os.O_RDONLY)
        filename = "(stdin)"
    else:
        filename = args[0]
        file = open(filename)

    with closing(file):
        if options.dataframe:
            import pandas
            df = pandas.read_csv(filename)
            model = grid.DataFrameModel(df, filename=filename)
        else:
            model = grid.DelimitedFileModel(
                file, options.hasHeader, options.bufferSize, options.delim,
                options.commentString, filename=filename)

        with closing(OutputSaver()):
            grid.show_model(model, num_frozen=options.frozenCols)


if __name__ == '__main__':
    try:    
        main()
    except (IOError, EOFError) as exc:
        print_(exc, file=sys.stderr)
    except KeyboardInterrupt:
        pass


