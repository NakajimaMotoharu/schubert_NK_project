import ast
import unittest
from pg2170_normal_publication_sources import sources


class Publication(unittest.TestCase):
    def test_actual_whole_normal_generation_roles_and_no_unit_replay(self):
        v=sources();raw='\n'.join(v.values())
        for text in ['3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','0fd734195b4d5338f6b7e860e087cce561d49562','0.1.0-PG2126','0.1.0-PG1846','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7','2026-10-13T03:35:44.330028Z','PG2170_INPUT_CLOSURE_READY','genuineParentNormalWarningOriginal=true']:self.assertIn(text,raw)
        for text in ['0.1.0-PG1638','REGULAR_MORNING_UNIT_EXCHANGE','NORMAL_DAEMON_RELOAD','unit_exchange.exchange','managerFailureRetained=true']:self.assertNotIn(text,raw)
        java=v['Pg2170OrdinaryPublication.java']
        self.assertIn('Outcome.WARNING',java);self.assertIn('FINITE_ORDINARY_PUBLICATION',java)
        self.assertIn('CANONICAL_INVALID',java)
        helper={};exec(compile(v['pg2170_native_owned_stop.py'],'<actual helper exports>','exec'),helper)
        attrs={n.attr for n in ast.walk(ast.parse(v['pg2170_native_refs.py']))if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='h'}
        self.assertTrue(attrs<=helper.keys())
        from pyflakes.api import check
        for n,body in v.items():
            if n.endswith('.py'):
                context="BUNDLE_HASH='realbundlepending'\n"if n=='pg2170_native_refs.py'else''
                self.assertEqual(check(context+body,n),0)


if __name__=='__main__':unittest.main()
