import ast
import unittest
from pyflakes.api import check
import pg4222_fresh_current_noargs_once as p
import pg4224_same_parent_stack_sample as sample


class FreshAttemptTest(unittest.TestCase):
    def test_complete_new_namespace_and_one_durable_start_after_all_data_checks(self):
        raw=p.payload({});self.assertEqual(0,check(raw,'<fresh exact entry>'))
        tree=ast.parse(raw)
        starts=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'and n.args and isinstance(n.args[0],ast.List)and any(isinstance(x,ast.Constant)and x.value=='start'for x in n.args[0].elts)]
        self.assertEqual(1,len(starts));self.assertEqual(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],[x.value for x in starts[0].args[0].elts])
        self.assertTrue(raw.index("persist('external-start-guard.private.json'")<raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        for phrase in ["require(len(records)==52)","native==snapshot()['native']",'snapshot()==before_current and config()==before_configuration',"save=base/'pg4222-fresh-current-noargs-once-v1-prestart'","save=base/'pg4222-fresh-current-noargs-once-v1'","'parentNormal':False","'previousFailedRootData':summary"]:
            self.assertTrue(phrase in raw,phrase)
        self.assertFalse("'--resume'"in ast.get_source_segment(raw,starts[0]))

    def fixture(self):
        return {'MainPID':'999','InvocationID':'1234567890abcdef1234567890abcdef','entry':'dev.codex.schubert.nk.batch.file.MorningProcessMain','startTicks':123,
                'process':{'Uid':'0 0 0 0'},'ExecMainStartTimestampMonotonic':'1230000'}

    def test_stack_only_latest_stable_new_root_no_old_generation_or_terminal(self):
        frame=self.fixture();self.assertEqual(frame,sample.select_parent([{'states':{'morning':frame}}]))
        for change in [{'MainPID':'0'},{'race':True},{'entry':'other'},{'InvocationID':'820851b8291a4c958bb34f6c48430ca3'},{'InvocationID':'0'*32},{'process':{'Uid':'1 1 1 1'}},{'startTicks':None}]:
            with self.subTest(change=change),self.assertRaises(ValueError):sample.select_parent([{'states':{'morning':frame}},{'states':{'morning':{**frame,**change}}}])
        with self.assertRaises(ValueError):sample.select_parent([])

    def test_private_stack_extracts_only_bounded_methods_no_values(self):
        raw=b'999:\n"main" #1\n java.lang.Thread.State: RUNNABLE\n\tat dev.codex.Example.run(Example.java:12)\n\tat java.base/java.lang.Thread.run(Thread.java:15)\n\n"other"\n credential=PRIVATE_FIXTURE\n'
        self.assertEqual(['at dev.codex.Example.run(Example.java:12)','at java.base/java.lang.Thread.run(Thread.java:15)'],sample.frames_from(raw))
        for invalid in [b'',b'no main',b'"main"\nnot a frame\n',b'x'*4194305]:
            with self.assertRaises(ValueError):sample.frames_from(invalid)
        self.assertEqual(0,check(sample.payload(self.fixture(),'fixture'),'<bounded same Root stack>'))


if __name__=='__main__':unittest.main()
