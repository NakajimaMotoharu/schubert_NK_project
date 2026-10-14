"""Current source/boot/observer/once guard and retained finite preflight namespace guards."""
import ast
import unittest
from pyflakes.api import check
import pg2862_network_newcurrent_observer as watch
import pg2864_network_newcurrent_once as p


class NewCurrentOnce(unittest.TestCase):
    def test_new_current_observer_no_old_boot_or_start_authority(self):
        raw=watch.source();ast.parse(raw)
        for v in ['pg2862','PG2802','a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','79a3260a-e16d-42bf-942a-b914ed144c28',
            '37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863']:
            self.assertTrue(v in raw,v)
        self.assertFalse('b2d6f605'in raw)
        generated=watch.namespace()['files']()
        for raw in generated.values():self.assertEqual(0,check(raw,'<whole immutable new observer>'))
        self.assertTrue("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860"in generated['pg2862_watch_parent.py'])

    def test_once_guard_precedes_external_start_and_no_old_native_import(self):
        raw=p.payload({'pg2862_watch_parent.py':'a'*64})
        self.assertEqual(0,check(raw,'<whole once admission>'))
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("['/usr/bin/systemctl','start','--no-block'"))
        for v in ['originalBudgetSeconds','1800',"'replayAllowed':False", "'newBootRuntimeExecCount':0",'clientSuccessIsNotParentSuccess',
            "first==snapshot()and runtime==runtime_check()"]:
            self.assertTrue(v in raw,v)
        self.assertFalse('allResources0' in raw)
        self.assertFalse('parentBackendAdvisoryFlocksGone' in raw)
        self.assertFalse('native_copy' in raw)


if __name__=='__main__':unittest.main()
