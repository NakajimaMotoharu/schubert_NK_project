import re
import unittest
import pg5184_environment_selected as role
import pg5180_backup_public as common


class EnvironmentScope(unittest.TestCase):
    def test_revalidated_public_case_ids_do_not_claim_new_work_or_omit_metadata(self):
        ids=common.revalidated_case_ids()
        self.assertEqual(len(ids),3)
        self.assertEqual({value['testId'] for value in ids.values()},
                         {'PT-OPS-CHILDFD-009','PT-OPS-CHILDFD-010','PT-NEXPORT193-META001'})
        self.assertTrue(all(value['newIndependentCase'] and value['newInThisChange'] is False for value in ids.values()))

    def test_all_environment_suites_and_case_inventory_are_exact_without_probe_counting(self):
        counts={}
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        for name in role.ENVIRONMENT:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),raw.count('@Test'))
            self.assertEqual(len(set(methods)),len(methods))
            counts[name.rpartition('.')[2]]=len(methods)
        self.assertEqual(counts,{'InspectorEnvironmentFilesTest':10,
          'InspectorEnvironmentReaderTest':8,'InspectorEnvironmentPublisherTest':13})
        self.assertEqual(sum(counts.values()),31)
        self.assertEqual(len(role.extra_suites()),50)

    def test_only_declared_three_outer_and_four_debug_candidate_families_added(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),9)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),10)
        self.assertIn('batch:dev/codex/schubert/nk/batch/file/InspectorEnvironmentFiles.class',role.selected.EXTRA_CHANGED)


if __name__=='__main__':unittest.main()
