import unittest
from pg5812_rollback_current_public import reader_source


class CurrentArtifactBindingTest(unittest.TestCase):
    def test_only_current54_original_xml_and_explicit_static_reauth(self):
        raw=reader_source()
        self.assertIn('pg5800-rollback-selected54-v5',raw)
        self.assertIn('PG5810-rollback-static-reauth-v1',raw)
        self.assertNotIn('selected54-v4',raw)
        self.assertNotIn('subprocess',raw)
        self.assertNotIn('lan_server',raw)


if __name__=='__main__':unittest.main()
