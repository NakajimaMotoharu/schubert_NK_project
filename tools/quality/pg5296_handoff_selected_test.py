import re
import subprocess
import unittest
import pg5296_handoff_selected as role

PATH='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/FactoryResourceScopeTest.java'
PRIOR='6f8d42065ce19f79edc8e54dd99f991eda1a06a4'
METHODS=['factory013CompleteOwnerTransfersWithoutClosingAndKeepsNarrowType',
    'factory014HandoffPortsAndFactoryFailuresNeverAcceptAnOwner',
    'factory015IncompleteAssemblyMatchesIndependentThreeByFourGolden',
    'factory016NullCompleteOwnerIsReleasedWithSanitizedCompoundFailure',
    'factory017RepeatedAndAlreadySuppressedFailuresKeepIndependentPriority',
    'factory018ParallelCompleteOwnersNeverShareTransferState']


class HandoffScope(unittest.TestCase):
    def test_old_twelve_test_bodies_unchanged_and_new_six_explicit(self):
        root=role.selected.ROOT;raw=(root/PATH).read_text()
        old=subprocess.check_output(['git','show',PRIOR+':'+PATH],cwd=root,text=True)
        self.assertEqual(old[old.index('  @Test'):old.index('  private static String narrowStorageType')].rstrip(),
                         raw[raw.index('  @Test'):raw.index('  @Test\n  void factory013')].rstrip())
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
        self.assertEqual(len(methods),18)
        self.assertEqual(methods[12:],METHODS)
        self.assertIn('String[] winners = {"SSRE", "RRRR", "EEEE"};',raw)
        self.assertIn('String[] suppressed = {"0000", "0111", "0111"};',raw)

    def test_existing_suite_and_main_scope_only(self):
        role.configure()
        self.assertEqual(len(role.selected.storage_suites()),25)
        self.assertEqual(len(role.extra_suites()),93)
        self.assertEqual(len(role.selected.EXTRA_CHANGED),48)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),148)


if __name__=='__main__':unittest.main()
