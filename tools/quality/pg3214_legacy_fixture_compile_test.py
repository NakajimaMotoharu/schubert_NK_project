"""Full compiler namespace, independent closed seven-case IDs, no mixed internal jars."""
import re
import unittest
from pyflakes.api import check
from pg3214_legacy_fixture_compile import CODE, JAVA


class FixtureCompiler(unittest.TestCase):
    def test_closed_runtime_export_and_original_main_not_compiled(self):
        code = 'INPUT={}\nSERVER="server"\nREMOTE="transfer"\nSOURCE="source"\n' + CODE
        self.assertEqual(0, check(code, '<complete fixed fixture compiler>'))
        compile(code, '<isolated negative harness builder>', 'exec')
        for value in ['main==1643 and resource==79', "full['tests']==3694", "not str(p.relative_to(repo)).startswith('dev/codex/schubert/')", "p.name.startswith('NativeLegacyAdmissionNegative')", "'mainRecompiled':False", 'all(sha(entries[name])==value for name,value in before.items())']:
            self.assertTrue(value in code, value)

    def test_seven_exact_cases_require_os_ack_not_just_ioexception(self):
        raw = JAVA.read_text()
        self.assertEqual(['PT-OPS-LFACT' + str(i).zfill(3) for i in range(1, 8)], re.findall(r'"(PT-OPS-LFACT[0-9]{3})"', raw))
        for value in ['"BEGIN|" + test.id()', '"ARMED|" + test.id()', '"END|" + test.id()', '"ACCESSED|" + test.id()', '"COMPLETE|7"', '"SEALED|7"', 'forbiddenCallback()', 'context.recheck(root)', 'StandardOpenOption.CREATE_NEW']:
            self.assertTrue(value in raw, value)
        for forbidden in ['setAccessible', 'getDeclaredMethod', 'MorningProcessMain.main', 'systemctl start', 'System.getenv("PASSWORD")']:
            self.assertFalse(forbidden in raw, forbidden)


if __name__ == '__main__':
    unittest.main()
