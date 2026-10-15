"""Fixed ownership, no fixture signal before genuine VM/disk down proof."""
import copy
import unittest
from pg3242_negative_fixture_forward_close import qualify


class OwnedForward(unittest.TestCase):
    def test_every_post_and_owner_must_match_before_signal(self):
        post = {'actualExit': 0, 'fixtureQemuGone': True, 'fixtureDiskNoOpeners': True, 'primaryUntouched': True}
        p = {'pid': 171540}; c = {'pid': 171602, 'ppid': 171540, 'exe': '/usr/bin/ssh'}
        fixed = {'port': 22224, 'guestKeyTransferred': False, 'parent': p, 'child': c}
        qualify(post, fixed, p, c)
        for key in post:
            bad = {**post, key: 1 if key == 'actualExit' else False}
            with self.assertRaises(ValueError, msg=key): qualify(bad, fixed, p, c)
        for key in fixed:
            bad = {**fixed, key: None}
            with self.assertRaises(ValueError, msg=key): qualify(post, bad, p, c)
        for key in c:
            wrong = copy.deepcopy(c); wrong[key] = 'foreign'
            with self.assertRaises(ValueError, msg=key): qualify(post, fixed, p, wrong)


if __name__ == '__main__':
    unittest.main()
