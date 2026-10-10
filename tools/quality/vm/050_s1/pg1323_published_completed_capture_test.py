import unittest
from pg1323_published_completed_capture import compose,ROLES

class PublishedCaptureTest(unittest.TestCase):
    def test_complete_actual_full_capture_source_genuine_guard_and_limited_oracle(self):
        owned={u:('800001','a'*32,7400000)for u in ROLES}
        code=compose(owned,74254946447);compile(code,'<actual full new-source capture>','exec')
        self.assertIn('published-completed-capture-v1',code)
        self.assertIn('pg1319-published-ordinary-before-v1',code)
        self.assertIn('proof.result[\'endMonotonicUs\']==74254946447',code)
        self.assertIn('complete_configuration',code)
        self.assertIn('businessFullOraclePending',code)
        self.assertTrue("summary['independentProgress']"not in code)
        self.assertNotIn('d5b00104280028d9ea81b44c1d1c805f3c2861ed',code)
        for value,end in [(None,74254946447),({},74254946447),(owned,None),(owned,75454946448),(owned,True)]:
            with self.assertRaises(ValueError):compose(value,end)
        for bad in [(None,'a'*32,7400000),('0','a'*32,7400000),('800001','wrong',7400000),('800001','a'*32,7365494)]:
            value=dict(owned);value['caddy.service']=bad
            with self.assertRaises(ValueError):compose(value,74254946447)

if __name__=='__main__':unittest.main()
