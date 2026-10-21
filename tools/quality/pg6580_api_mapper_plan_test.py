import unittest
import pg6580_api_mapper_plan as subject


class MapperPlanTest(unittest.TestCase):
    def test_trace_comment_stays_before_contiguous_imports_and_order_is_not_java_semantics(self):
        raw='''package test;
        // PG-D trace remains a header, not an inter-import comment.
        import static java.util.Objects.requireNonNull;
        import java.sql.SQLException;
        try {} catch(SQLException failure) { throw new Catalog(); }'''
        fixed,_,_=subject.transform('UserQueryApplicationService',raw,['SQLCATCH-008'])
        self.assertLess(fixed.index('// PG-D trace'),fixed.index('import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;'))
        between=fixed[fixed.index('import '):fixed.index('try {}')]
        self.assertNotIn('// PG-D trace',between)
        self.assertEqual(subject.semantic_hash('import a.B; import static c.D.x; class A {}'),
                         subject.semantic_hash('import static c.D.x; import a.B; class A {}'))
        self.assertNotEqual(subject.semantic_hash('import a.B; class A {}'),subject.semantic_hash('import a.C; class A {}'))

    def test_owned_cleanup_does_not_classify_before_rollback_or_change_sql(self):
        raw='''package test;
        try {} catch(SQLException | RuntimeException failure) {
          try { connection.rollback(); } catch(SQLException secondary) { failure.addSuppressed(secondary); }
          throw failure;
        }
        try {} catch(SQLException | RuntimeException catalog) { throw new Catalog(); }
        '''
        fixed,actions,_=subject.transform('UserMutationApplicationService',raw,['SQLCATCH-003','SQLCATCH-004','SQLCATCH-005'])
        self.assertIn('catch(SQLException | RuntimeException | Error failure)',fixed)
        self.assertIn('catch(SQLException | RuntimeException | Error secondary)',fixed)
        self.assertIn('TemporaryInfrastructureException.attachSecondary(failure, secondary);',fixed)
        self.assertIn('TemporaryInfrastructureException.preserveFatal(catalog);',fixed)
        self.assertEqual(3,len(actions))
        self.assertEqual(1,fixed.count('connection.rollback();'))

    def test_auth_priority_and_raw_transfer_are_not_replaced(self):
        raw='''package test;
        try {} catch(SQLException failure) { throw new Catalog(); }
        try {} catch(InboxException invalid) { throw invalid; }
        '''
        fixed,actions,_=subject.transform('LoginInboxService',raw,['SQLCATCH-077'])
        self.assertIn('AuthenticationInfrastructureException.preserveFatal(failure);',fixed)
        self.assertNotIn('TemporaryInfrastructureException',fixed)
        self.assertIn('catch(InboxException invalid) { throw invalid; }',fixed)
        self.assertEqual(1,len(actions))

    def test_comment_literal_and_changed_cardinality_fail_closed(self):
        raw='''package test; String s="catch(SQLException ignored) {}";
        // catch(SQLException alsoIgnored) {}
        try {} catch(RuntimeException runtime) { throw new Catalog(); }'''
        self.assertEqual(1,len(subject.spans(raw)))
        with self.assertRaises(ValueError):subject.transform('UserQueryApplicationService',raw,['SQLCATCH-005'])
        with self.assertRaises(ValueError):subject.apply_edits('abcd',[(0,3,'x'),(2,4,'y')])
        self.assertEqual(subject.semantic_hash('int x=1; // public comment'),subject.semantic_hash('int x = 1;'))
        self.assertNotEqual(subject.semantic_hash('String x="one";'),subject.semantic_hash('String x="two";'))

    def test_outbox_direct_fatal_selection_stays_before_attachment(self):
        raw='''package test;
        if (secondary instanceof Error fatal && !(primary instanceof Error)) {
          fatal.addSuppressed(primary); throw fatal;
        }
        if (primary != secondary) primary.addSuppressed(secondary);'''
        fixed,actions,_=subject.transform('OutboxDispatcher',raw,[])
        self.assertIn('fatal.addSuppressed(primary); throw fatal;',fixed)
        self.assertLess(fixed.index('throw fatal;'),fixed.index('TemporaryInfrastructureException.attachSecondary(primary, secondary)'))
        self.assertEqual(1,len(actions))


if __name__=='__main__':unittest.main()
