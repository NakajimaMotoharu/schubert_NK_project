import unittest
from pyflakes.api import check
import pg6042_original3976_artifacts as t


class OriginalArtifactReaderTest(unittest.TestCase):
    def test_complete_read_only_namespace_and_case_duplicates(self):
        raw = t.emitted('0'*64)
        self.assertEqual(0, check(raw, '<original3976 artifact reader full definitions>'))
        for operation in ('Popen', 'subprocess', 'systemctl', 'qemu-system', 'sudo ', '--recover', '--resume'):
            self.assertNotIn(operation, raw)
        row = dict(module='api', **{'class': 'Example'}, caseNameSha256='a'*64)
        self.assertEqual({('api', 'Example', 'a'*64)}, t.expected_case_keys([row]))
        with self.assertRaises(ValueError):
            t.expected_case_keys([row, row])

    def test_actual_four_counters_missing_and_missed_never_accepted(self):
        modules = {name: dict(coverage={k: dict(covered=1, missed=0) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}) for name in t.MODULES}
        self.assertTrue(t.global_four100(modules))
        modules['api']['coverage']['BRANCH']['missed'] = 1
        self.assertFalse(t.global_four100(modules))
        del modules['api']['coverage']['METHOD']
        with self.assertRaises(ValueError):
            t.global_four100(modules)

    def test_only_declared_added_interface_and_owner_changes(self):
        owner = 'batch:dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient.class'
        interface = owner[:-6]+'$OperationEncoder.class'
        before = {str(i): 'a'*64 for i in range(1665)} | {owner: 'a'*64}
        after = dict(before) | {owner: 'b'*64, interface: 'c'*64}
        self.assertEqual(([owner], [interface], 1665), t.physical_difference(before, after, {owner}))
        after['0'] = 'd'*64
        with self.assertRaises(ValueError):
            t.physical_difference(before, after, {owner})


if __name__ == '__main__':
    unittest.main()
