"""Full generated dispatch literal stage/phase guards, no stage or VM execution."""
import ast,unittest
from pg947_completed_native import source
class Test(unittest.TestCase):
    def test_every_phase_uses_same_frozen_genuine_profile(self):
        raw=source();ast.parse(raw)
        for literal in ('pg945-frozen-v1.safe.json','PG945-compile-v1','pg942-completed-tools-v1','pg942-stage-v1',"stage['run']=='PG942-stage-v1'",'pg942-prepare-ro-v1.safe.json','pg942-verify-v1.safe.json',"'oldGenuineParentProvenanceRequired':True,'newCandidateParentAccepted':False",'Pg942CompletedDeploymentTest',"prefix+'Pg942CompletedDeployment '+action"):
            self.assertIn(literal,raw)
        for forbidden in ('-v2','pg864','Pg864','PG864','PG832','pg942-frozen-v1.safe.json'):
            self.assertNotIn(forbidden,raw)
        self.assertIn("action=sys.argv[1]",raw);self.assertIn("('stage','prepare-ro','verify','activate')",raw)
        self.assertIn("base=W/('pg942-'+action+'-v1')",raw)
        self.assertIn("for s in ('.private.log','.safe.json','.exit')",raw)
        self.assertIn('seen==set(FILES)',raw);self.assertIn("'payload-sha256.json'",raw)
if __name__=='__main__':unittest.main()
