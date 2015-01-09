from   collections import OrderedDict
from   datetime import datetime, date
from   pytz import UTC, timezone
import numpy as np
import pandas as pd
import cPickle as pickle
import random

LETTERS = "abcdefghijklmnopqrstuvwxyz"

def random_word():
    length = random.randint(3, 12)
    return "".join( random.choice(LETTERS) for _ in range(length) )


N = 65563

cols = OrderedDict()
cols.update(
    ("flag{}".format(i), np.random.randint(0, 2, (N, )).astype(bool))
    for i in range(4)
    )
cols.update(
    ("normal{}".format(i), np.random.standard_normal((N, )))
    for i in range(4)
    )
cols.update(
    ("exp{}".format(i), np.exp(np.random.random((N, )) * 20))
    for i in range(2)
    )
cols.update(
    ("expexp{}".format(i), np.exp(np.exp(np.random.random((N, )) * 5)))
    for i in range(2)
    )
cols.update(
    ("count{}".format(i), np.exp(np.random.random((N, )) * 20).astype("int32"))
    for i in range(8)
    )
cols.update(
    ("word{}".format(i), [ random_word() for _ in range(N) ])
    for i in range(4)
    )
cols.update(
    ("datetime{}".format(i), (np.random.uniform(631152000e9, 1577836800e9, (N, ))).astype("datetime64[ns]"))
    for i in range(4)
    )

df = pd.DataFrame(cols)
with open("sample0.pickle", "wb") as file:
    pickle.dump(df, file, pickle.HIGHEST_PROTOCOL)

df.to_csv("sample0.csv")

