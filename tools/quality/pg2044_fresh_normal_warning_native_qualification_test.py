"""Current full candidate/MainCRC no old source import; Inspector single-session two points."""
import unittest
from pg2044_fresh_normal_warning_native_qualification import source,server


class Qualification(unittest.TestCase):
    def test_actual_current_snapshot_transport_and_crc_session_constraints(self):
        transport=source();raw=server()
        self.assertTrue('pg1845-warning-unit-full-qualified-v1'in transport)
        self.assertTrue('pg2042-fresh-normal-warning-native-catalog-v1'in transport)
        self.assertTrue('PG1844'in raw and 'qualified1844Tests'in raw)
        self.assertTrue('2741c4546afad6c1e8b6efbd53dfb58144edf7bb'not in raw)
        self.assertTrue('0fd734195b4d5338f6b7e860e087cce561d49562'in raw)
        self.assertTrue('inspectorTwoPointsSameSessionAndOrdered'in raw)
        self.assertTrue('classByteMismatch' in raw and 'distinctSessionIdsMeasured'in raw)


if __name__=='__main__':unittest.main()
