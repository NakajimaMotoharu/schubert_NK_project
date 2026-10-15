"""Independent whole namespace and no public-to-private scope inflation."""
import unittest
from pyflakes.api import check
from pg3232_legacy_negative_post import build


class PrivateWitness(unittest.TestCase):
    def test_closed_v4_source_and_live_syscall_witness(self):
        raw = 'HASHES={}\n' + build()
        self.assertEqual(0, check(raw, '<actual v4 syscall post>'))
        compile(raw, '<actual v4 syscall post>', 'exec')
        for literal in ["mutations==[]", "whole['privateSystemctlExecVerified']is True", "whole['publicBusScopeLimited']is True", "whole['syscallSha256']", "v['actualSystemctlShowExecs']>0", "v['unsafeSystemctlExecs']==0", "v['inetConnects']==0", "'syscall.private.log':syscalls", 'cohort-native-v4.exec', 'PG3230-LFACT-v4']:
            self.assertIn(literal, raw)
        for old in ['cohort-v3', 'cohort-native-v3', 'PG3222-LFACT', "mutations]==['StartUnit','StopUnit']"]:
            self.assertNotIn(old, raw)


if __name__ == '__main__':
    unittest.main()
