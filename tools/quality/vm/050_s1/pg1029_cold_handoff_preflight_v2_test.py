import ast
import unittest
from pg1029_cold_handoff_preflight_v2 import payload


class Retry(unittest.TestCase):
    def test_kernel_cardinality_retained_only_fd_alias_normalized(self):
        raw = payload()
        ast.parse(raw)
        self.assertIn("owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),lockmeta,3091)", raw)
        self.assertIn('owned_flocks(contract.fd_alias_records(actor_fd_locks),lockmeta,3091)', raw)
        self.assertIn('PG1029_REFUSED phase=', raw)
        self.assertNotIn('pg1028-cold-handoff-preflight-v1', raw)
        for forbidden in ('pidfd_send_signal(', 'SIGTERM', 'os.kill(', "['systemctl','start'", "['systemctl','stop'", "['mount'"):
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__': unittest.main()
