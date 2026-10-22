"""Management negative checks only; no Production execution or external resource."""
import copy
import hashlib
import unittest
from unittest.mock import patch

import pg6958_recovery_catalog as subject


class RecoveryCatalogTest(unittest.TestCase):
    def test_join_rejects_old_source_missing_and_duplicate_original(self):
        selector = 'protocol:transport.BrokerTopologyTest'
        text = 'import org.junit.jupiter.api.Test;\nclass Example {\n  @Test\n  void fixedVector() {}\n}\n'
        row = dict(module='protocol', **{'class':'dev.codex.schubert.nk.protocol.transport.BrokerTopologyTest'},
                   source=subject.SOURCE, result='PASS_ORIGINAL_XML', testId='original-one',
                   caseNameSha256=hashlib.sha256(b'fixedVector').hexdigest())
        self.assertEqual('fixedVector', subject.join_suite(selector, text, [row])[0]['method'])
        for changed in ([], [row, row], [{**row, 'source':'old'}], [{**row, 'result':'SKIPPED'}],
                        [{**row, 'caseNameSha256':hashlib.sha256(b'other').hexdigest()}]):
            with self.subTest(original=changed), self.assertRaises(ValueError):
                subject.join_suite(selector, text, changed)

    def test_branchless_is_absent_not_fabricated_one_hundred(self):
        path = 'src/schubert-nk-protocol/src/main/java/p/Value.java'
        counter = {k:dict(missed=0, covered=1) for k in ('LINE','METHOD','CLASS')}
        q = dict(allActualClassCounters={'protocol:p/Value.class':counter})
        result = subject.family_counters(path, q)
        self.assertNotIn('BRANCH', result['counters']['protocol:p/Value.class'])
        self.assertEqual('NOT_APPLICABLE_NOT_SYNTHESIZED', result['absentCounters'])
        bad = copy.deepcopy(q)
        bad['allActualClassCounters']['protocol:p/Value.class']['METHOD']['missed'] = 1
        with self.assertRaises(ValueError):
            subject.family_counters(path, bad)
        with self.assertRaises(ValueError):
            subject.family_counters(path, dict(allActualClassCounters={}))

    def test_package_declaration_is_not_executable_coverage(self):
        result = subject.family_counters('src/any/package-info.java', dict(allActualClassCounters={}))
        self.assertEqual({}, result['counters'])
        self.assertEqual('PACKAGE_ANNOTATION_NO_EXECUTABLE_METHOD', result['applicability'])

    def test_zero_executable_counter_and_unknown_counter_are_refused(self):
        path = 'src/schubert-nk-protocol/src/main/java/p/Value.java'
        base = {k:dict(missed=0, covered=1) for k in ('LINE','METHOD','CLASS','BRANCH')}
        for key in ('LINE','METHOD','CLASS'):
            value = copy.deepcopy(base)
            value[key]['covered'] = 0
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.family_counters(path, dict(allActualClassCounters={'protocol:p/Value.class':value}))
        value = {**base, 'UNKNOWN':dict(missed=0, covered=1)}
        with self.assertRaises(ValueError):
            subject.family_counters(path, dict(allActualClassCounters={'protocol:p/Value.class':value}))

    def test_registry_does_not_promote_wrong_source_formal_or_effort(self):
        base = dict(source=subject.SOURCE, formalUpdated=False, wholeEffortCompletionRate=None)
        for changed in ({**base,'source':'old'}, {**base,'formalUpdated':True},
                        {**base,'wholeEffortCompletionRate':100}):
            with self.subTest(value=changed), self.assertRaises(ValueError):
                subject.verify_register(changed)

    def test_interface_without_actual_counter_requires_explicit_contract(self):
        path = 'src/schubert-nk-protocol/src/main/java/p/LayoutPayload.java'
        with patch.object(subject, 'ROOT') as root:
            root.__truediv__.return_value.read_text.return_value = 'public sealed interface LayoutPayload {}'
            result = subject.family_counters(path, dict(allActualClassCounters={}))
            self.assertEqual('ABSTRACT_INTERFACE_NO_EXECUTABLE_METHOD', result['applicability'])
            root.__truediv__.return_value.read_text.return_value = 'public class LayoutPayload {}'
            with self.assertRaises(ValueError):
                subject.family_counters(path, dict(allActualClassCounters={}))


if __name__ == '__main__':
    unittest.main()
