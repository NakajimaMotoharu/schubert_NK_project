import unittest
from pyflakes.api import checkPath,check
import pg6294_web_send_red as subject


class RedDefinition(unittest.TestCase):
    def test_actual28_declarations_and_two_modified_classes(self):
        cases,counts=subject.inventory()
        self.assertEqual((28,9),(sum(counts.values()),len(counts)))
        self.assertIn('web.messaging.ArtemisRequestSenderTest',cases['web'])
        self.assertIn('web.logging.WebLogMessageSenderTest',cases['web'])
        self.assertEqual(9,counts['dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest'])
        self.assertEqual(7,counts['dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest'])

    def test_new_namespace_and_current_source_targets_no_old_reproduction(self):
        raw=subject.runner();compile(raw,'<ordinary28>','exec')
        exports=('runner_source','engine','node_environment','source_test_names','inspect','targets_profile')
        for name in exports:self.assertIn(name,vars(subject.previous.prior))
        bindings='from pg6206_keeper_faults_selected import '+','.join(exports)+'\nfrom pg6294_web_send_red import inventory\n'
        self.assertEqual(0,check(bindings+raw,'<ordinary28 with actual explicit bindings>'))
        self.assertIn('pg6294-web-send-red-v1',raw)
        self.assertIn('runner_source(28,9,target_count=16)',raw)
        self.assertIn("scope['targets']['web'].extend(('web/messaging/ArtemisRequestSender','web/logging/WebLogMessageSender'))",raw)
        self.assertNotIn('pg6264-outbox-failure-red-v1',raw)
        self.assertEqual(0,checkPath(subject.__file__))
        self.assertEqual(0,checkPath(__file__))

    def test_missing_actual_binding_is_still_rejected(self):
        exports='runner_source,engine,node_environment,source_test_names,inspect'
        bindings='from pg6206_keeper_faults_selected import '+exports+'\nfrom pg6294_web_send_red import inventory\n'
        self.assertEqual(1,check(bindings+subject.runner(),'<independently omitted targets_profile>'))


if __name__=='__main__':unittest.main()
