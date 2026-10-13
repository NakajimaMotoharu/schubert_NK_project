import unittest
from pg2222_root_host_selected import server,FILES


class TwoBoundaries(unittest.TestCase):
    def test_actual_scope_count_and_independent_outputs(self):
        s=server()
        for text in ['PG2222-selected-v1','Pg2222RootHostLauncher',"'tests':'2'",'len(x.findall(\'testcase\'))==2',"'tests':2",'source-full-PG2124']:
            self.assertIn(text,s)
        self.assertNotIn('PG2220',s)
        self.assertIn('tools/quality/vm/050_s1/Pg2222RootHostLauncher.java',FILES)
        self.assertNotIn('PG1618',s)


if __name__=='__main__':unittest.main()
