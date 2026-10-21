import ast
import unittest
import pg6330_outbox_graph_whole as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_actual4048_declarations_preserve_existing_repeated_case(self):
        self.assertEqual((4048,607),subject.declared_inventory())

    def test_new_only_namespace_actual_dimensions_and_no_held_operations(self):
        raw=subject.server_source('a'*40,'0'*64);tree=ast.parse(raw)
        for value,count in ((4048,2),(607,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6330',raw);self.assertNotIn('source-full-PG6188',raw)
        for token in ('systemctl','qemu-system','/opt/schubert-nk/current','--recover','--resume'):
            self.assertNotIn(token,raw)

    def test_original89_and_four_boundary_proof_first(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4048, 'suites': 607, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw);self.assertIn('SSC322323 ordinary API-Web',raw)
        values=subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6326-web-graph-qualification-v1/manifest.json',values)
        self.assertIn('PG6328-outbox-graph-order-v1/manifest.json',values)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
