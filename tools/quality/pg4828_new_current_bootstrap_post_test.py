import ast
import unittest
import pg4828_new_current_bootstrap_post as role


class IndependentPost(unittest.TestCase):
    def test_actual_current_binding_and_scope(self):
        raw=role.payload();ast.parse(raw)
        self.assertIn(role.role.BASELINE,raw)
        self.assertIn('boot_before[\'rows\']==boot_after[\'rows\']==after[\'rows\']',raw)
        self.assertIn("CONTRACT['same_terminal_cohort']",raw)
        self.assertIn("CONTRACT['native_tree']",raw)
        self.assertIn("'allResources0':True",raw)
        self.assertIn("save=base/'pg4828-new-current-bootstrap-post-v1'",raw)
        self.assertIn('67108864',raw)
        self.assertLess(raw.index("terminal=boot_after['units'][bootstrap]"),raw.index('current_bootstrap=show'))
        self.assertLess(raw.index('refs.append(u)'),raw.index('current_bootstrap=show'))
        self.assertLess(raw.index('current_bootstrap=show'),raw.index('def snapshot():'))
        for bad in ('systemctl start','reset-failed','pg1730-execute','pg1727-bootstrap-recovery'):
            self.assertNotIn(bad,raw)

    def test_original_whole_functions_preserved(self):
        raw=role.payload();before=(role.role.W/role.role.before.SLOT/'payload.private.py').read_text()
        funcs=lambda text:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
        old=funcs(before);now=funcs(raw)
        for name,value in old.items():self.assertEqual(value,now[name],name)


if __name__=='__main__':unittest.main()
