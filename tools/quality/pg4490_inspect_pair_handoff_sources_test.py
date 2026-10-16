"""Actual emitted controller scope, full pre-save ordering and no-action oracle."""
import ast
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4490_inspect_pair_handoff_sources as source
import pg4492_inspect_pair_stage as stage


class HandoffBoundary(unittest.TestCase):
    def test_full_emitted_static_and_independent_post_unchanged_except_save(self):
        raw=source.payload();compile(raw,'<actual handoff>','exec')
        self.assertEqual(0,check(raw,'<actual handoff>',Reporter(io.StringIO(),io.StringIO())))
        self.assertEqual(0,check(stage.stage_payload(),'<actual stage>',Reporter(io.StringIO(),io.StringIO())))
        self.assertEqual(source.post.files()['post.py'],source.independent_post().replace('pg4490-inspect-pair-handoff-v2-independent-post','pg4362-pool-bound-post-v3'))

    def test_actual_invariant_captures_both_complete_images_before_comparing(self):
        tree=ast.parse(source.payload());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='invariant')
        actions=[]
        def capture(label):actions.append(('capture',label));return {'pair':{},'data':{},'config':{},'hashes':{}}
        def check_one(value):actions.append(('check',value));raise ValueError('independent injected mismatch')
        ns={'release':lambda:actions.append(('release',)),'capture':capture,'check_one':check_one,'private':lambda *a:None,'require':lambda v:None}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual invariant>','exec'),ns)
        with self.assertRaises(ValueError):ns['invariant']('literal')
        self.assertEqual(['release','capture','capture','check'],[a[0]for a in actions])

    def test_only_two_explicit_pidfd_targets_and_no_business_actions(self):
        raw=source.payload();tree=ast.parse(raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([(827198,16494387),(827230,16494598)],[(c.args[0].value,c.args[1].value)for c in calls])
        for banned in ['SIGKILL','pg_terminate_backend','KillUnit','StopUnit','StartUnit','ReloadUnit']:self.assertNotIn(banned,source.BODY)
        self.assertIn("if MODE=='recover':",source.BODY)
        self.assertIn("frame('SSC297_OWNERS_READY '+proof);issued=True",source.BODY)
        self.assertIn("while True:time.sleep(1)",source.BODY)
        self.assertIn("for unit in reversed(refs):manager.UnrefUnit(unit)",source.BODY)


if __name__=='__main__':unittest.main()
