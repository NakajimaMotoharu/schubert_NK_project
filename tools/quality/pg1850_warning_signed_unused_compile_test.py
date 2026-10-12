"""Actual compile source checks every generated helper with its own injected inputs."""
import unittest
from pg1850_warning_signed_unused_compile import compiler


class Freeze(unittest.TestCase):
    def test_exact_actual_candidate_current_sharedabi_and_every_java(self):
        raw=compiler()
        for v in ['pg1846-candidate-build-v1.safe.json','pg1849-warning-completed-current-before-v1','pg1834-frozen-v1.safe.json','pg1833-warning-owned-stop-tools-v1',"generated['pg1848_input_preflight.py'] = 'BUNDLE_HASH='","names = sorted(n for n in generated if n.endswith('.java'))",'Pg1848CurrentIdentityTest','Pg1848InputBoundaryTest','check(body']:
            self.assertIn(v,raw)
        for v in ['pg1544-release-v1','pg1610-frozen-v1','Pg1640','__NEW_PREFIX__']:
            self.assertNotIn(v,raw)


if __name__=='__main__':unittest.main()
