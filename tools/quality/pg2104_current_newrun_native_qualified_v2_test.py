"""Actual server and compiled entry, current Main/CRC/session inputs and output namespace disjoint."""
import inspect
import unittest
from pyflakes.api import check
from pg2104_current_newrun_native_qualified_v2 import source,server,entry


class Qualification(unittest.TestCase):
    def test_actual_code_and_transport_fixed_namespace(self):
        transport=source();code=server();compiled=entry()
        for marker in ['PG2104-native-v1','PG2104-native-input.tar','PG1844-six-v1','productionSource','3618','inspectorTwoPointsSameSessionAndOrdered']:
            self.assertTrue(marker in code,marker)
        self.assertTrue('pg2100-current-newrun-native-catalog-v1'in transport)
        self.assertTrue('pg2104-current-newrun-native-qualified-v1'in transport)
        self.assertEqual(code,compiled.__globals__['CODE'])
        actual='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="fixed"\n'+inspect.getsource(compiled.__globals__['coordinates'])+'\n'+code
        self.assertEqual(0,check(actual,'<actual complete matched server qualifier>'))
        for old in ['PG2048-native-v1','PG2044-native-v1','PG2102-native-v1']:
            self.assertFalse(old in code,old)


if __name__=='__main__':unittest.main()
