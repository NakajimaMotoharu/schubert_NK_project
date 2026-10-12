"""Actual independent whole source and proper placement proof, no old stop replay."""
import json
import unittest
from pg1866_warning_direct_unused_post import payload,W,SLOT


class Whole(unittest.TestCase):
    def test_current_oldsource_and_real_newcandidate_inputs_whole_conditions(self):
        raw=payload(json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes()))
        for literal in ['pg1864-warning-unused-placement-v1',SLOT,'0.1.0-PG1846','ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7','managerFailureRetained=true','len(sums)==187','1928d1bd0d8aa0f00d3b1e4bb120e78c0bc710a9d5a219d89b3853d4929a11d6']:
            self.assertIn(literal,raw)
        self.assertNotIn('genuineParentDone=true',raw)
        self.assertNotIn('ResetFailedUnit',raw);self.assertNotIn('StopUnit',raw)


if __name__=='__main__':unittest.main()
