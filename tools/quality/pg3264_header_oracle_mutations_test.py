"""Mutation runner boundaries, not Production PT."""
import ast
import unittest
from pyflakes.api import check
import pg3264_header_oracle_mutations as subject
import pg3266_header_protocol_regression as normal
import pg3268_header_unissued_transport_resume as recovery
import pg3270_header_protocol_independent as independent


class HeaderMutationToolTest(unittest.TestCase):
    def test_complete_namespace_and_three_literal_faults(self):
        self.assertEqual(0, check('INPUT={}\n' + subject.SERVER, '<header oracle server>'))
        tree = ast.parse(subject.SERVER)
        vectors = next(node.value for node in ast.walk(tree)
                       if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'vectors' for t in node.targets))
        self.assertEqual(5, len(vectors.elts))
        for literal in ['WRONG_EXCEPTION', 'MESSAGE_WIRE', 'INTERACTION_WIRE',
                        'AssertionFailedError', "require(not list(out.rglob('*.exec')))",
                        "'productionPtCredit':0", "'coverageCredit':0"]:
            self.assertIn(literal, subject.SERVER)

    def test_real_production_has_exactly_one_each_fault_site(self):
        expected = [('CommonHeader', 'throw new LayoutValidationException("unsupported protocol identifier");'),
                    ('MessageKind', "RESPONSE('S')"), ('InteractionKind', "SYNCHRONOUS('S')")]
        for name, site in expected:
            path = next(subject.ROOT / p for p in subject.FILES if p.endswith('/' + name + '.java'))
            self.assertEqual(1, path.read_text().count(site))

    def test_related_protocol84_is_actual_xml_and_member_qualified(self):
        raw = normal.server()
        for marker in ['tests==84', 'len(xmls)==17', 'main==174', 'images[0]==images[1]',
                       "count('@Test\\n')==7", "cases=x.findall('testcase')", "'flaky'in n.tag.lower()"]:
            self.assertIn(marker, raw)

    def test_summary_accepts_actual_projection_without_coverage_and_refuses_missing_required(self):
        actual = {'tests': 84, 'suites': 17, 'mainClasses': 174, 'staticIssues': 0,
                  'FESFlakyNotRun': 0, 'startUTC': 'FIXED_START', 'endUTC': 'FIXED_END',
                  'allProtocolMainAndResourcesSameBytes': True}
        self.assertEqual(actual, recovery.public_result_summary(actual))
        self.assertEqual(actual, recovery.public_result_summary({**actual, 'coverage': {'LINE': 'PRIVATE_DETAIL'}}))
        self.assertNotIn('coverage', recovery.public_result_summary(actual))
        incomplete = dict(actual); del incomplete['tests']
        with self.assertRaises(KeyError):
            recovery.public_result_summary(incomplete)

    def test_independent_original_evidence_requires_xml_counters_and_preserves_wrapper_failure(self):
        self.assertEqual(0, check('INPUT={}\n' + independent.SERVER, '<independent Header84>'))
        for marker in ["len(cases)==len(set(cases))==d['tests']==84", "counters==d['coverage']",
                       "'originalWrapperExit':1", "'mavenReissued':False", 'images[0]==images[1]',
                       "headers=={", "sha(authority)==INPUT['manifestSha256']"]:
            self.assertIn(marker, independent.SERVER)


if __name__ == '__main__':
    unittest.main()
