"""Lexer inventory tests, no Java execution or source rewrite."""
import unittest
import pg6542_jdbc_catch_inventory as subject


class CatchInventoryTest(unittest.TestCase):
    def test_comments_literals_text_blocks_and_non_sql_are_not_sites(self):
        code = '''// catch(SQLException ignored) {}
        String s="catch(SQLException ignored) {}";
        String t="""catch(SQLException ignored) { new Error(); }""";
        try {} catch(IOException ignored) {} catch(SQLException actual) { throw actual; }
        '''
        rows = subject.sites(code)
        self.assertEqual(1, len(rows))
        self.assertEqual('actual', rows[0]['catchVariable'])
        self.assertEqual('RETHROW_OR_ATTACH_REVIEW', rows[0]['category'])

    def test_nested_multicatch_and_categories_are_only_pending_hints(self):
        code = '''try {} catch(java.sql.SQLException | RuntimeException outer) {
          try {} catch(SQLException inner) { outer.addSuppressed(inner); }
          Catalog.preserveFatal(outer); throw new Catalog();
        }
        try {} catch(SQLException key) { if(key.getSQLState()!=null) return; }
        try {} catch(SQLException mapped) { throw new Catalog(); }'''
        rows = subject.sites(code)
        self.assertEqual(['GUARDED_REVIEW', 'RETHROW_OR_ATTACH_REVIEW', 'SQLSTATE_REVIEW',
                          'TRANSLATION_REVIEW'], [r['category'] for r in rows])
        self.assertTrue(all(r['reviewStatus'].startswith('PENDING') for r in rows))
        self.assertEqual(4, len({r['bodyTokenSha256'] for r in rows}))

    def test_malformed_catch_rejects_instead_of_silently_losing_target(self):
        for code in ('catch(SQLException e', 'catch(SQLException e) {', 'catch(SQLException e) x'):
            with self.assertRaises(ValueError):
                subject.sites(code)


if __name__ == '__main__':
    unittest.main()
