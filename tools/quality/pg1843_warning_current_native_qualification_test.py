"""Input source/count separation and actual session equality/time order gates."""
import unittest
from pg1843_warning_current_native_qualification import source,server


class Native(unittest.TestCase):
    def test_full3618_never_old3596_and_not_candidate_acceptance(self):
        transport=source();actual=server()
        self.assertIn("len(catalog['selected'])!=10",transport)
        self.assertIn('pg1756-boundary-full-qualified-v1',transport)
        self.assertIn('qualify_snapshot()',transport)
        self.assertIn('source-full-PG1755',actual);self.assertIn("full['tests']==3618",actual)
        self.assertNotIn('PG1633',actual);self.assertNotIn('==3596',actual)
        self.assertIn("early['dumpMs']<=closed['dumpMs']",actual)
        self.assertIn("closed['sessionIdSha256']==early['sessionIdSha256']",actual)
        self.assertIn("'notDeployedUnitCandidateAccepted':False",actual)


if __name__=='__main__':unittest.main()
