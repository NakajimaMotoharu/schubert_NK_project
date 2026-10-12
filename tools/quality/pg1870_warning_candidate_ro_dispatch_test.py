"""Direct stage/consumer path and whole readonly post capabilities."""
import inspect
import json
import unittest
from pg1870_warning_candidate_ro_dispatch import main,STAGE,REMOTE
from pg1871_warning_candidate_ro_post import payload,prior


class Entry(unittest.TestCase):
    def test_actual_closure_stage_and_direct_RO_path(self):
        raw=inspect.getsource(main)
        self.assertIn(REMOTE,STAGE);self.assertIn('pg1868-frozen-v1.safe.json',raw)
        self.assertIn("CLASS+' prepare-ro'",raw);self.assertIn('with management_gate',raw)
        post=payload(json.loads((prior.W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes()))
        self.assertIn("'ro'in mounts and 'rw'not in mounts",post)
        self.assertIn('pg1869-warning-candidate-host-ro-v1',post)
        self.assertIn('managerFailureRetained=true',post)
        self.assertNotIn('StartUnit',post);self.assertNotIn('ResetFailedUnit',post)


if __name__=='__main__':unittest.main()
