import json
import unittest
from pyflakes.api import checkPath
import pg6346_ordinary_outbox_rollout as subject


class CurrentOrdinaryScope(unittest.TestCase):
    def test_saved_whole_qualified_six_classes_and_five_graph_cases(self):
        p=subject.BASE/'PG6346-ordinary-outbox-rollout-v1/manifest.json';value=json.loads(p.read_bytes())
        self.assertEqual(subject.SOURCE,value['source']);self.assertEqual(0,value['actualExit'])
        self.assertEqual((6,3,3,7),(value['ordinaryProducerClasses'],value['ownedSenderClasses'],value['borrowedStageOnlyClasses'],value['producerSourceSites']))
        self.assertEqual(6,len(value['targets']));self.assertEqual(5,len(value['independentGraphCases']))
        for target in value['targets']:
            self.assertTrue(target['currentWholeCaseRefs'])
            for ref in target['currentWholeCaseRefs']:self.assertEqual(subject.SOURCE,ref['source'])
        self.assertFalse(value['formalAccepted']);self.assertEqual(0,value['vmActions']);self.assertEqual(0,value['testsExecuted'])
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_missing_wrong_source_or_nonpass_whole_case_rejected(self):
        for cases in ([],[dict(**{'class':'fixture'},source='a'*40,result='PASS_ORIGINAL_XML')],
            [dict(**{'class':'fixture'},source=subject.SOURCE,result='SKIPPED')]):
            with self.subTest(cases=cases),self.assertRaises(ValueError):subject.bind_classes(['fixture'],cases)


if __name__=='__main__':unittest.main()
