import unittest

from   ngrid.formatters import *

#-------------------------------------------------------------------------------

class BoolFormatterTest(unittest.TestCase):

    def test_default(self):
        fmt = BoolFormatter()
        self.assertEqual('True ', fmt(True))
        self.assertEqual('False', fmt(False))
        self.assertEqual('True ', fmt(1))
        self.assertEqual('False', fmt(0))
        self.assertEqual('True ', fmt('yes'))
        self.assertEqual('False', fmt(''))
        self.assertEqual('True ', fmt({3, 4, 5}))
        self.assertEqual('False', fmt(None))


    def test_names(self):
        fmt = BoolFormatter('yes', 'no')
        self.assertEqual('yes', fmt(True))
        self.assertEqual('no ', fmt(False))


    def test_size(self):
        fmt = BoolFormatter(size=8)
        self.assertEqual('True    ', fmt(True))
        self.assertEqual('False   ', fmt(False))

        fmt = BoolFormatter(size=2)
        self.assertEqual('Tr', fmt(True))
        self.assertEqual('Fa', fmt(False))

        fmt = BoolFormatter('Definitely so', 'Absolutely not', size=8)
        self.assertEqual('Definite', fmt(True))
        self.assertEqual('Absolute', fmt(False))


    def test_pad_left(self):
        fmt = BoolFormatter(pad_left=True)
        self.assertEqual(' True', fmt(True))
        self.assertEqual('False', fmt(False))

        fmt = BoolFormatter(size=12, pad_left=True)
        self.assertEqual('        True', fmt(True))
        self.assertEqual('       False', fmt(False))



#-------------------------------------------------------------------------------

class IntFormatterTest(unittest.TestCase):

    def test_default(self):
        fmt = IntFormatter(4)
        self.assertEqual('    0', fmt(0))
        self.assertEqual('    1', fmt(1))
        self.assertEqual(' 9999', fmt(9999))
        self.assertEqual('#####', fmt(10000))
        self.assertEqual('   -1', fmt(-1))
        self.assertEqual('  -10', fmt(-10))
        self.assertEqual('-9999', fmt(-9999))
        self.assertEqual('#####', fmt(-10000))

        self.assertEqual('    1', fmt(True))
        self.assertEqual('    0', fmt(False))

        self.assertEqual(' 1000', fmt(1.0e+3))


    def test_size(self):
        fmt = IntFormatter(1)
        self.assertEqual(' 4', fmt(4))
        self.assertEqual('-6', fmt(-6))
        self.assertEqual('##', fmt(-10))

        fmt = IntFormatter(20)
        self.assertEqual('                    0', fmt(0))
        self.assertEqual('                   -1', fmt(-1))
        self.assertEqual(' 10000000000000000000', fmt(1e+19))
        self.assertEqual('-10000000000000000000', fmt(-1e+19))
        self.assertEqual(' 99999999999999999999', fmt(int(1e+20) - 1))
        self.assertEqual('-99999999999999999998', fmt(int(-1e+20) + 2))


    def test_pad(self):
        fmt = IntFormatter(4, pad=' ')
        self.assertEqual('    0', fmt(0))
        self.assertEqual('    1', fmt(1))
        self.assertEqual('   -1', fmt(-1))
        self.assertEqual('  999', fmt(999))
        self.assertEqual('-9999', fmt(-9999))
        self.assertEqual('#####', fmt(10000))

        fmt = IntFormatter(4, pad='0')
        self.assertEqual(' 0000', fmt(0))
        self.assertEqual(' 0001', fmt(1))
        self.assertEqual('-0001', fmt(-1))
        self.assertEqual(' 0999', fmt(999))
        self.assertEqual('-9999', fmt(-9999))
        self.assertEqual('#####', fmt(10000))


    def test_sign(self):
        fmt = IntFormatter(4, sign="-")
        self.assertEqual(5, fmt.width)
        self.assertEqual('    0', fmt(0))
        self.assertEqual('   -1', fmt(-1))
        self.assertEqual(' 1000', fmt(1000))
        self.assertEqual('-1000', fmt(-1000))
        self.assertEqual('#####', fmt(10000))

        fmt = IntFormatter(4, sign="+")
        self.assertEqual(5, fmt.width)
        self.assertEqual('   +0', fmt(0))
        self.assertEqual('   -1', fmt(-1))
        self.assertEqual('+1000', fmt(1000))
        self.assertEqual('-1000', fmt(-1000))
        self.assertEqual('#####', fmt(10000))

        fmt = IntFormatter(4, sign=None)
        self.assertEqual(4, fmt.width)
        self.assertEqual('   0', fmt(0))
        self.assertEqual('   1', fmt(1))
        self.assertEqual('####', fmt(-1))
        self.assertEqual('1000', fmt(1000))
        self.assertEqual('####', fmt(-1000))
        self.assertEqual('####', fmt(10000))



#-------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

