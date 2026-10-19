"""No dispatch: exact inventory/namespace and new-only driver binding before whole execution."""
import ast
import unittest
from pyflakes.api import checkPath
import pg5716_exec_generation_whole as entry


class Whole(unittest.TestCase):
    def test_complete_new_namespace_and_exact_inventory(self):
        raw=entry.server_source(entry.SOURCE,'0'*64)
        self.assertEqual(0,checkPath(entry.__file__))
        self.assertEqual(0,checkPath(__file__))
        self.assertIn(entry.SOURCE,raw)
        constants=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        self.assertIn(3908,constants);self.assertNotIn(3905,constants)
        driver=entry.driver_source({'matchingActiveJobs':[]})
        self.assertIn("'tests': 3908, 'suites': 563, 'mainClasses': 1664",driver)
        self.assertIn('pg5716',driver);self.assertNotIn('pg5588',driver)
        self.assertIn('failed0ea Root30 preserved',driver)
        self.assertTrue(callable(entry.previous.previous.previous.preflight))
        self.assertTrue(callable(entry.previous.previous.previous.previous.driver.main))


if __name__=='__main__':unittest.main()
