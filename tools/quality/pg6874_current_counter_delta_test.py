import copy
import unittest
import pg6874_current_counter_delta as p


class OriginalCounterDeltaTest(unittest.TestCase):
    def fixtures(self):
        keys={p.WEB,p.ACCEPTOR,p.PG,'unchanged'}
        rows={k:{kind:dict(covered=1,missed=0)for kind in('LINE','METHOD','CLASS','BRANCH')}for k in keys}
        rows[p.ACCEPTOR]['BRANCH']['missed']=1;rows[p.PG]['BRANCH']['missed']=2
        a=dict(allPhysicalMainSha256={k:'0'for k in keys},allActualClassCounters=rows,modules={})
        b=copy.deepcopy(a);b['allPhysicalMainSha256'][p.WEB]='1'
        b['allActualClassCounters'][p.WEB]['LINE']['covered']=2
        b['allActualClassCounters'][p.ACCEPTOR]['BRANCH']['missed']=0
        b['allActualClassCounters'][p.PG]['BRANCH']['missed']=1
        return a,b

    def test_only_expected_changed_or_closed_classes(self):
        a,b=self.fixtures();x=p.compare(a,b)
        self.assertEqual([p.ACCEPTOR],x['newlyClosedClasses']);self.assertEqual([],x['reopenedClasses'])

    def test_unrelated_or_missing_actual_counter_is_not_normalized(self):
        a,b=self.fixtures();b['allActualClassCounters']['unchanged']['LINE']['covered']=2
        with self.assertRaises(ValueError):p.compare(a,b)
        a,b=self.fixtures();del b['allActualClassCounters'][p.ACCEPTOR]['BRANCH']
        with self.assertRaises(ValueError):p.compare(a,b)


if __name__=='__main__':unittest.main()
