"""Actual payload data/control ordering, no replay of completed run or native loss."""
import ast
import inspect
import unittest
from pg1596_current_ordinary_before import payload as before
from pg1597_current_ordinary_observer import namespace
from pg1598_current_ordinary_once import payload,main

class NewRunOnceTest(unittest.TestCase):
    def test_exact_payload_reserve_preserve_then_one_noargs_start(self):
        hashes={'pg1597_watch_parent.py':'a'*64,'pg457_stable_actor.py':'b'*64,'pg462_observer_identity.py':'c'*64}
        raw=payload(hashes);ast.parse(raw)
        start="subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"
        self.assertEqual(raw.count(start),1)
        self.assertLess(raw.index("persist('native-before-manifest.private.json'"),raw.index("persist('external-start-guard.private.json'"))
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index(start))
        self.assertLess(raw.index("require(watch==observer()and native==snapshot())"),raw.index(start))
        self.assertIn('require(len(records)==10)',raw)
        self.assertIn("'oldCompletedRunNotResumed':True",raw)
        self.assertIn("'originalBudgetSeconds':1800",raw)
        self.assertNotIn("'pg1596-current-ordinary-before-v1';require(not os.path.lexists(save))",raw)
        for forbidden in ['reset-failed','systemctl restart','--resume 15700','DROP TABLE','UPDATE schubert','settimeofday','CLOCK_REALTIME']:
            self.assertNotIn(forbidden,raw)
        self.assertIn("'ordinaryNoargs':True",before())
        watch=namespace()['files']()['pg1597_watch_parent.py']
        self.assertIn('sameRootOrdinary',watch);self.assertIn('sameParent',watch)
        self.assertNotIn('systemctl start',watch);self.assertNotIn('systemctl stop',watch)
        self.assertIn("frame.get('automaticStop',False)is not False",inspect.getsource(main))

if __name__=='__main__':unittest.main()
