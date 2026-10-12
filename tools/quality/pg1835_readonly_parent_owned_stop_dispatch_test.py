"""Actual composed prequal uses dedicated parent read, unchanged stop scope."""
import contextlib
import io
import json
import sys
import types
import unittest
from unittest.mock import Mock,patch
import pg1835_readonly_parent_owned_stop_dispatch as actual
from pg1799_warning_parent_projection_contract import qualify_warning_parent
import pg1833_readonly_parent_state_sources_test as fixture


class Profile(unittest.TestCase):
    def test_actual_before_ownership_entry_never_calls_stop_show(self):
        state=fixture.Scope().fixture();helper=types.ModuleType('pg1833_native_owned_stop')
        helper.parent_state=Mock(return_value=state);helper.parent_configuration=Mock(return_value={'Type':'oneshot','SuccessExitStatus':''});helper.qualify_warning_parent=qualify_warning_parent
        helper.show=Mock(side_effect=ValueError('parent is never a stop target'))
        with patch.dict(sys.modules,{'pg1833_native_owned_stop':helper}),patch.object(sys,'path',list(sys.path)),contextlib.redirect_stdout(io.StringIO())as output:
            exec(compile(actual.PARENT_PREQUAL,'<actual fixed before ownership>','exec'),{'GUEST':'/fixture/no-ownership','HASHES':{}})
        v=json.loads(output.getvalue());self.assertTrue(v['stateConfigurationStableTwice']);self.assertFalse(v['stopAuthority']);helper.show.assert_not_called();self.assertEqual(2,helper.parent_state.call_count)

    def test_actual_main_busy_gate_and_fixed_stage(self):
        self.assertTrue(actual.GUEST in actual.STAGE);self.assertTrue(actual.REMOTE in actual.STAGE)
        self.assertFalse('pg1821'in actual.PARENT_PREQUAL);self.assertFalse('helper.show'in actual.PARENT_PREQUAL)
        with patch.object(actual.sys,'argv',['actual','stop']),patch.object(actual,'management_gate',side_effect=BlockingIOError),patch.object(actual,'run_action')as run:
            with self.assertRaises(BlockingIOError):actual.main()
            run.assert_not_called()


if __name__=='__main__':unittest.main()
