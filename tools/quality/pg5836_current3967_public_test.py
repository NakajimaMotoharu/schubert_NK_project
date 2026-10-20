import ast
import unittest
from pg5836_current3967_public import payload
from pg5832_whole_observation import observer_source,SOURCE


class Original3967ReadersTest(unittest.TestCase):
    def test_projection_and_observer_do_not_invoke_tests_or_held_runtime(self):
        raw=payload({});values=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        self.assertIn(3967,values);self.assertNotIn(3955,values)
        self.assertIn('source-full-PG5832',raw);self.assertNotIn('PG5808',raw)
        observer=observer_source({'source':SOURCE,'tests':3967,'suites':590,'mainClasses':1666,'archiveSha256':'a'*64})
        self.assertIn('pg5832-full.py',observer);self.assertNotIn('pg5754',observer)
        for text in('systemctl','mvnw','qemu-system','sudo ','recover','resume'):
            self.assertNotIn(text,raw);self.assertNotIn(text,observer)


if __name__=='__main__':unittest.main()
