"""Independent literal artifact/path/class/module negative tests. Management only."""
import copy
import unittest
from pg548_candidate_contract import artifacts,verify_delta


class Candidate(unittest.TestCase):
    def test_closed_artifact_inputs(self):
        good=[{'path':'assets/f'+str(i),'size':i,'sha256':'a'*64}for i in range(187)]
        self.assertEqual(len(artifacts(good)),187)
        for value in(None,good[:-1],good+[good[0]]):
            with self.assertRaises(ValueError):artifacts(value)
        for field,value in(('path',None),('path','/etc/key'),('path','../key'),('path','a/../key'),('path','a//key'),('path','a/./key'),('path','a\\key'),('path','assets/f1'),('size',True),('size',-1),('size',None),('sha256','g'*64),('sha256','a'*63),('sha256',None)):
            bad=copy.deepcopy(good);bad[0][field]=value
            with self.assertRaises(ValueError):artifacts(bad)

    def test_only_approved_constructor_delta(self):
        old={m:{'x.class':'a'}for m in('protocol','storage','bootstrap','api','web','batch')}
        name='dev/codex/schubert/nk/batch/file/MorningCompletionEvidence.class'
        old['batch'][name]='b';new=copy.deepcopy(old);new['batch'][name]='c'
        self.assertEqual(verify_delta(old,new),7)
        for group in('missing_module','extra_module','missing_class','extra_class','another_change','no_change'):
            bad=copy.deepcopy(new)
            if group=='missing_module':del bad['web']
            elif group=='extra_module':bad['foreign']={'z.class':'a'}
            elif group=='missing_class':del bad['api']['x.class']
            elif group=='extra_class':bad['api']['foreign.class']='a'
            elif group=='another_change':bad['web']['x.class']='d'
            else:bad['batch'][name]='b'
            with self.assertRaises(ValueError):verify_delta(old,bad)


if __name__=='__main__':unittest.main()
