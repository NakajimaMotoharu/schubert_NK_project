"""No root aggregator or stale cache fallback; current selection remains explicit."""
import unittest
from pg1009_stream_selected_v3 import source,selected
class ReactorTest(unittest.TestCase):
    def test_explicit_same_source_dependencies_scope_and_new_namespace(self):
        s=source()
        self.assertFalse("'-am'"in s)
        self.assertTrue("'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch'"in s)
        self.assertEqual(4,len(selected.TESTS['batch']))
        self.assertTrue("'run':'PG1009-stream-selected-v3'"in s)
        self.assertTrue('40ef6e894573d2ffab1d1732124960f9c98d5f97'in s)
        self.assertFalse('PG1008-stream-selected-v2'in s)
if __name__=='__main__':unittest.main()
