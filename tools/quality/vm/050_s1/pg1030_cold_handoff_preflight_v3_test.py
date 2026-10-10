import ast
import unittest
from pg1030_cold_handoff_preflight_v3 import payload


class Retry(unittest.TestCase):
    def test_masked_targets_and_ten_cold_gate_preserved_with_exact_os_classification(self):
        raw = payload()
        ast.parse(raw)
        self.assertIn("fields=={'LoadState':'masked','ActiveState':'inactive','SubState':'dead','Job':''}", raw)
        self.assertIn('contract.timer_path_classification(units,console)', raw)
        self.assertIn('require(before==after)', raw)
        self.assertIn('h=contract.HeldInventory(str(RELEASE),records,0).open()', raw)
        self.assertIn('PG1030_REFUSED', raw)
        self.assertNotIn('pg1029-cold-handoff-preflight-v2', raw)
        for forbidden in ('pidfd_send_signal(', 'SIGTERM', 'os.kill(', "['systemctl','start'", "['systemctl','stop'", "['mount'"):
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__': unittest.main()
