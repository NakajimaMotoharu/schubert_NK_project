"""Independent no-primary-mutation, one readonly chain and isolated port/boot oracle."""
import copy
import os
import unittest
import pg3210_legacy_negative_vm as fixture


class NegativeVm(unittest.TestCase):
    def test_primary_owner_and_every_backing_are_exact_readonly(self):
        expected = dict(fixture.PRIMARY)
        modes = {str(p): os.O_RDONLY for p in fixture.CHAIN}
        self.assertEqual(expected, fixture.qualify_primary(expected, modes, [4599]))
        for key in expected:
            bad = copy.deepcopy(expected); bad[key] = None
            with self.assertRaises(ValueError):
                fixture.qualify_primary(bad, modes, [4599])
        for path in modes:
            for wrong in [True, os.O_WRONLY, os.O_RDWR]:
                with self.assertRaises(ValueError):
                    fixture.qualify_primary(expected, {**modes, path: wrong}, [4599])
        for bad in [[], [4599, 6000], [6000]]:
            with self.assertRaises(ValueError):
                fixture.qualify_primary(expected, modes, bad)

    def test_new_child_argv_has_no_current_active_disk_or_old_port(self):
        args = fixture.arguments(); text = ' '.join(args)
        self.assertTrue('pg3210-legacy-negative-v1/active.qcow2' in text)
        self.assertFalse('pg2810-network-resume-cold-v1' in text)
        self.assertFalse('22222-:22' in text)
        self.assertTrue('restrict=on,hostfwd=tcp:127.0.0.1:22224-:22' in text)
        self.assertEqual('4096', args[args.index('-m') + 1])
        self.assertEqual('2', args[args.index('-smp') + 1])
        self.assertEqual(fixture.original.APPEND, args[args.index('-append') + 1])
        self.assertTrue('systemd.unit=basic.target' in text and 'systemd.mask=timers.target' in text)
        self.assertFalse('-loadvm' in args or '-incoming' in args)


if __name__ == '__main__':
    unittest.main()
