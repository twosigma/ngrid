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
        self.assertEqual('    0', fmt(     0))
        self.assertEqual('    1', fmt(     1))
        self.assertEqual(' 9999', fmt(  9999))
        self.assertEqual('#####', fmt( 10000))
        self.assertEqual('   -1', fmt(    -1))
        self.assertEqual('  -10', fmt(   -10))
        self.assertEqual('-9999', fmt( -9999))
        self.assertEqual('#####', fmt(-10000))

        self.assertEqual('    1', fmt(True))
        self.assertEqual('    0', fmt(False))

        self.assertEqual(' 1000', fmt(1.0e+3))
        self.assertEqual('  999', fmt( 999.499))
        self.assertEqual(' 1000', fmt( 999.5))
        self.assertEqual(' -999', fmt(-999.499))
        self.assertEqual('-1000', fmt(-999.5))


    def test_size(self):
        fmt = IntFormatter(1)
        self.assertEqual(' 4', fmt(  4))
        self.assertEqual('-6', fmt( -6))
        self.assertEqual('##', fmt(-10))

        fmt = IntFormatter(20)
        self.assertEqual('                    0', fmt( 0))
        self.assertEqual('                   -1', fmt(-1))
        self.assertEqual(' 10000000000000000000', fmt( 1e+19))
        self.assertEqual('-10000000000000000000', fmt(-1e+19))
        self.assertEqual(' 99999999999999999999', fmt(int( 1e+20) - 1))
        self.assertEqual('-99999999999999999998', fmt(int(-1e+20) + 2))


    def test_pad(self):
        fmt = IntFormatter(4, pad=' ')
        self.assertEqual('    0', fmt(    0))
        self.assertEqual('    1', fmt(    1))
        self.assertEqual('   -1', fmt(   -1))
        self.assertEqual('  999', fmt(  999))
        self.assertEqual('-9999', fmt(-9999))
        self.assertEqual('#####', fmt(10000))

        fmt = IntFormatter(4, pad='0')
        self.assertEqual(' 0000', fmt(    0))
        self.assertEqual(' 0001', fmt(    1))
        self.assertEqual('-0001', fmt(   -1))
        self.assertEqual(' 0999', fmt(  999))
        self.assertEqual('-9999', fmt(-9999))
        self.assertEqual('#####', fmt(10000))


    def test_sign(self):
        fmt = IntFormatter(4, sign="-")
        self.assertEqual(5, fmt.width)
        self.assertEqual('    0', fmt(    0))
        self.assertEqual('   -1', fmt(   -1))
        self.assertEqual(' 1000', fmt( 1000))
        self.assertEqual('-1000', fmt(-1000))
        self.assertEqual('#####', fmt(10000))

        fmt = IntFormatter(4, sign="+")
        self.assertEqual(5, fmt.width)
        self.assertEqual('   +0', fmt(    0))
        self.assertEqual('   -1', fmt(   -1))
        self.assertEqual('+1000', fmt( 1000))
        self.assertEqual('-1000', fmt(-1000))
        self.assertEqual('#####', fmt(10000))

        fmt = IntFormatter(4, sign=None)
        self.assertEqual(4, fmt.width)
        self.assertEqual('   0', fmt(    0))
        self.assertEqual('   1', fmt(    1))
        self.assertEqual('####', fmt(   -1))
        self.assertEqual('1000', fmt( 1000))
        self.assertEqual('####', fmt(-1000))
        self.assertEqual('####', fmt(10000))



#-------------------------------------------------------------------------------

POS_INF = float("+Inf")
NEG_INF = float("-Inf")
NAN = float("NaN")

class FloatFormatterTest(unittest.TestCase):

    def test_default(self):
        fmt = FloatFormatter(4, 2)
        self.assertEqual(8, fmt.width)
        self.assertEqual('    0.00', fmt(      0.0  ))
        self.assertEqual('    1.00', fmt(      1.0  ))
        self.assertEqual('   -1.00', fmt(     -1.0  ))
        self.assertEqual('   12.34', fmt(     12.344))
        self.assertEqual('   12.34', fmt(     12.3449999999))
        self.assertEqual('   12.35', fmt(     12.3450000001))
        self.assertEqual('  -12.34', fmt(    -12.3449999999))
        self.assertEqual('  -12.35', fmt(    -12.3450000001))
        self.assertEqual(' 9999.99', fmt(   9999.99 ))
        self.assertEqual('-9999.99', fmt(  -9999.99 ))
        self.assertEqual('########', fmt(   9999.999))
        self.assertEqual('########', fmt(  -9999.999))
        self.assertEqual('     NaN', fmt(NAN))
        self.assertEqual('     Inf', fmt(POS_INF))
        self.assertEqual('    -Inf', fmt(NEG_INF))


    def test_precision_none(self):
        fmt = FloatFormatter(4, None)
        self.assertEqual(5, fmt.width)
        self.assertEqual('    0', fmt(      0.0  ))
        self.assertEqual('    1', fmt(      1.0  ))
        self.assertEqual('   -1', fmt(     -1.0  ))
        self.assertEqual('   12', fmt(     12.4))
        self.assertEqual('   12', fmt(     12.49999999))
        self.assertEqual('   13', fmt(     12.50000001))
        self.assertEqual('  -12', fmt(    -12.49999999))
        self.assertEqual('  -13', fmt(    -12.50000001))
        self.assertEqual(' 9999', fmt(   9998.99 ))
        self.assertEqual('-9999', fmt(  -9998.99 ))
        self.assertEqual('#####', fmt(   9999.999))
        self.assertEqual('#####', fmt(  -9999.999))
        self.assertEqual('  NaN', fmt(NAN))
        self.assertEqual('  Inf', fmt(POS_INF))
        self.assertEqual(' -Inf', fmt(NEG_INF))


    def test_precision_0(self):
        fmt = FloatFormatter(4, 0)
        self.assertEqual(6, fmt.width)
        self.assertEqual('    0.', fmt(      0.0  ))
        self.assertEqual('    1.', fmt(      1.0  ))
        self.assertEqual('   -1.', fmt(     -1.0  ))
        self.assertEqual('   12.', fmt(     12.4))
        self.assertEqual('   12.', fmt(     12.49999999))
        self.assertEqual('   13.', fmt(     12.50000001))
        self.assertEqual('  -12.', fmt(    -12.49999999))
        self.assertEqual('  -13.', fmt(    -12.50000001))
        self.assertEqual(' 9999.', fmt(   9998.99 ))
        self.assertEqual('-9999.', fmt(  -9998.99 ))
        self.assertEqual('######', fmt(   9999.999))
        self.assertEqual('######', fmt(  -9999.999))
        self.assertEqual('   NaN', fmt(NAN))
        self.assertEqual('   Inf', fmt(POS_INF))
        self.assertEqual('  -Inf', fmt(NEG_INF))


    def test_pad_0(self):
        fmt = FloatFormatter(4, 2, pad="0")
        self.assertEqual(8, fmt.width)
        self.assertEqual(' 0000.00', fmt(      0.0  ))
        self.assertEqual(' 0001.00', fmt(      1.0  ))
        self.assertEqual('-0001.00', fmt(     -1.0  ))
        self.assertEqual(' 0012.34', fmt(     12.344))
        self.assertEqual(' 0012.34', fmt(     12.3449999999))
        self.assertEqual(' 0012.35', fmt(     12.3450000001))
        self.assertEqual('-0012.34', fmt(    -12.3449999999))
        self.assertEqual('-0012.35', fmt(    -12.3450000001))
        self.assertEqual(' 9999.99', fmt(   9999.99 ))
        self.assertEqual('-9999.99', fmt(  -9999.99 ))
        self.assertEqual('########', fmt(   9999.999))
        self.assertEqual('########', fmt(  -9999.999))
        self.assertEqual('     NaN', fmt(NAN))
        self.assertEqual('     Inf', fmt(POS_INF))
        self.assertEqual('    -Inf', fmt(NEG_INF))


    def test_sign_plus(self):
        fmt = FloatFormatter(4, 2, sign="+")
        self.assertEqual(8, fmt.width)
        self.assertEqual('   +0.00', fmt(      0.0  ))
        self.assertEqual('   +1.00', fmt(      1.0  ))
        self.assertEqual('   -1.00', fmt(     -1.0  ))
        self.assertEqual('  +12.34', fmt(     12.344))
        self.assertEqual('  +12.34', fmt(     12.3449999999))
        self.assertEqual('  +12.35', fmt(     12.3450000001))
        self.assertEqual('  -12.34', fmt(    -12.3449999999))
        self.assertEqual('  -12.35', fmt(    -12.3450000001))
        self.assertEqual('+9999.99', fmt(   9999.99 ))
        self.assertEqual('-9999.99', fmt(  -9999.99 ))
        self.assertEqual('########', fmt(   9999.999))
        self.assertEqual('########', fmt(  -9999.999))
        self.assertEqual('     NaN', fmt(NAN))
        self.assertEqual('    +Inf', fmt(POS_INF))
        self.assertEqual('    -Inf', fmt(NEG_INF))


    def test_sign_none(self):
        fmt = FloatFormatter(4, 2, sign=None)
        self.assertEqual(7, fmt.width)
        self.assertEqual('   0.00', fmt(      0.0  ))
        self.assertEqual('   1.00', fmt(      1.0  ))
        self.assertEqual('#######', fmt(     -1.0  ))
        self.assertEqual('  12.34', fmt(     12.344))
        self.assertEqual('  12.34', fmt(     12.3449999999))
        self.assertEqual('  12.35', fmt(     12.3450000001))
        self.assertEqual('#######', fmt(    -12.3449999999))
        self.assertEqual('#######', fmt(    -12.3450000001))
        self.assertEqual('9999.99', fmt(   9999.99 ))
        self.assertEqual('#######', fmt(  -9999.99 ))
        self.assertEqual('#######', fmt(   9999.999))
        self.assertEqual('#######', fmt(  -9999.999))
        self.assertEqual('    NaN', fmt(NAN))
        self.assertEqual('    Inf', fmt(POS_INF))
        self.assertEqual('#######', fmt(NEG_INF))


    def test_point(self):
        fmt = FloatFormatter(4, 2, point=",")
        self.assertEqual(8, fmt.width)
        self.assertEqual('    0,00', fmt(      0.0  ))
        self.assertEqual('   -1,00', fmt(     -1.0  ))
        self.assertEqual('-9999,99', fmt(  -9999.99 ))
        self.assertEqual('########', fmt(   9999.999))


    def test_nan_str(self):
        fmt = FloatFormatter(4, 2, nan_str="INVALID")
        self.assertEqual(8, fmt.width)
        self.assertEqual('    0.00', fmt(      0.0  ))
        self.assertEqual('-9999.99', fmt(  -9999.99 ))
        self.assertEqual(' INVALID', fmt(NAN))

        self.assertRaises(Exception, FloatFormatter, 4, 0, nan_str="INVALID")


    def test_inf_str(self):
        fmt = FloatFormatter(4, 3, inf_str="INFINITE")
        self.assertEqual(9, fmt.width)
        self.assertEqual('    0.000', fmt(      0.0  ))
        self.assertEqual('-9999.990', fmt(  -9999.99 ))
        self.assertEqual(' INFINITE', fmt(POS_INF))
        self.assertEqual('-INFINITE', fmt(NEG_INF))

        self.assertRaises(Exception, FloatFormatter, 4, 0, inf_str="INFINITE")



#-------------------------------------------------------------------------------

class EFloatFormatterTest(unittest.TestCase):

    def test_default(self):
        fmt = EFloatFormatter(2, 2)
        self.assertEqual(9, fmt.width)
        self.assertEqual(' 0.00E+00', fmt(            0.0))
        self.assertEqual(' 1.00E+00', fmt(            1.0))
        self.assertEqual('-1.00E+00', fmt(           -1.0))
        self.assertEqual(' 9.90E-01', fmt(            0.99))
        self.assertEqual(' 9.95E-01', fmt(            0.994999))
        self.assertEqual(' 9.95E-01', fmt(            0.995001))
        self.assertEqual(' 1.00E+00', fmt(            0.999501))
        self.assertEqual('-9.90E-01', fmt(           -0.99))
        self.assertEqual('-9.95E-01', fmt(           -0.994999))
        self.assertEqual('-9.95E-01', fmt(           -0.995001))
        self.assertEqual('-1.00E+00', fmt(           -0.999501))
        self.assertEqual(' 1.00E+03', fmt(         1000.0))
        self.assertEqual('-1.00E+03', fmt(        -1000.0))
        self.assertEqual(' 1.23E+11', fmt( 123456789012))
        self.assertEqual('-1.23E+11', fmt(-123456789012))
        self.assertEqual(' 1.24E+11', fmt( 123556789012))
        self.assertEqual('-1.24E+11', fmt(-123556789012))
        self.assertEqual(' 1.23E-13', fmt(            0.0000000000001234))
        self.assertEqual('-1.23E-13', fmt(           -0.0000000000001234))
        self.assertEqual(' 1.24E-13', fmt(            0.000000000000123501))
        self.assertEqual('-1.24E-13', fmt(           -0.000000000000123501))
        self.assertEqual(' 9.99E+99', fmt(            9.99e+99))
        self.assertEqual('-9.99E+99', fmt(           -9.99e+99))
        self.assertEqual('#########', fmt(            9.996e+99))
        self.assertEqual('#########', fmt(           -9.996e+99))
        self.assertEqual('#########', fmt(            1e+100))
        self.assertEqual('#########', fmt(           -1e+100))
        self.assertEqual(' 1.00E-99', fmt(            1.00e-99))
        self.assertEqual(' 1.00E-99', fmt(            0.999501e-99))
        self.assertEqual('-1.00E-99', fmt(           -1.00e-99))
        self.assertEqual('-1.00E-99', fmt(           -0.999501e-99))
        self.assertEqual('#########', fmt(            0.994e-99))
        self.assertEqual('#########', fmt(           -0.994e-99))
        self.assertEqual('#########', fmt(            1e-100))
        self.assertEqual('#########', fmt(           -1e-100))
        self.assertEqual('      NaN', fmt(NAN))
        self.assertEqual('      Inf', fmt(POS_INF))
        self.assertEqual('     -Inf', fmt(NEG_INF))


    def test_size_1(self):
        fmt = EFloatFormatter(1, 2)
        self.assertEqual(8, fmt.width)
        self.assertEqual(' 0.00E+0', fmt(          0.0))
        self.assertEqual(' 9.95E-1', fmt(          0.995001))
        self.assertEqual(' 1.00E+0', fmt(          0.999501))
        self.assertEqual('-9.95E-1', fmt(         -0.995001))
        self.assertEqual('-1.00E+0', fmt(         -0.999501))
        self.assertEqual(' 9.99E+9', fmt( 9994999999.99))
        self.assertEqual('-9.99E+9', fmt(-9994999999.99))
        self.assertEqual('########', fmt( 9995000001.0))
        self.assertEqual('########', fmt(-9995000001.0))
        self.assertEqual(' 1.00E-9', fmt(          0.0000000009995001))
        self.assertEqual('-1.00E-9', fmt(         -0.0000000009995001))
        self.assertEqual('########', fmt(          0.0000000009994999))
        self.assertEqual('########', fmt(         -0.0000000009994999))
        self.assertEqual('     NaN', fmt(NAN))
        self.assertEqual('     Inf', fmt(POS_INF))
        self.assertEqual('    -Inf', fmt(NEG_INF))


    def test_size_4(self):
        fmt = EFloatFormatter(4, 2)
        self.assertEqual(11, fmt.width)
        self.assertEqual(' 0.00E+0000', fmt( 0.0))
        self.assertEqual(' 9.95E-0001', fmt( 0.995001))
        self.assertEqual(' 1.00E+0000', fmt( 0.999501))
        self.assertEqual(' 1.23E+0110', fmt( 1.23e+110))
        self.assertEqual('-1.23E-0110', fmt(-1.23e-110))


    def test_precision_none(self):
        fmt = EFloatFormatter(2, None)
        self.assertEqual(6, fmt.width)
        self.assertEqual(' 0E+00', fmt(            0.0))
        self.assertEqual(' 1E+00', fmt(            1.0))
        self.assertEqual('-1E+00', fmt(           -1.0))
        self.assertEqual(' 5E-01', fmt(            0.500001))
        self.assertEqual('-5E-01', fmt(           -0.500001))
        self.assertEqual('-5E-01', fmt(           -0.4999))
        self.assertEqual('-1E+00', fmt(           -0.995001))
        self.assertEqual('-1E+00', fmt(           -0.999501))
        self.assertEqual(' 1E+03', fmt(         1000.0))
        self.assertEqual('-1E+03', fmt(        -1000.0))
        self.assertEqual(' 1E+11', fmt( 123456789012))
        self.assertEqual('-1E+11', fmt(-123456789012))
        self.assertEqual(' 2E+11', fmt( 150000000001))
        self.assertEqual('-2E+11', fmt(-150000000001))
        self.assertEqual(' 1E-13', fmt(            0.0000000000001234))
        self.assertEqual('-1E-13', fmt(           -0.0000000000001234))
        self.assertEqual(' 1E+99', fmt(            1e+99))
        self.assertEqual('-1E+99', fmt(           -1e+99))
        self.assertEqual('######', fmt(            9.50001e+99))
        self.assertEqual('######', fmt(           -9.50001e+99))
        self.assertEqual('   NaN', fmt(NAN))
        self.assertEqual('   Inf', fmt(POS_INF))
        self.assertEqual('  -Inf', fmt(NEG_INF))


    def test_precision_0(self):
        fmt = EFloatFormatter(2, 0)
        self.assertEqual(7, fmt.width)
        self.assertEqual(' 0.E+00', fmt(            0.0))
        self.assertEqual(' 1.E+00', fmt(            1.0))
        self.assertEqual('-1.E+00', fmt(           -1.0))
        self.assertEqual(' 5.E-01', fmt(            0.500001))
        self.assertEqual('-5.E-01', fmt(           -0.500001))
        self.assertEqual('-5.E-01', fmt(           -0.4999))
        self.assertEqual('-1.E+00', fmt(           -0.995001))
        self.assertEqual('-1.E+00', fmt(           -0.999501))
        self.assertEqual(' 1.E+03', fmt(         1000.0))
        self.assertEqual('-1.E+03', fmt(        -1000.0))
        self.assertEqual(' 1.E+11', fmt( 123456789012))
        self.assertEqual('-1.E+11', fmt(-123456789012))
        self.assertEqual(' 2.E+11', fmt( 150000000001))
        self.assertEqual('-2.E+11', fmt(-150000000001))
        self.assertEqual(' 1.E-13', fmt(            0.0000000000001234))
        self.assertEqual('-1.E-13', fmt(           -0.0000000000001234))
        self.assertEqual(' 1.E+99', fmt(            1e+99))
        self.assertEqual('-1.E+99', fmt(           -1e+99))
        self.assertEqual('#######', fmt(            9.50001e+99))
        self.assertEqual('#######', fmt(           -9.50001e+99))
        self.assertEqual('    NaN', fmt(NAN))
        self.assertEqual('    Inf', fmt(POS_INF))
        self.assertEqual('   -Inf', fmt(NEG_INF))


    def test_sign_plus(self):
        fmt = EFloatFormatter(2, 2, sign="+")
        self.assertEqual(9, fmt.width)
        self.assertEqual('+0.00E+00', fmt(            0.0))
        self.assertEqual('+1.00E+00', fmt(            1.0))
        self.assertEqual('-1.00E+00', fmt(           -1.0))
        self.assertEqual('+9.95E-01', fmt(            0.995001))
        self.assertEqual('+1.00E+00', fmt(            0.999501))
        self.assertEqual('-9.90E-01', fmt(           -0.99))
        self.assertEqual('+1.00E+03', fmt(         1000.0))
        self.assertEqual('-1.00E+03', fmt(        -1000.0))
        self.assertEqual('+1.23E+11', fmt( 123456789012))
        self.assertEqual('-1.23E+11', fmt(-123456789012))
        self.assertEqual('+1.24E+11', fmt( 123556789012))
        self.assertEqual('-1.24E+11', fmt(-123556789012))
        self.assertEqual('+9.99E+99', fmt(            9.99e+99))
        self.assertEqual('-9.99E+99', fmt(           -9.99e+99))
        self.assertEqual('+1.00E-99', fmt(            1.00e-99))
        self.assertEqual('-1.00E-99', fmt(           -1.00e-99))
        self.assertEqual('      NaN', fmt(NAN))
        self.assertEqual('     +Inf', fmt(POS_INF))
        self.assertEqual('     -Inf', fmt(NEG_INF))


    def test_sign_none(self):
        fmt = EFloatFormatter(2, 2, sign=None)
        self.assertEqual(8, fmt.width)
        self.assertEqual('0.00E+00', fmt(            0.0))
        self.assertEqual('1.00E+00', fmt(            1.0))
        self.assertEqual('########', fmt(           -1.0))
        self.assertEqual('9.95E-01', fmt(            0.995001))
        self.assertEqual('1.00E+00', fmt(            0.999501))
        self.assertEqual('########', fmt(           -0.99))
        self.assertEqual('1.00E+03', fmt(         1000.0))
        self.assertEqual('########', fmt(        -1000.0))
        self.assertEqual('1.23E+11', fmt( 123456789012))
        self.assertEqual('########', fmt(-123456789012))
        self.assertEqual('1.24E+11', fmt( 123556789012))
        self.assertEqual('########', fmt(-123556789012))
        self.assertEqual('9.99E+99', fmt(            9.99e+99))
        self.assertEqual('########', fmt(           -9.99e+99))
        self.assertEqual('1.00E-99', fmt(            1.00e-99))
        self.assertEqual('########', fmt(           -1.00e-99))
        self.assertEqual('     NaN', fmt(NAN))
        self.assertEqual('     Inf', fmt(POS_INF))
        self.assertEqual('########', fmt(NEG_INF))


    def test_point(self):
        fmt = EFloatFormatter(2, 2, point=",")
        self.assertEqual(9, fmt.width)
        self.assertEqual(' 0,00E+00', fmt(    0.0))
        self.assertEqual(' 1,00E+00', fmt(    1.0))
        self.assertEqual('-1,00E+00', fmt(   -1.0))
        self.assertEqual(' 1,00E+03', fmt( 1000.0))
        self.assertEqual('-1,00E+03', fmt(-1000.0))
        self.assertEqual(' 9,99E+99', fmt(    9.99e+99))
        self.assertEqual('-9,99E+99', fmt(   -9.99e+99))


    def test_exp(self):
        fmt = EFloatFormatter(2, 2, exp=" e")
        self.assertEqual(10, fmt.width)
        self.assertEqual(' 0.00 e+00', fmt(      0.0))
        self.assertEqual(' 1.00 e+00', fmt(      1.0))
        self.assertEqual('-1.00 e+00', fmt(     -1.0))
        self.assertEqual(' 1.00 e+03', fmt( 1000.0))
        self.assertEqual('-1.00 e+03', fmt(-1000.0))
        self.assertEqual(' 9.99 e+99', fmt(      9.99e+99))
        self.assertEqual('-9.99 e+99', fmt(     -9.99e+99))


    def test_nan_str(self):
        fmt = EFloatFormatter(2, 2, nan_str="INVALID")
        self.assertEqual(9, fmt.width)
        self.assertEqual(' 0.00E+00', fmt(      0.0  ))
        self.assertEqual('-1.00E+04', fmt(  -9999.99 ))
        self.assertEqual('  INVALID', fmt(NAN))
        self.assertEqual('      Inf', fmt(POS_INF))
        self.assertEqual('     -Inf', fmt(NEG_INF))

        self.assertRaises(
            Exception, EFloatFormatter, 2, 2, nan_str="INVALID VALUE")


    def test_inf_str(self):
        fmt = EFloatFormatter(2, 3, inf_str="INFINITY")
        self.assertEqual(10, fmt.width)
        self.assertEqual(' 0.000E+00', fmt(      0.0  ))
        self.assertEqual('-1.000E+04', fmt(  -9999.99 ))
        self.assertEqual('       NaN', fmt(NAN))
        self.assertEqual('  INFINITY', fmt(POS_INF))
        self.assertEqual(' -INFINITY', fmt(NEG_INF))

        self.assertRaises(
            Exception,  EFloatFormatter, 4, 0, inf_str="WAY WAY TOO LARGE")



#-------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

