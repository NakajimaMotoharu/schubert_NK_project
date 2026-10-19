import ast
import copy
import unittest
from pyflakes.api import check,checkPath
import pg5606_current_full_preservation as entry


class FreshBeforeImage(unittest.TestCase):
    def fixtures(self):
        prefix='/run/schubert-nk/pt-coverage/'
        original={prefix+f'old{i}.exec':{'metadata':[1,i+100,1400,1400,0o100600,1,20,1,1],'sha256':'a'*64}for i in range(92)}
        selected=[{'relative':f'old{i}.exec','metadata':copy.deepcopy(original[prefix+f'old{i}.exec']['metadata']),'bytes':20,'sha256':'a'*64}for i in range(8)]
        selected.extend({'relative':f'new{i}.exec','metadata':[1,i+300,1400,1400,0o100600,1,20,1,1],'bytes':20,'sha256':'b'*64}for i in range(2))
        return original,selected

    def test_every92_retained_two_later_points_no_arithmetic_native_credit(self):
        original,selected=self.fixtures();expected=entry.native_expected(original,selected)
        self.assertEqual(len(expected),94)
        self.assertEqual({k:expected[k]for k in original},original)

    def test_unknown_point_missing_old_duplicate_size_or_overwrite_refused(self):
        for kind in('oldMissing','missingPoint','duplicate','absolute','traversal','size','oldMutation','extra'):
            with self.subTest(kind=kind):
                original,selected=self.fixtures()
                if kind=='oldMissing':original.pop(next(iter(original)))
                if kind=='missingPoint':selected.pop()
                if kind=='duplicate':selected[-1]=copy.deepcopy(selected[0])
                if kind=='absolute':selected[-1]['relative']='/foreign.exec'
                if kind=='traversal':selected[-1]['relative']='../foreign.exec'
                if kind=='size':selected[-1]['bytes']=21
                if kind=='oldMutation':selected[0]['sha256']='0'*64
                if kind=='extra':selected[-1]['relative']='old90.exec'
                with self.assertRaises(ValueError):entry.native_expected(original,selected)

    def test_complete_ro_payload_retains_original_checks_and_normal_ref_finally(self):
        raw=entry.payload();self.assertEqual(check(raw,'<fresh current11 before-image>'),0)
        for text in('fresh_rows == second_rows','fresh_pid1 == after[\'pid1\']',"fresh_rows",'native_expected(original[\'native\']',"'sealedFull11Fields':11","'dataOnlyNotRuntimeAuthority':True"):
            self.assertIn(text,raw)
        tree=ast.parse(raw)
        forbidden={'StartUnit','StopUnit','RestartUnit','KillUnit','ResetFailedUnit','Reload','reboot','poweroff','unlink','rename'}
        pure_boot=ast.dump(ast.parse("ROOT_BINDING['boot'].replace('-', '')",mode='eval').body)
        def mutation(call):
            return isinstance(call,ast.Call)and isinstance(call.func,ast.Attribute)and(call.func.attr in forbidden or(call.func.attr=='replace'and ast.dump(call)!=pure_boot))
        self.assertFalse([n for n in ast.walk(tree)if mutation(n)])
        self.assertTrue(mutation(ast.parse("path.replace('other')",mode='eval').body))
        refs=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='UnrefUnit']
        self.assertEqual(len(refs),1)
        self.assertIn('finally:\n    for u in reversed(refs)',raw)
        self.assertIn("stable_path = base / 'pg5496-current-owned-tools-v1' / 'pg5496_stable_journal.py'",raw)
        self.assertNotIn("sealed('pg5496_stable_journal.py'",raw)
        self.assertLess(raw.index('stable_stat = stable_path.lstat()'),raw.index('manager.RefUnit(u)'))
        self.assertLess(raw.index("hashlib.sha256(stable_source).hexdigest() == HASHES"),raw.index('manager.RefUnit(u)'))
        self.assertNotIn("'ownedExplicitStops': 4",raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
