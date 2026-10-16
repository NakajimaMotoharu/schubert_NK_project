"""Actual RO stage path/ABI and independent failed receipt / Ref scope."""
import ast
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4526_failed_current_ro_dispatch as d
import pg4528_failed_current_ro_post as p


class CandidateOnlyRo(unittest.TestCase):
    def test_complete_stage_paths_and_current_jar_not_old_release(self):
        raw=d.source();compile(raw,'<actual RO operator>','exec')
        self.assertIn('pg4530-frozen-v1.safe.json',raw);self.assertIn('pg4532-stage-v1.exit',raw);self.assertIn('Pg4522OriginalTupleTest',raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG3976',raw);self.assertNotIn('PG3748',raw)
        self.assertIn(d.REMOTE+'/',d.STAGE);self.assertIn(d.role.TOOLS+'.tar',d.STAGE)
        self.assertEqual(0,check("DIGEST='literal'\nFILES={}\n"+d.STAGE,'<full stage>',Reporter(io.StringIO(),io.StringIO())))

    def test_literal_ro_receipt_all_lines_old_normal_and_type_mutations_reject(self):
        raw=(b'genuineParentNormalWarningOriginal=false\ncurrentManagerGc=false\nfailedParent143DataOnly=true\ncandidateReadOnlyVerified=true\n'
          b'allNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsReloadsEpochWrites0=true\noldUnknownNormalized=false\n')
        self.assertTrue(p.normal_readonly_receipt(raw))
        lines=raw.splitlines(keepends=True)
        for i in range(8):
            with self.subTest(i=i),self.assertRaises(ValueError):p.normal_readonly_receipt(b''.join(lines[:i]+lines[i+1:]))
        for bad in [None,bytearray(raw),raw+b'extra\n',raw.replace(b'genuineParentNormalWarningOriginal=false',b'genuineParentNormalWarningOriginal=true')]:
            with self.assertRaises(ValueError):p.normal_readonly_receipt(bad)

    def test_actual_ro_checks_inside_metadata_refs_and_after_current_candidate_proof(self):
        raw=p.payload();tree=ast.parse(raw);scope=next(n for n in tree.body if isinstance(n,ast.Try)and n.finalbody)
        calls=[n for n in ast.walk(scope)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='normal_readonly_receipt']
        self.assertEqual(1,len(calls));self.assertLess(calls[0].lineno,scope.finalbody[0].lineno)
        self.assertIn("'ro'in options and 'rw'not in options",raw)
        self.assertEqual(0,check(raw,'<full independent RO post>',Reporter(io.StringIO(),io.StringIO())))
        self.assertIn('pg4532-prepare-ro-v1.safe.json',p.main_source())


if __name__=='__main__':unittest.main()
