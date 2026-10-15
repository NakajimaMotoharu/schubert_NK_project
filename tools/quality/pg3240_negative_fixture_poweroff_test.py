"""Separate once-only normal request and read-only down proof, no broad signal."""
import unittest
from pyflakes.api import check, checkPath
import pg3240_negative_fixture_poweroff as shutdown


class FixturePoweroff(unittest.TestCase):
    def test_every_complete_namespace_and_no_forced_or_primary_stop(self):
        self.assertEqual(0, checkPath(shutdown.__file__))
        for prefix, raw in [('HASHES={}\n', shutdown.GUEST), ('FIXTURE={}\n', shutdown.BEFORE), ('PRIOR={}\n', shutdown.AFTER)]:
            self.assertEqual(0, check(prefix + raw, '<whole shutdown phase>'))
            compile(prefix + raw, '<whole shutdown phase>', 'exec')
            for forbidden in ['SIGKILL', 'SIGTERM', 'virsh destroy', 'rm -rf', 'systemctl reboot']:
                self.assertNotIn(forbidden, raw)
        self.assertIn("['systemctl','poweroff','--no-block']", shutdown.GUEST)
        self.assertNotIn('poweroff', shutdown.AFTER.lower().replace('normalguestpowerdowninnewserial', ''))
        for guard in ['not Path(\'/proc/445092\').exists()', 'v.primary()', 'openers==[]', "len(info)==4", "b'Power down'", "v.chain(v.reference(),False)"]:
            self.assertIn(guard, shutdown.AFTER)


if __name__ == '__main__':
    unittest.main()
