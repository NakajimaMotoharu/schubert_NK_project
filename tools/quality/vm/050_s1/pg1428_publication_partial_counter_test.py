import unittest
import pg1428_publication_partial_counter as p

class Test(unittest.TestCase):
    def test_partial_observation_not_guessed_method_closure(self):
        good={'LINE':2,'METHOD':2,'CLASS':0,'BRANCH':0}
        self.assertEqual(good,p.partial(good))
        other={'LINE':5,'METHOD':3,'CLASS':0,'BRANCH':0}
        self.assertEqual(other,p.partial(other))
        for bad in (None,{},dict(good,LINE=-1),dict(good,METHOD=True),dict(good,LINE=None),dict(good,CLASS=1),dict(good,BRANCH=1),dict(good,UNKNOWN=0)):
            with self.assertRaises(ValueError):p.partial(bad)

    def test_actual_nineteen_inputs_native_pending_and_failed_slot_preserved(self):
        raw=p.source()
        self.assertIn('partial({k:counts[k]for k in kinds})',raw)
        self.assertIn('len(data)==19',raw)
        self.assertIn('observedPartialClasses',raw)
        self.assertIn("'coverage100':False",raw)
        self.assertIn('pg1428-publication-partial-counter-v1',raw)
        self.assertNotIn('pg1427-publication-latest-counter-v1',raw)
        self.assertIn('bootstrap-0.exec\'not in data',raw)
        compile(raw,'<fixed partial graph>','exec')

if __name__=='__main__':unittest.main()
