import inspect
import unittest
from pyflakes.api import checkPath,check
import pg6296_web_send_green as subject
import pg6298_web_send_qualification as qualification


class GreenDefinitions(unittest.TestCase):
    def test_actual84_and_both_changed_classes_and_caller_suites(self):
        cases,counts=subject.inventory()
        self.assertEqual((84,15),(sum(counts.values()),len(counts)))
        self.assertEqual(2,len(subject.MAIN))
        for name in ('web.logging.WebLogDispatcherTest','web.logging.WebLogReplayWorkerTest','web.messaging.JmsRequestReplyClientTest'):
            self.assertIn(name,cases['web'])
        self.assertEqual(9,counts['dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest'])
        self.assertEqual(7,counts['dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest'])

    def test_green_explicit_namespace_and_original_read84_not51(self):
        raw=subject.red.runner().replace('runner_source(28,9,target_count=16)','runner_source(84,15,target_count=16)').replace('pg6294-web-send-red-v1','pg6296-web-send-selected-v1').replace('def run_red():','def run_green():')
        bindings='from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6296_web_send_green import inventory\n'
        self.assertEqual(0,check(bindings+raw,'<ordinary84 actual binding>'))
        self.assertIn('pg6296-web-send-selected-v1',raw)
        self.assertIn('runner_source(84,15,target_count=16)',raw)
        code=inspect.getsource(qualification.main)
        self.assertIn('(84,15)',code)
        self.assertIn('PG6268-outbox-failure-qualification-v1',code)
        self.assertNotIn('(51,11)',code)
        for path in (subject.__file__,qualification.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
