"""PT-DEP-1047001..003: independent SQL token oracle, no Production expected call."""
import ast
import re
import unittest
from pg1037_cold_preparation_sources import guest
from pg1023_cold_contract import owned_peer_sql as legacy_future_sql


def functions():
    tree = ast.parse(guest())
    names = {'owned_peer_sql'}
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    class Contract:
        @staticmethod
        def all_client_sql(backend):
            return 'select 0;'
    env = {'contract': Contract}
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'sql-only', 'exec'), env)
    return env['owned_peer_sql']


class OwnedSql(unittest.TestCase):
    def test_independent_exact_peer_predicate_and_statement_count(self):
        for function in (functions(), legacy_future_sql):
            sql = function(5497)
            self.assertEqual(3, len([x for x in sql.split(';') if x]))
            self.assertIn("where datname='schubert_nk'and pid=5497 and usename='schubert_batch'", sql)
            self.assertIn("l.pid=a.pid and locktype='advisory'", sql)
            self.assertIn("objsubid=1 and mode='ExclusiveLock'and granted", sql)

    def test_backend_boundaries_have_separate_numeric_tokens(self):
        for function in (functions(), legacy_future_sql):
            for backend in (0, 2, 5497, 2147483646):
                sql = function(backend)
                self.assertIsNone(re.search(r'\d(?:and|or|select)\b', sql))
                self.assertIn('pid=' + str(backend) + ' and ', sql)

    def test_historical_counterexample_is_rejected_not_rewritten(self):
        historical = 'pid=5497and usename='
        self.assertIsNotNone(re.search(r'\dand\b', historical))
        self.assertNotIn('pid=5497and ', functions()(5497))


if __name__ == '__main__':
    unittest.main()
