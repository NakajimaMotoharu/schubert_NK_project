import unittest
from pyflakes.api import check
import pg3466_outbox_current_live_binding as current


class SameIssuedRootIdentity(unittest.TestCase):
    def test_current_boot_release_and_prior_generation_rejection(self):
        raw = current.body()
        _, _, prior, _ = current.roles._binding_context()
        for marker in [current.roles.BOOT, 'PG3420', prior['run'], prior['activation']]:
            self.assertTrue(marker in raw, marker)
        self.assertNotIn('b2d6f605', raw)
        self.assertEqual(0, check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n' + raw, '<exact current Root>'))
        self.assertNotIn('systemctl\',\'start', raw)


if __name__ == '__main__':
    unittest.main()
