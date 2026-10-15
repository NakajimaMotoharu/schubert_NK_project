import ast
import unittest

import pg3450_current_outbox_publication_sources as role
import pg3452_current_outbox_publication_compile as compiler
import pg3454_current_outbox_publication_dispatch as dispatcher


class FiniteActualCandidatePublication(unittest.TestCase):
    def test_whole_namespace_current_candidate_data_and_phase_roles(self):
        values = role.sources()
        raw = '\n'.join(values.values())
        for marker in [role.CURRENT, role.production(), role.CURRENT_BOM, role.BEFORE,
                       role.BOOT, role.TOOLS, role.SAVE, role.ro.SAVE, role.ro.role.BOM,
                       '0.1.0-PG2802', '0.1.0-PG3420']:
            self.assertIn(marker, raw)
        self.assertNotIn('NORMAL_DAEMON_RELOAD', raw)
        self.assertNotIn('REGULAR_MORNING_UNIT_EXCHANGE', raw)

    def test_source_guard_stage_boot_and_actual_whole_abi(self):
        bom = role.candidate_bom()
        raw = compiler.compiler(bom) + dispatcher.source(bom)
        stage = dispatcher.stage(bom)
        ast.parse(stage)
        for marker in ['pg3448-current-outbox-ro-independent-post-v1', 'pg3436-frozen',
                       'pg3434-current-outbox-unused-tools-v1', 'pg3452-frozen', role.production(),
                       'program/characterization', 'pg3454-']:
            self.assertIn(marker, raw)
        for marker in [role.BOOT, '0.1.0-PG2802', role.TOOLS, dispatcher.REMOTE]:
            self.assertIn(marker, stage)
        for marker in [role.ro.role.old.BOOT, 'PG2512', 'pg2658-operation']:
            self.assertNotIn(marker, stage)
        self.assertEqual(1, dispatcher.source(bom).count('with management_gate('))

    def test_foreign_or_missing_bom_never_becomes_pending_authority(self):
        for bad in ['', None, 'a' * 64, role.CURRENT_BOM]:
            with self.assertRaises(ValueError):
                role.bind('not executed', bad)


if __name__ == '__main__':
    unittest.main()
