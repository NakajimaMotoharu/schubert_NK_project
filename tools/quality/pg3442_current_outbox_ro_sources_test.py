import ast
import unittest

import pg3442_current_outbox_ro_sources as ro
import pg3444_current_outbox_ro_compile as compiler


class CurrentReadOnlyRoles(unittest.TestCase):
    def test_all_roles_namespaces_and_historical_root_are_separate(self):
        values = ro.sources()
        self.assertEqual(18, len(values))
        raw = '\n'.join(values.values())
        for marker in [ro.TOOLS, ro.SAVE, ro.role.CURRENT, ro.role.SOURCE,
                       ro.role.CURRENT_BOM, ro.role.BOM, ro.role.BEFORE, ro.role.BOOT]:
            self.assertIn(marker, raw)
        self.assertEqual(ro.role.binding(ro.role.sources()['pg3434_parent_receipt.py']),
                         ro.role.binding(values['pg3442_parent_receipt.py']))
        for value in [ro.role.old.CURRENT, ro.role.old.SOURCE, ro.role.old.BOOT]:
            self.assertNotIn(value, raw)

    def test_ro_requires_fixed_bom_and_before(self):
        for value in [None, '', 'f' * 64, ro.role.CURRENT_BOM]:
            with self.assertRaises(ValueError):
                ro.sources(value)
        with self.assertRaises(ValueError):
            ro.sources(ro.role.BOM, 'f' * 64)

    def test_host_compile_uses_actual_unused_post_and_current_abi_only(self):
        raw = compiler.compiler()
        ast.parse(raw)
        for marker in ['pg3444-frozen-v1', 'pg3440-current-outbox-unused-independent-post-v1',
                       'pg3436-frozen-v1', 'pg3434-current-outbox-unused-tools-v1',
                       'pg2802-release-v1']:
            self.assertIn(marker, raw)
        for value in ['pg2664-operation', 'pg2659-frozen', 'pg2654-release', 'systemctl']:
            self.assertNotIn(value, raw)


if __name__ == '__main__':
    unittest.main()
