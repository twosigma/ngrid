_It's "less" for your data!_

ngrid is a tool for interactive browsing large tabular datasets in a text-based
terminal enviroment.  ngrid is to tables as
[less](http://en.wikipedia.org/wiki/Less_%28Unix%29) is to text.


## Installing

```
pip install git+https://github.com/twosigma/ngrid
```


## Command line

The `ngrid` command reads CSV data from a file, or from standard input if no
filename is specified, and displays it in an interactive, ncurses-based grid.  

By default, ngrid loads rows incrementally from its input, so that it can
quickly present the beginning of a long file or stream without loading the
entirety of the data.  (The total line count in the status bar shows "+" to
indicate that more lines are available but have not been read.)  It does however
store all data it has already seen, so that you can always scroll backward.

With the `--dataframe` option, `ngrid` instead loads the entire input into a 
Pandas dataframe at startup.  This may result in better guesses for column
display parameters, such as width and decimal precision.

In the interactive display, press `h` to show usage help; press `q` to exit.


## API

Use `ngrid.grid.show_dataframe()` to show a Pandas dataframe.  As with the
command line program, press `q` to exit the interactive display and return
control.

ngrid works only in an ncurses-compatible terminal; it won't work in IPython
Notebook, most IDEs, or similar graphical environments.



## License

Copyright (c) 2014, Two Sigma Open Source.  All rights reserved.  Released under
the BSD three-clause license.  See [LICENSE.txt](LICENSE.txt) for details.

