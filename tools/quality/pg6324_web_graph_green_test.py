import inspect
import unittest
from pyflakes.api import checkPath,check
import pg6324_web_graph_green as subject
import pg6326_web_graph_qualification as qualification


class Definition(unittest.TestCase):
    def test_exact89_and_two_web_main_original86_reference(self):
        cases,counts=subject.inventory()
        self.assertEqual((89,15),(sum(counts.values()),len(counts)))
        self.assertEqual(2,len(subject.MAIN));self.assertIn('api.messaging.outbound.OwnedOutboxDispatcherTest',cases['api'])
        raw=subject.red.runner().replace('runner_source(53,10,target_count=17)','runner_source(89,15,target_count=17)').replace('pg6322-web-graph-red-v1','pg6324-web-graph-selected-v1').replace('def run_red():','def run_green():')
        bindings='from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6324_web_graph_green import inventory\n'
        self.assertEqual(0,check(bindings+raw,'<ordinary89 actual bindings>'))
        self.assertIn('(89,15)',inspect.getsource(qualification.main))
        self.assertIn('PG6320-outbox-graph-qualification-v1',inspect.getsource(qualification.main))
        for path in (subject.__file__,qualification.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
