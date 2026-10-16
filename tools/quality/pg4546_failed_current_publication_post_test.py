"""All seven phases, full typed eleven fields and no old Source/native authority."""
import ast
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4546_failed_current_publication_post as p


class FinitePost(unittest.TestCase):
    def test_actual_seven_phase_loop_and_failed_receipt_are_independent(self):
        raw=p.publication_checks()
        self.assertIn("tuple(dict.fromkeys(phase for stamp,phase,observed in phases))==oracle['PHASES']",raw)
        self.assertIn("for stamp,phase,observed in phases:oracle['verify']",raw)
        self.assertIn('genuineParentNormalWarningOriginal=false\\ncurrentManagerGc=false\\nfailedParent143DataOnly=true',raw)
        self.assertNotIn('genuineParentNormalWarningOriginal=true',raw)
        self.assertIn(p.role.SAVE,raw);self.assertIn(p.role.TOOLS,raw)
        self.assertIn('strict_equal(after[k],old_after[k])',raw)
        self.assertNotIn('startsStopsReloadsEpochWrites0=true',raw);self.assertIn('canonicalInvalidEpochWritten=true',raw)

    def test_signed_new_current_and_only_old_parent_data_are_separate(self):
        raw=p.payload();compile(raw,'<actual post>','exec');self.assertEqual(0,check(raw,'<actual post>',Reporter(io.StringIO(),io.StringIO())))
        prefix=p.reader_prefix();self.assertIn(p.role.SOURCE,prefix);self.assertIn(p.role.BOM,prefix);self.assertIn('pg4432-manifest.sig',prefix)
        self.assertNotIn("data['source']['commit']=='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'",prefix)
        self.assertIn("parent['ExecMainStatus']=='143'",p.BODY);self.assertIn("oldNativeNotAppliedToNewSource':True",p.BODY)
        self.assertNotIn('newMARDDBTenRefNormalClose',p.BODY)  # independently verifies resources0; never fabricates an unacquired scope

    def test_full_images_saved_before_typed_comparison_and_normal_ref_close(self):
        tree=ast.parse(p.payload());capture=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='capture')
        calls=[(n.lineno,n)for n in ast.walk(capture)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)]
        fullsave=next(line for line,n in calls if n.func.id=='save_private'and isinstance(n.args[0],ast.BinOp)and isinstance(n.args[0].right,ast.Constant)and n.args[0].right.value=='-full11.private.json')
        compare=next(line for line,n in calls if n.func.id=='strict_equal');self.assertLess(fullsave,compare)
        self.assertIn('require(strict_equal(first,second))',p.BODY);self.assertIn('manager.UnrefUnit(unit)',p.BODY)
        self.assertFalse(p.strict_equal({'value':True},{'value':1}));self.assertFalse(p.strict_equal([1,2],[2,1]))
        self.assertTrue(p.strict_equal({'a':None,'b':[1,'two']},{'b':[1,'two'],'a':None}))


if __name__=='__main__':unittest.main()
