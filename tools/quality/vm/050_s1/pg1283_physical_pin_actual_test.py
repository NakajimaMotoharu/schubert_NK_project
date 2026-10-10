import ast
import unittest
from pg1283_physical_pin_actual import BODY, payload, SOURCE


class PhysicalComponentBoundaryTest(unittest.TestCase):
    def test_closed_compiler_failure_and_file_set_refused(self):
        for value in [dict(actualExit=1,source=SOURCE),dict(actualExit=0,source='other'),
                      dict(actualExit=0,source=SOURCE,fileHashes={'../other':'0'*64})]:
            with self.assertRaises(ValueError):payload(value)

    def test_isolated_namespace_and_non_application_scope(self):
        ast.parse(BODY)
        self.assertIn("'--mount','--propagation','private'",BODY)
        self.assertIn("require(observe()==before)",BODY)
        self.assertIn("'applicationRootUnitStartupAccepted':False",BODY)
        self.assertNotIn('systemctl',BODY)
        self.assertNotIn('StartUnit',BODY)
        self.assertNotIn('psql',BODY)
        self.assertIn("r.stdout==expected and not r.stderr",BODY)


if __name__=='__main__':unittest.main()
