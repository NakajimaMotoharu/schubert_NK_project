"""Actual pre-ownership script with separate sources, actual gate, immutable slots."""
import contextlib
import io
import json
import sys
import types
import unittest
from unittest.mock import Mock,patch
import pg1826_state_configuration_owned_stop_dispatch as actual
from pg1799_warning_parent_projection_contract import qualify_warning_parent


class Dispatcher(unittest.TestCase):
    def fixture(self):
        return {'Id':'schubert-nk-morning-controller.service','LoadState':'loaded','ActiveState':'failed','SubState':'failed','Result':'exit-code','MainPID':'0','ControlPID':'0','Job':'','InvocationID':'b5a12ee25dc44ec49b08f5d084b4052f','ExecMainCode':'1','ExecMainStatus':'10','ExecMainStartTimestampMonotonic':'81404764713','ExecMainExitTimestampMonotonic':'83018952135','Type':'oneshot','Restart':'no','RemainAfterExit':'no','KillMode':'control-group','SendSIGKILL':'no'}

    def exercise_prequal(self,states,configs):
        helper=types.ModuleType('pg1821_native_owned_stop');helper.show=Mock(side_effect=states);helper.parent_configuration=Mock(side_effect=configs);helper.qualify_warning_parent=qualify_warning_parent
        with patch.dict(sys.modules,{'pg1821_native_owned_stop':helper}),patch.object(sys,'path',list(sys.path)),contextlib.redirect_stdout(io.StringIO())as output:
            exec(compile(actual.PARENT_PREQUAL,'<actual before-ownership two-source probe>','exec'),{'GUEST':'/fixture/no-owned-resources','HASHES':{}})
        result=json.loads(output.getvalue());self.assertFalse(result['stopAuthority']);self.assertTrue(result['stateHasNoVirtualConfiguration']);self.assertEqual(2,helper.show.call_count);self.assertEqual(2,helper.parent_configuration.call_count)

    def test_actual_prequalification_separate_fields(self):
        config={'Type':'oneshot','SuccessExitStatus':''}
        self.exercise_prequal([self.fixture(),self.fixture()],[config,config])

    def test_missing_config_wrong_state_and_two_read_change(self):
        good={'Type':'oneshot','SuccessExitStatus':''}
        for states,configs in [([self.fixture()],[{'Type':'oneshot'}]),([{**self.fixture(),'SuccessExitStatus':''}],[good]),([{**self.fixture(),'ActiveState':'inactive'}],[good]),([self.fixture(),{**self.fixture(),'Result':'success'}],[good,good]),([self.fixture(),self.fixture()],[good,{'Type':'oneshot','SuccessExitStatus':'10'}])]:
            with self.subTest(states=states),self.assertRaises((AssertionError,ValueError)):self.exercise_prequal(states,configs)

    def test_actual_main_excludes_busy_other_management(self):
        with patch.object(actual.sys,'argv',['actual','stop']),patch.object(actual,'management_gate',side_effect=BlockingIOError),patch.object(actual,'run_action')as run:
            with self.assertRaises(BlockingIOError):actual.main()
            run.assert_not_called()

    def test_exact_current_stage_namespace(self):
        compile(actual.STAGE,'<actual new stage>','exec');self.assertTrue(actual.GUEST in actual.STAGE);self.assertTrue(actual.REMOTE in actual.STAGE)
        self.assertFalse('pg1808'in actual.STAGE);self.assertFalse('pg1816'in actual.STAGE)


if __name__=='__main__':unittest.main()
