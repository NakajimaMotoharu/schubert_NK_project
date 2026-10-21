import unittest
from pyflakes.api import checkPath,check
import pg6316_outbox_graph_red as subject


class NewGraphDefinition(unittest.TestCase):
    def test_exact38_actual_declarations_and_two_named_targets(self):
        _,counts=subject.inventory()
        self.assertEqual((38,9),(sum(counts.values()),len(counts)))
        self.assertEqual(20,counts['dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest'])
        self.assertEqual(6,counts['dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcherTest'])
        raw=subject.runner();compile(raw,'<ordinary38>','exec')
        bindings='from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6316_outbox_graph_red import inventory\n'
        self.assertEqual(0,check(bindings+raw,'<new38 with explicit actual bindings>'))
        self.assertIn('pg6316-outbox-graph-red-v1',raw)
        self.assertIn('runner_source(38,9,target_count=16)',raw)
        self.assertNotIn('pg6264-outbox-failure-red-v1',raw)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
