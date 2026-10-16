import inspect
import unittest
from pyflakes.api import check
import pg4034_current_jdbc_finally_static as review


class CurrentTypedJdbc(unittest.TestCase):
    def test_complete_current_scope_never_old_coordinate_alias_or_f03_pass(self):
        raw = '\n'.join(inspect.getsource(fn) for fn in [review.previous.require, review.previous.facts]) + '\n' + review.server_source()
        self.assertEqual(0, check(raw, '<current JDBC all52 and26 typed decisions>')); compile(raw, '<new source actual type facts>', 'exec')
        for marker in ['PG4032-current-identity-static-v1', 'PG3968-literal-invariant-whole-qualified-v1', 'source-full-PG3966', 'len(unsupported) == 2', 'NO_MATCHING_TYPED_PRECEDENCE_SHAPE', "'currentTypedFinallyVerified': 26", "'newSourceRequalifiedScopes': 15", "'unclassified': 1349", "'F03Accepted': False"]:
            self.assertIn(marker, raw)
        for marker in ['PMD-7fff-1162', 'PMD-7fff-1167', 'source-full-PG3734', 'management_gate', 'systemctl']:
            self.assertNotIn(marker, raw)
        main = review.main_source(); compile(main, '<complete new JDBC source emission>', 'exec')
        self.assertIn('server_source() if f is server', main)


if __name__ == '__main__': unittest.main()
