import unittest
import hashlib
import pg6759_owned_counter_delta as p


def counters(miss=0):return {k:dict(covered=1,missed=miss)for k in p.KINDS}


class ActualCounterComparisonTest(unittest.TestCase):
    def test_exact_delta_without_branchless_or_zero_as100(self):
        b={'a':counters(1),'b':{'LINE':dict(covered=1,missed=0)},'c':counters(0)}
        a={'a':counters(0),'b':b['b'],'c':counters(1)}
        x=p.compare(b,a)
        self.assertEqual(['a'],x['newlyMeasuredFour100']);self.assertEqual(['c'],x['noLongerMeasuredFour100'])
        self.assertEqual((1,1),(x['beforeExplicitFour100'],x['afterExplicitFour100']))
        z=counters();z['BRANCH']['covered']=0;self.assertFalse(p.four_closed(z))

    def test_class_scope_change_cannot_be_counted_as_improvement(self):
        with self.assertRaises(ValueError):p.compare({'a':counters()},{'b':counters()})

    def test_exact_new_design_ids_cannot_join_missing_or_ambiguous_cases(self):
        rows=[dict(module='bootstrap' if 'bootstrap' in cls else 'batch',source='s',testId='actual-'+str(i),
          **{'class':cls},caseNameSha256=hashlib.sha256((method+'()').encode()).hexdigest(),xmlSha256='0'*64)
          for i,(_,cls,method)in enumerate(p.DESIGN_CASES)]
        self.assertEqual(5,len(p.design_trace(rows)))
        for wrong in (rows[:-1],rows+[rows[0]]):
            with self.assertRaises(ValueError):p.design_trace(wrong)


if __name__=='__main__':unittest.main()
