import re
import unittest
import pg5356_ffm_outputs_selected as entry
import pg5366_ffm_outputs_bytecode as bytecode
import pg5368_ffm_outputs_public as public
import pg5376_ffm_progress_public as progress


class FfmTools(unittest.TestCase):
    def test_original_twelve_and_new_eight_with_explicit_scope_and_credit(self):
        path=entry.selected.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSessionTest.java'
        raw=path.read_text();names=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
        self.assertEqual(len(names),20);self.assertEqual(raw.count('@Test'),20)
        self.assertEqual(tuple(n for n in names if n.startswith('ffmown')),public.NAMES+(progress.NAME,))
        entry.configure()
        self.assertEqual((len(entry.selected.EXTRA_CHANGED),len(entry.selected.EXTRA_DEBUG),len(entry.extra_suites())),(59,178,101))
        ids=progress.revalidated_case_ids(owner_new=True)
        self.assertEqual(sum(v['newInThisChange'] for v in ids.values()),8)
        self.assertEqual(sum(v['newInThisChange'] for v in progress.revalidated_case_ids().values()),0)
        self.assertEqual(len({v['testId'] for v in ids.values()}),len(ids))

    def test_registration_rejects_missing_state_or_heap_after_native_return(self):
        valid={'ops':[(0,'iconst_1',''),(1,'bastore',''),(2,'invokevirtual','Method call:()Ljava/lang/Object;'),
            (3,'astore_3',''),(4,'iconst_2',''),(5,'bastore',''),(6,'aload_3',''),(7,'areturn','')]}
        self.assertEqual(bytecode.state_registration(valid),{'pendingStorePc':1,'nativeCallPc':2,'returnedStorePc':5})
        for opcode,arg in [('new','wrapper'),('invokedynamic','callback'),('invokestatic','box'),('anewarray','grow')]:
            bad={'ops':valid['ops'][:3]+[(3,opcode,arg)]+valid['ops'][3:]}
            with self.assertRaises(ValueError):bytecode.state_registration(bad)
        bad={'ops':[o for o in valid['ops'] if o[0]!=1]}
        with self.assertRaises(ValueError):bytecode.state_registration(bad)


if __name__=='__main__':unittest.main()
