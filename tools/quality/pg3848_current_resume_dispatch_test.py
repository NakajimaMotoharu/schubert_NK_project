"""Independent role/operation/immutable-oracle boundary checks, no VM actions."""
import ast
import unittest
import pg3848_current_resume_dispatch as dispatch
import pg3850_current_resume_post as post
import pg3844_current_resume_sources as role


class BindingTest(unittest.TestCase):
    def test_closed_new_only_dispatch(self):
        raw=dispatch.source();ast.parse(raw);ast.parse(dispatch.STAGE)
        for text in ['pg3848-', 'pg3846-frozen-v1.safe.json', 'Pg3844FreshResumePreparation', "['stage'],['prepare-resume']", "management_gate(P/'current-management-critical.lock')", 'new-only action required']:
            self.assertIn(text,raw)
        self.assertEqual(1,raw.count("with management_gate(P/'current-management-critical.lock')"))
        for text in ['pg3568-', 'pg3566-frozen', 'PG3420', 'pg3104']:
            self.assertNotIn(text,raw+dispatch.STAGE)
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg3844-current-resume-tools-v1',dispatch.GUEST)

    def test_strict_prepared_full11(self):
        raw=post.payload();ast.parse(raw)
        for text in [role.BASELINE,role.BEFORE,role.RUN,role.SAVE,"initial==after",'existing_parent_metadata(',"all(final[k]==initial[k]",'baseline==expected',"runtime==expected['runtime']",'nativeExecs', 'all11And18Config32AndOriginalJournalVerified']:
            self.assertIn(text,raw)
        self.assertNotIn("require(set(runtime)==",raw)
        self.assertIn('INVOCATION_ID=6f7821fe0af24d95953a9e29abd00c0d',raw)
        self.assertIn("manager.UnrefUnit(unit)",raw)
        self.assertEqual(1,raw.count('expected=after\n'))


if __name__=='__main__':unittest.main()
