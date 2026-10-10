import ast
import unittest
from pg1031_cold_handoff_preflight_v4 import payload


class Retry(unittest.TestCase):
    def test_exact_canonical_checksum_required_not_generic_extra(self):
        raw = payload()
        ast.parse(raw)
        self.assertIn("records.append({'path':'SHA256SUMS','size':len(canonical),'sha256':CHECKSUM_HASH})", raw)
        self.assertIn('require(hashlib.sha256(canonical).hexdigest()==CHECKSUM_HASH)', raw)
        self.assertIn('h=contract.HeldInventory(str(RELEASE),records,0).open()', raw)
        self.assertIn('PG1031_REFUSED', raw)
        self.assertNotIn('pg1030-cold-handoff-preflight-v3', raw)
        self.assertNotIn('pidfd_send_signal(', raw)


if __name__ == '__main__': unittest.main()
