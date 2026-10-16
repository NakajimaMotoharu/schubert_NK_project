"""Literal collision reproducer and complete actual continuation namespace; no operations."""
import ast
import builtins
import symtable
import unittest
from pyflakes.api import checkPath
import pg4806_new_current_owned_continue as target


class Continuation(unittest.TestCase):
    def fixture(self):return "CHAIN={'historical':'old-raw'}\nORACLE='read old-raw exactly'\nGUARD='old-raw negative'\nRAW_SAVE=BASE/'old-raw';require(not exists(RAW_SAVE))\nSAVE=BASE/'old';require(not exists(SAVE))\n"

    def test_literal_pre_fix_collision_and_both_new_output_roles(self):
        original=self.fixture();old=target.previous.rename_output(original,'old','fresh')
        self.assertIn("RAW_SAVE=BASE/'old-raw'",old)
        new=target.rename_output(original,'old','fresh')
        self.assertIn("RAW_SAVE=BASE/'fresh-raw'",new);self.assertIn("SAVE = BASE / 'fresh'",new)
        self.assertEqual(target.capsules(original),target.capsules(new))
        for raw in [original.replace("BASE/'old-raw'","BASE/'foreign'"),original.replace('RAW_SAVE=','OTHER='),original+"RAW_SAVE=BASE/'old-raw'\n"]:
            with self.assertRaises(ValueError):target.rename_output(raw,'old','fresh')

    def test_complete_existing_stage_new_once_namespace_and_absent_guest_guard(self):
        ns=target.runtime();raw=target.run_source()
        self.assertEqual('825e463334c43a5bc96f50db964df22e11758d1b',ns['SOURCE'])
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg4772-new-current-owned-tools-v1',ns['GUEST'])
        self.assertIn('pg4776-stage-v1.exit',raw);self.assertIn("base = W / ('pg4806-'",raw)
        self.assertIn('pg4809-newboot-pre-stop-full-v1',raw);self.assertIn('pg4807-parent-two-source',raw)
        self.assertIn("os.path.lexists('/var/lib/pgpt-s1-preservation/pg4772-native-stop-v1')",ns['PARENT_PREQUAL'])
        function=next(c for c in symtable.symtable(raw,'<actual new runtime>','exec').get_children()if c.get_name()=='run_action')
        missing=[s.get_name()for s in function.get_symbols()if s.is_global()and s.is_referenced()and s.get_name()not in ns and not hasattr(builtins,s.get_name())]
        self.assertEqual([],missing)
        with self.assertRaisesRegex(ValueError,'fixed action'):ns['run_action']('stage')
        self.assertEqual(0,checkPath(target.__file__));self.assertEqual(0,checkPath(__file__))
        ast.parse(raw)


if __name__=='__main__':unittest.main()
