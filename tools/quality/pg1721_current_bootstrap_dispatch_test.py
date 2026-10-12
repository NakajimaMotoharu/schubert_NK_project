"""Independent current joins and exact one Bootstrap dispatch capability."""
import ast
import unittest
from pg1721_current_bootstrap_dispatch import source


class DispatchTest(unittest.TestCase):
    def test_current_actual_records_and_old_operations_absent(self):
        raw=source();ast.parse(raw)
        for expected in ['pg1720-frozen-v1.safe.json','pg1718-current-bootstrap-before-v1/manifest.safe.json',
                         'pg1701-new-source-done-receipt-v1.safe.json','pg1707-new-source-terminal-post-v1.safe.json',
                         'pg1721-verify-v1.exit','Pg1719BootstrapExisting','0.1.0-PG1638',
                         '3d69f5af-6bac-46b1-a540-7591c4a79a0d','pg1719-current-bootstrap-tools-v1']:
            self.assertIn(expected,raw)
        for old in ['PG932','pg986','pg983','pg963-stop-v1.exit','pg968-terminal-final-v1.exit','40ef6e894573d2ffab1d1732124960f9c98d5f97']:
            self.assertNotIn(old,raw)
        self.assertNotIn('MorningProcessMain',raw)


if __name__=='__main__':unittest.main()
