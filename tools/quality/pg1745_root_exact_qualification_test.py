"""Independent literal XML/schema counterexamples, BUG1159/YKT927."""
import unittest
from pg1745_root_exact_qualification import METHODS, qualified_tests, generated_oracle, server

class Oracle(unittest.TestCase):
    def test_actual_emitted_oracle_and_all_count_failure_boundaries(self):
        names=sorted(METHODS)
        xml='<testsuite tests="8" failures="0" errors="0" skipped="0">'+''.join('<testcase classname="'+v.split(':')[0]+'" name="'+v.split(':')[1]+'"/>' for v in names)+'</testsuite>'
        manifest={'tests':8, **{k:0 for k in ('actualExit','failures','errors','skipped','aborted','notRun','javacWarnings','classByteMismatch')}}
        ns={}; exec(compile(generated_oracle(),'<actual emitted oracle>','exec'),ns)
        for oracle in (qualified_tests, ns['qualified_tests']):
            self.assertEqual(8, oracle(manifest,xml.encode(),METHODS))
            for k in manifest:
                with self.subTest(field=k):
                    bad=dict(manifest); bad[k]=4 if k=='tests' else 1
                    with self.assertRaises(ValueError): oracle(bad,xml.encode(),METHODS)
            for bad in (xml.replace('tests="8"','tests="4"'), xml.replace('failures="0"','failures="1"'), xml.replace('skipped="0"','skipped="1"'), xml.replace(names[-1].split(':')[1],names[0].split(':')[1]), xml.replace(names[-1].split(':')[1],'unknown'), xml.replace('/>','><failure/></testcase>',1)):
                with self.assertRaises(ValueError): oracle(manifest,bad.encode(),METHODS)
            with self.assertRaises(ValueError): oracle(manifest,xml.encode(),set(names[:4]))
        self.assertIn("results['1743']['tests']==8",server())
        self.assertNotIn('PG1744',server())

if __name__ == '__main__': unittest.main()
