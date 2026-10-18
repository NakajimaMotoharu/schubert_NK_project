"""Fresh process-generation checks, never weakening remote VM identity."""
import unittest
from pyflakes.api import checkPath
import pg4996_resume_connection as role


class ForwardIdentity(unittest.TestCase):
    def test_every_identity_field_and_exact_socket_owner_required(self):
        parent = {'pid': 11, 'ticks': 100, 'argvSha256': 'a' * 64}
        child = {'pid': 12, 'ticks': 101, 'argvSha256': 'b' * 64}
        value = {'localBoot': 'new', 'parent': parent, 'child': child,
                 'forward': '127.0.0.1:22222->server127.0.0.1:22222',
                 'miniOnly': True, 'guestPrivateKeyTransferred': False}
        listener = 'LISTEN users:(("ssh",pid=12,fd=4))'
        role.qualify(value, 'new', parent, child, listener)
        for changes in [dict(localBoot='old'), dict(parent={**parent, 'ticks': 99}),
                        dict(child={**child, 'argvSha256': 'c' * 64}), dict(miniOnly=1),
                        dict(guestPrivateKeyTransferred=0), dict(forward='other')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                role.qualify({**value, **changes}, 'new', parent, child, listener)
        with self.assertRaises(ValueError):
            role.qualify(value, 'new', parent, child, listener.replace('pid=12,', 'pid=112,'))
        self.assertEqual(0, checkPath(role.__file__))
        self.assertEqual(0, checkPath(__file__))


if __name__ == '__main__':
    unittest.main()
