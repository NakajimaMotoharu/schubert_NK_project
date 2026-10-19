"""Pre-dispatch full-source generation checks only; no server auth/job/VM operations."""
import ast
import unittest
from pyflakes.api import check
import pg5754_private_contract_whole as entry


class CoherentWholeGenerationTest(unittest.TestCase):
    def test_standalone_actual_inventory_and_no_runtime_operation(self):
        raw=entry.server_source(entry.SOURCE,'0'*64);tree=ast.parse(raw)
        values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and type(n.value)is int]
        self.assertIn(3932,values);self.assertIn(581,values);self.assertIn(1664,values)
        self.assertNotIn(3908,values);self.assertNotIn(563,values)
        self.assertEqual(0,check(raw,'<coherent generated runner>'))
        self.assertNotIn('systemctl',raw);self.assertNotIn('qemu-system',raw)

    def test_new_only_driver_preserves_source_and_planned_inventory(self):
        raw=entry.driver_source({'host':'PREFLIGHT_NOT_EXECUTED','matchingActiveJobs':[]})
        self.assertIn("'tests': 3932, 'suites': 581, 'mainClasses': 1664",raw)
        self.assertIn('pg5754-private-contract-six-v1',raw)
        self.assertIn('pg5754-full.py',raw)
        self.assertIn('replayAllowed',raw)


if __name__=='__main__':unittest.main()
