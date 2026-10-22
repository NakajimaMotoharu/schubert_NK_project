"""Management guards, never actual application/VM execution."""
import unittest
import copy
import xml.etree.ElementTree as ET

import pg6962_jms_f02_criteria as subject


class RemainingCriteriaTest(unittest.TestCase):
    def test_logical_and_two_existing_support_are_both_required_and_cost_zero(self):
        task = dict(id='WBS-P005-03',ownedArtifacts=['ordinary'])
        rows = [dict(owner=task['id'],path='ordinary',sha256='ordinary-hash')]
        inputs = {'ordinary':'ordinary-hash'}
        for path,(digest,origin) in subject.SUPPORT.items():
            inputs[path] = digest
            rows.append(dict(owner=task['id'],costOwner=task['id'],supportingExistingLeaf=task['id'],
                             path=path,sha256=digest,originCommit=origin,implementationSupportOnly=True,
                             additionalBudgetPp=0,historicalPath=None,kind='JAVA',module='protocol',
                             **{'class':path.split('/src/main/java/')[1][:-5]}))
        logical,support = subject.scope_rows(task,rows,inputs)
        self.assertEqual({'ordinary':'ordinary-hash'},logical)
        self.assertEqual(set(subject.SUPPORT),{r['path'] for r in support})
        for field,value in [('additionalBudgetPp',1),('module','api'),('costOwner','other'),
                            ('supportingExistingLeaf','other'),('originCommit','old'),('sha256','tamper'),
                            ('historicalPath','invented'),('implementationSupportOnly',False)]:
            changed = copy.deepcopy(rows);changed[1][field] = value
            with self.subTest(field=field),self.assertRaises(ValueError):subject.scope_rows(task,changed,inputs)
        with self.assertRaises(ValueError):subject.scope_rows(task,rows[:-1],inputs)
        with self.assertRaises(ValueError):subject.scope_rows(task,rows+[dict(rows[1])],inputs)
        changed = copy.deepcopy(rows);changed[1]['path']='unregistered'
        with self.assertRaises(ValueError):subject.scope_rows(task,changed,inputs)

    def test_actual_test_source_path_has_one_physical_module(self):
        self.assertEqual('web:messaging.JmsReplyDecoderTest', subject.selector(
            'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/JmsReplyDecoderTest.java'))

    def test_xml_required_field_is_not_missing_or_optional_zero(self):
        node = ET.fromstring('<project xmlns="http://maven.apache.org/POM/4.0.0"><version> 25 </version></project>')
        self.assertEqual('25', subject.text(node,'m:version'))
        with self.assertRaises(ValueError):subject.text(node,'m:missing')

    def test_missing_empty_or_uncovered_family_is_not_one_hundred(self):
        path = 'src/schubert-nk-web/src/main/java/p/Value.java'
        key = 'web:p/Value.class'
        for counters in ({}, {key:{}}, {key:{'LINE':{'missed':1,'covered':1}}}):
            with self.subTest(counters=counters), self.assertRaises(ValueError):
                subject.family(path,dict(allActualClassCounters=counters))
        measured = {k:{'missed':0,'covered':1} for k in ('LINE','METHOD','CLASS')}
        result = subject.family(path,dict(allActualClassCounters={key:measured}))
        self.assertNotIn('BRANCH',result['counters'][key])

    def test_register_rejects_pending_review_formal_promotion_and_wrong_source(self):
        base = dict(source=subject.SOURCE,formalUpdated=False,wholeEffortCompletionRate=None,reviewState='COMPLETE',acceptedBy='test')
        for value in ({**base,'source':'old'},{**base,'reviewState':'PENDING'},{**base,'formalUpdated':True},
                      {**base,'wholeEffortCompletionRate':100}):
            with self.subTest(value=value), self.assertRaises(ValueError):subject.verify_register(value)


if __name__ == '__main__':
    unittest.main()
