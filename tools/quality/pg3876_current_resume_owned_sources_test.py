"""Independent protected snapshot/oracle binding and closed graph namespaces, no guest actions."""
import ast
import unittest
import pg3876_current_resume_owned_sources as role
import pg3880_current_resume_owned_dispatch as dispatch
import pg3882_current_resume_owned_post as post


class ImmutableRoles(unittest.TestCase):
    def test_current_roles_never_rewrite_nested_history(self):
        nested="CHAIN={'old':'pg3822/Pg3822/pg3816','source':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2'}\n"
        raw="TOOLS='"+role.previous.TOOLS+"'\nORACLE="+repr(nested)+"\nGUARD="+repr('original pg3822 native source')+'\n'
        result=role.bind(raw);values={n.targets[0].id:ast.literal_eval(n.value)for n in ast.parse(result).body if isinstance(n,ast.Assign)}
        self.assertEqual(role.TOOLS,values['TOOLS']);self.assertEqual(nested,values['ORACLE']);self.assertEqual('original pg3822 native source',values['GUARD'])
        for key in ['context','emit','emit_receipt','sources']:self.assertIn(key,role.namespace())
        for key in ['stage','run_action','main']:self.assertIn(key,dispatch.namespace())
        for key in ['entry','emit','payload']:self.assertIn(key,post.namespace())
        self.assertIn('class Pg3876X',role.final_bind('class Pg3822X {}'))
        self.assertEqual(role.acceptance.TERM,role.current.TERM)
        self.assertEqual(role.composite.SLOT,role.current.SEAL)


if __name__=='__main__':unittest.main()
