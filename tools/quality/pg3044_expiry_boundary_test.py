"""Independent six-name inventory against the already executed literal XML; no rerun."""
import json
from pathlib import Path
import re
import unittest
from pg3044_expiry_boundary_selected import server, TEST
from pg1446_current_cold_stage import W


class Inventory(unittest.TestCase):
    def test_literal_six_methods_and_actual_result(self):
        expected = {'ereq3042001PriorBoundaryAndNullContractNeverAuthorizeCleanup', 'ereq3042002EveryRequiredFieldAndPriorPrecisionRejectsWithErasure', 'wire200001ForeignAnchorCutoffIsExplicitAndOldGrammarIsNotReinterpreted', 'independentGoldenFullHandleAndInputErasure', 'fixedCanonicalNegativeMatrixAndCleanupMutualRejection', 'ereq005SkipRequiresSeparateCompleteCanonicalOriginalAndErasesEveryRejectedInput'}
        actual = set(re.findall(r'@Test\s+void\s+(\w+)\(', Path(TEST).read_text()))
        self.assertEqual(expected, actual)
        result = json.loads((W / 'pg3044-expiry-boundary-selected-v1/manifest.safe.json').read_bytes())
        self.assertEqual(0, result['actualExit'])
        self.assertEqual(6, result['tests'])
        self.assertEqual(0, result['FESAbortedNotRun'])
        self.assertEqual(0, result['vmActions'])
        self.assertFalse(result['targetClassFour100'])
        raw = server()
        self.assertIn('source-full-PG3026', raw)
        self.assertIn('platform.ExpiryWorkerRequestTest', raw)
        self.assertNotIn('seven', raw)


if __name__ == '__main__':
    unittest.main()
