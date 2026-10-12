"""Actual direct profile and immutable two-source input basenames."""
import unittest
from pg1851_warning_signed_unused_dispatch import source,STAGE


class Dispatch(unittest.TestCase):
    def test_actual_fixed_names_all_inputs_source_capture_and_separate_oldrelease(self):
        raw=source()
        for v in ['pg1850-frozen-v1.safe.json','pg1849-warning-completed-current-before-v1','pg1851-warning-release-v1.tar','pg1846-manifest-v1.sig','Pg1848CurrentIdentityTest','Pg1848InputBoundaryTest','0.1.0-PG1638/operations/batch.jar','test ! -e /opt/schubert-nk/releases/0.1.0-PG1846','completedObservedHead','sourceQualified']:
            self.assertIn(v,raw)
        self.assertIn('pg1848-warning-unused-tools-v1',STAGE)
        for v in ['Pg1640','pg1683','__NEW_RELEASE__','0.1.0-PG1544']:
            self.assertNotIn(v,raw)


if __name__=='__main__':unittest.main()
