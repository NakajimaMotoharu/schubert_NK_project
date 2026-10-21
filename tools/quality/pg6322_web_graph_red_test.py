import unittest
from unittest.mock import patch
from pyflakes.api import checkPath,check
import pg6322_web_graph_red as subject


class NewDefinitions(unittest.TestCase):
    def test_actual53_and_current_three_targets_original86_prerequisite(self):
        _,counts=subject.inventory()
        self.assertEqual((53,10),(sum(counts.values()),len(counts)))
        self.assertEqual(21,counts['dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest'])
        self.assertEqual(10,counts['dev.codex.schubert.nk.web.logging.WebLogDispatcherTest'])
        self.assertEqual(10,counts['dev.codex.schubert.nk.web.logging.WebLogReplayWorkerTest'])
        subject.prerequisites()
        raw=subject.runner();compile(raw,'<ordinary53>','exec')
        bindings='from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6322_web_graph_red import inventory\n'
        self.assertEqual(0,check(bindings+raw,'<ordinary53 actual bindings>'))
        self.assertIn('pg6322-web-graph-red-v1',raw)
        self.assertIn('runner_source(53,10,target_count=17)',raw)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_wrong_original_qualification_hash_is_rejected(self):
        with patch.object(subject,'sha',return_value='a'*64),self.assertRaisesRegex(ValueError,'exact original86'):
            subject.prerequisites()


if __name__=='__main__':unittest.main()
