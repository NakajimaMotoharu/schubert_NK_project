import re
import unittest
import pg5200_morning_owner_selected as role


class MorningOwnerScope(unittest.TestCase):
    def test_existing_seven_plus_four_new_independent_cases(self):
        file=role.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupRequestPublicationTest.java'
        raw=file.read_text();cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
        self.assertEqual(len(cases),11)
        self.assertEqual(len(set(cases)),11)
        self.assertEqual(sum(name.startswith(('mbpub007','mbpub008','mbpub009','mbpub010')) for name in cases),4)
        self.assertEqual(len(role.extra_suites()),54)


if __name__=='__main__':unittest.main()
