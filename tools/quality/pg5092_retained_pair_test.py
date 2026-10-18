"""Independent all-original AST, ownership-negative and exact-current proof factory tests."""
import ast
import copy
import json
import unittest
from pyflakes.api import check, checkPath
import pg5092_retained_pair_full_proof as proof


class CurrentProof(unittest.TestCase):
    def test_exact_full_namespace_original_guards_and_distinct_root_end(self):
        raw = proof.payload()
        self.assertEqual(0, check(raw, '<whole100/7 original witness>'))
        old_tree, tree = ast.parse(proof.before.payload()), ast.parse(raw)
        funcs = lambda t: {n.name: ast.dump(n, include_attributes=False) for n in t.body if isinstance(n, ast.FunctionDef)}
        old, new = funcs(old_tree), funcs(tree)
        for name, body in old.items():
            self.assertEqual(body, new[name], name)
        for literal in (proof.role.SOURCE, proof.role.BOM, 'pg5082-bootstrap-verify-v3',
                        '1c6a71bbcae6f487217e5d9b92dafbf4bb461f226d7544edb62e174bfd7f7ab9',
                        "summary['endMonotonicUs'] == 308517705767", '927504', '31055084',
                        '927536', '31055311', 'fresh_current_parent', 'owned_lock(name)',
                        "'signals0': True", "'oldCloseUnknown': True"):
            self.assertTrue(literal in raw, literal)
        self.assertTrue("summary['endMonotonicUs'] == 306951851178" not in raw)
        for forbidden in ('StartUnit(', 'StopUnit(', 'pidfd_send_signal', 'signal.SIGKILL', 'pg_terminate_backend'):
            self.assertTrue(forbidden not in raw, forbidden)

    def test_only_original_lock_loop_replaced_not_full_snapshot_or_sql(self):
        def snapshot(tree):
            return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'snapshot')
        old, new = snapshot(ast.parse(proof.before.payload())), snapshot(ast.parse(proof.payload()))
        loop = next(n for n in old.body if isinstance(n, ast.For) and ast.unparse(n.iter) == "('maintenance.lock', 'startup-admission.lock')")
        loop.body = ast.parse('owned_lock(name)').body
        self.assertEqual(ast.dump(old, include_attributes=False), ast.dump(new, include_attributes=False))
        source = ast.unparse(new)
        for literal in ("lines[-2:] == [b'0', b'0']", "len(rows) == 24", "rows == after['rows']",
                        "after['configuration'][u]", "after['runtime']", "after['unitFilesActual']"):
            self.assertIn(literal, source)

    def test_full100fd_fresh_guard_rejects_foreign_and_missing_metadata(self):
        ns = {}
        exec(proof.fresh_source(), ns)
        guard = ns['fresh_current_parent']
        old, _, _ = proof.observation()
        upper = max(v['metadata'][8] for v in old['fds'].values()) + 100
        self.assertTrue(guard(old, copy.deepcopy(old), upper))
        for field, invalid in [('pid', 1), ('ticks', old['ticks'] + 1), ('argvSha256', '0' * 64), ('authority', {})]:
            altered = copy.deepcopy(old)
            altered[field] = invalid
            with self.subTest(field=field), self.assertRaises(ValueError):
                guard(old, altered, upper)
        for mutate in (lambda v: v['fds'].pop('0'),
                       lambda v: v['fds']['0'].update(target='foreign'),
                       lambda v: v['fds']['0']['metadata'].__setitem__(1, 1),
                       lambda v: v['fds']['31']['metadata'].__setitem__(7, upper + 1)):
            altered = copy.deepcopy(old)
            mutate(altered)
            with self.assertRaises(ValueError):
                guard(old, altered, upper)

    def test_shared_run_only_legal_monotonic_change_and_exact_child_identity(self):
        ns = {}
        exec(proof.fresh_source(), ns)
        parent, child, names = proof.observation()
        changed = copy.deepcopy(parent)
        upper = max(v['metadata'][8] for v in parent['fds'].values()) + 100
        for fd in ('31', '90'):
            changed['fds'][fd]['metadata'][7:] = [upper, upper]
        self.assertTrue(ns['fresh_current_parent'](parent, changed, upper))
        self.assertEqual((927536, 31055311, 7), (child['pid'], child['ticks'], len(child['fds'])))
        self.assertEqual(1, len(names))
        self.assertEqual('927504', child['authority']['PPid'])
        # The snapshot is a measurement, never an invented successful old close.
        original = json.loads((proof.W / 'pg5090-retained-pair-observe-v1/stdout.private.json').read_bytes())
        self.assertIs(original['oldCloseUnknown'], True)
        for path in (proof.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
