"""Before-image deletion identities/content never guessed from current totals."""
import unittest
from pg1769_next_day_rows_oracle import oracle_source,payload


class Rows(unittest.TestCase):
    def test_actual_emitted_delta_exactness(self):
        env={};exec(oracle_source(),env);delta=env['delta']
        old=[{'id':1,'value':'kept'},{'id':2,'value':'expired'}]
        self.assertEqual([],delta(old,[old[0]],'id',['2']))
        for new,expected in [([],['2']),([{'id':1,'value':'changed'}],['2']),([old[0]],[]),([old[0],old[0]],['2'])]:
            with self.assertRaises(ValueError):delta(old,new,'id',expected)
        self.assertIn('begin isolation level repeatable read read only',payload())


if __name__=='__main__':unittest.main()
