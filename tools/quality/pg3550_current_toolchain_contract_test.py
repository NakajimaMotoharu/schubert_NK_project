import copy
import unittest
from pg3550_current_toolchain_contract import verify_graph, EXPECTED


class ModuleBoundary(unittest.TestCase):
    def test_literal_allowed_graph(self):
        self.assertTrue(verify_graph(copy.deepcopy(EXPECTED)))

    def test_null_missing_illegal_webapi_storagejdbc_or_cycle_refused(self):
        examples=[None,{}]
        for left,right in [('web','api'),('storage','bootstrap'),('bootstrap','api')]:
            graph=copy.deepcopy(EXPECTED);graph[left].add(right);examples.append(graph)
        graph=copy.deepcopy(EXPECTED);graph['storage'].add('postgresql');examples.append(graph)
        for graph in examples:
            with self.assertRaises(ValueError):verify_graph(graph)


if __name__=='__main__':unittest.main()
