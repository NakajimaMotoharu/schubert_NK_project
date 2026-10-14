import unittest
from pyflakes.api import check
import pg2641_wire_oracle_full_qualified as full
import pg2642_wire_oracle_native_qualified as native


class OracleIntegrationQualification(unittest.TestCase):
    def test_full_consumer_counts_static_physical(self):
        raw = full.server()
        self.assertEqual(0, check(raw, '<full independent namespace>'))
        for marker in ['PG2640', '3664', "'protocol':(82,17,174)", '540', '1643']:
            self.assertIn(marker, raw)
        self.assertNotIn("'protocol':(81,17,174)", raw)

    def test_byte_bridge_never_recaptures_vm(self):
        raw = native.server()
        for marker in ['source-full-PG2510', 'source-full-PG2640', 'identical_main==1643', 'images[0]==images[1]', '3664']:
            self.assertIn(marker, raw)
        self.assertNotIn('SSH+', native.source())
        self.assertIn('pg2641-wire-oracle-full-qualified-v1', native.source())

    def test_transport_whole_supplied_namespace(self):
        entry = native.entry()
        supplied = '\n'.join(name + '=None' for name in entry.__globals__ if name.isidentifier())
        self.assertEqual(0, check(supplied + '\n' + native.source(), '<whole supplied transport>'))


if __name__ == '__main__':
    unittest.main()
