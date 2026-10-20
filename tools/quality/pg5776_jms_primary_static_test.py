"""Strict source delta model controls, not PT/coverage of Production paths."""
import unittest
from pg5776_jms_primary_static import expected_source,PATHS


class MinimalIdentityDelta(unittest.TestCase):
    def test_exact_three_guards_no_other_edits(self):
        paths=list(PATHS)
        before='prefix\n      isolationFailure.addSuppressed(protocolFailure);\n      failure.addSuppressed(rollbackFailure);\nsuffix'
        actual=expected_source(paths[0],before)
        self.assertEqual(2,actual.count('if ('))
        self.assertEqual(before,actual.replace('      if (isolationFailure != protocolFailure) {\n        isolationFailure.addSuppressed(protocolFailure);\n      }','      isolationFailure.addSuppressed(protocolFailure);').replace('      if (failure != rollbackFailure) {\n        failure.addSuppressed(rollbackFailure);\n      }','      failure.addSuppressed(rollbackFailure);'))
        self.assertEqual(1,expected_source(paths[1],'      isolationFailure.addSuppressed(protocolFailure);').count('if ('))
        with self.assertRaisesRegex(ValueError,'one exact'):expected_source(paths[0],before+before)
        with self.assertRaisesRegex(ValueError,'one exact'):expected_source(paths[0],before.replace('rollbackFailure','other'))


if __name__=='__main__':unittest.main()
