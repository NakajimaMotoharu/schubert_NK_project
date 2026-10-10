"""Assembly contract, independent of guest operation; no private values printed."""
import ast
import unittest
from pg1028_cold_handoff_preflight import payload


class Assembly(unittest.TestCase):
    def test_readonly_profile_is_current_and_no_signal_or_unit_mutation(self):
        raw = payload()
        ast.parse(raw)
        self.assertFalse(any(isinstance(n, ast.ImportFrom) and (n.module or '').startswith('pg') for n in ast.parse(raw).body))
        self.assertIn('OWNER_PID=3091;OWNER_BACKEND=0', raw)
        self.assertIn("ticks==835207", raw)
        self.assertIn('contract.all_client_sql(0)', raw)
        self.assertIn('h=contract.HeldInventory(str(RELEASE),records,0).open()', raw)
        self.assertIn('require(before==after)', raw)
        self.assertIn('actor_fd_locks', raw)
        for forbidden in ('pidfd_send_signal(', 'SIGTERM', 'os.kill(', "['systemctl','start'", "['systemctl','stop'", "['mount'", 'createStatement(', 'INSERT INTO', 'StartupPermitFiles.invalidate'):
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__': unittest.main()
