"""Mutation runner boundaries, not Production PT."""
import ast
import unittest
from pyflakes.api import check
import pg3264_header_oracle_mutations as subject
import pg3266_header_protocol_regression as normal


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


if __name__ == '__main__':
    unittest.main()
