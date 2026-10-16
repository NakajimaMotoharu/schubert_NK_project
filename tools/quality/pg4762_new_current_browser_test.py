"""Source-only transformation and preserved prerequisites; no Browser/login calls."""
import inspect
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg4762_new_current_browser_ready as ready
import pg4764_new_current_same_owner_browser as actual


class Browser(unittest.TestCase):
    def test_identity_only_oracle_literals_pins_and_twelve_cases(self):
        self.assertEqual('825e463334c43a5bc96f50db964df22e11758d1b',ready.SOURCE)
        self.assertIn('tools/quality/pg4762_new_current_browser_ready.py',ready.PINNED)
        for name in ready.shared.JAVA_INPUTS:
            raw=(ready.shared.ROOT/name).read_text()
            if name not in ready.shared.SHARED:
                self.assertEqual(1,raw.count(ready.shared.OLD));bound=raw.replace(ready.shared.OLD,ready.SOURCE)
                self.assertEqual(raw,bound.replace(ready.SOURCE,ready.shared.OLD))
        self.assertIn("['plannedCases']==12",inspect.getsource(ready.shared.require_ready))
        self.assertEqual(0,checkPath(ready.__file__));self.assertEqual(0,checkPath(actual.__file__))

    def test_no_execution_without_current_genuine_terminal(self):
        with patch.object(actual,'receipt',side_effect=ValueError('genuine current missing')):
            with self.assertRaisesRegex(ValueError,'genuine current missing'):actual.guard()
        main=inspect.getsource(actual.previous.main)
        self.assertLess(main.index('ready.require_ready()'),main.index('subprocess.run(command'))
        self.assertIn('before_socks==previous.previous.owned_socks()',main)


if __name__=='__main__':unittest.main()
