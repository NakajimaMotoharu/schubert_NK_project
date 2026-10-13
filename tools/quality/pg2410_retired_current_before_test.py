import unittest
from pg2040_fresh_normal_warning_terminal_post import SEALS
from pg2410_retired_current_before import payload, entry, SLOT


class Before(unittest.TestCase):
    def test_complete_current_retired_and_backup_independent_scope(self):
        raw = payload({k:'a'*64 for k in SEALS})
        for v in ['same_except_runtime','prior_equal','pg2368-current-resume-full-seal-v1',
                  'qualify_backup()', "require(after['native']==native)",
                  'before.private.json','native-before.private.json','runtimeAlreadyRetired',
                  'all24UnchangedTwice','allClientAdvisoryFlock0']:
            self.assertIn(v,raw)
        for v in ['StartUnit(', 'StopUnit(', 'daemon-reload']:
            self.assertNotIn(v,raw)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])
        self.assertIs(payload,entry().__globals__['payload'])


if __name__ == '__main__':
    unittest.main()
