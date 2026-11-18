"""Metadata-only regression for BUG-3236. No Java or product test execution."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pgpt_closed_host_profile as profile


class ExpectedCasesTest(unittest.TestCase):
    def test_preserves_plain_and_formatter_split_declarations(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'Cases.java'
            path.write_text(
                'package fixture;\n'
                'class Cases {\n'
                '  @Test\n'
                '  void ordinaryCase() {}\n'
                '  @Test\n'
                '  void\n'
                '      formattedCase() {}\n'
                '}\n',
                encoding='utf-8',
            )
            config = {'testSources': [{'path': path.name, 'tests': 2}], 'expectedTests': 2}
            with patch.object(profile, 'R', root):
                self.assertEqual(profile.expected_cases(config), [
                    {'classname': 'fixture.Cases', 'name': 'ordinaryCase()'},
                    {'classname': 'fixture.Cases', 'name': 'formattedCase()'},
                ])
                config['testSources'][0]['tests'] = 1
                with self.assertRaisesRegex(ValueError, 'whole Test method count changed'):
                    profile.expected_cases(config)
