"""Full actual seventeen input graph remains latest-only, no oracle replay or phantom gain."""
import unittest
import pg1415_readiness_latest_counter as p

class Test(unittest.TestCase):
    def test_generated_input_and_proof_join(self):
        raw=p.source()
        for s in ('pg1411-latest-closing-counter-v1','pg1414-batch-boundary-selected-v1','pg1415-readiness-latest-counter-v1','len(data)==17','bootstrap-0.exec\'not in data','monotonicProofReusedFrom','ArtemisRoleReadinessClient','MorningServiceReadiness',"'freshSelectedTests':11",'gainVs1411'):
            self.assertIn(s,raw)
        self.assertNotIn('NativeClosingSelect1411Test\']',raw)
        self.assertNotIn('subprocess.run(args,stdout=log',raw)
        compile(raw,'<actual latest-only readiness graph>','exec')

if __name__=='__main__':unittest.main()
