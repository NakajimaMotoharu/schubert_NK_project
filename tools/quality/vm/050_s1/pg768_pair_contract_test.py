"""Independent SSC234 pairtree literals, not authority to accept native probes/session."""
import copy
from pathlib import Path
import unittest
import pg768_bootstrap_contract as p

ROLE='/run/schubert-nk/pt-coverage/ordinary-bootstrap196'


def fixture():
    before={ROLE:{'metadata':[17,23,999,981,0o40700,2,4096,100,100],'sha256':None},
        ROLE+'/old.terminal.exec':{'metadata':[17,24,999,981,0o100600,1,50,100,100],'sha256':'b'*64}}
    actual=copy.deepcopy(before);actual[ROLE]['metadata'][7:]=[200,200]
    for i,point in enumerate(('terminal','closing')):
        actual[ROLE+'/'+'a'*32+'.'+point+'.exec']={'metadata':[17,25+i,999,981,0o100600,1,80,200,200],'sha256':str(i+1)*64}
    return before,actual


class Test(unittest.TestCase):
    def test_unchanged_non_native_contract_and_idle(self):
        root=Path(__file__).resolve().parent
        self.assertEqual((root/'pg535_bootstrap_contract.py').read_text().split('def native_tree(')[0],
                         (root/'pg768_bootstrap_contract.py').read_text().split('def completion_messages(')[0])
        before,_=fixture();p.native_tree(before,copy.deepcopy(before))
        with self.assertRaises(ValueError):p.native_tree(before,fixture()[1])

    def test_exact_two_new_files_preserve_old_and_each_boundary(self):
        before,actual=fixture();p.native_tree(before,actual,'a'*32)
        for point in ('terminal','closing'):
            path=ROLE+'/'+'a'*32+'.'+point+'.exec'
            for size in (5,16777216):
                bad=copy.deepcopy(actual);bad[path]['metadata'][6]=size;p.native_tree(before,bad,'a'*32)
            for key,value in ((2,0),(3,0),(4,0o100644),(5,2),(6,4),(6,16777217)):
                bad=copy.deepcopy(actual);bad[path]['metadata'][key]=value
                with self.assertRaises(ValueError):p.native_tree(before,bad,'a'*32)
            for sha in (None,'x',True):
                bad=copy.deepcopy(actual);bad[path]['sha256']=sha
                with self.assertRaises(ValueError):p.native_tree(before,bad,'a'*32)
            bad=copy.deepcopy(actual);del bad[path]
            with self.assertRaises(ValueError):p.native_tree(before,bad,'a'*32)
        for mode in ('extra','oldbyte','diridentity','sameinode'):
            bad=copy.deepcopy(actual)
            if mode=='extra':bad[ROLE+'/foreign.exec']=bad[ROLE+'/old.terminal.exec']
            if mode=='oldbyte':bad[ROLE+'/old.terminal.exec']['sha256']='c'*64
            if mode=='diridentity':bad[ROLE]['metadata'][1]=999
            if mode=='sameinode':bad[ROLE+'/'+'a'*32+'.closing.exec']['metadata'][1]=25
            with self.subTest(mode=mode),self.assertRaises(ValueError):p.native_tree(before,bad,'a'*32)
        for bad in ('0'*32,'A'*32,'b'*32,'',True):
            with self.assertRaises(ValueError):p.native_tree(before,actual,bad)
        for bad in (None,{},[]):
            with self.assertRaises(ValueError):p.native_tree(bad,actual,'a'*32)

    def test_both_completion_markers_once_in_order(self):
        values=['Initial ADMIN bootstrap finished','Bootstrap fixed PT native capture complete','Bootstrap fixed PT native closing complete']
        p.completion_messages(values);p.completion_messages(['safe outer diagnostic',*values])
        for bad in (None,[],values[:2],values[1:],values[::-1],values+[values[1]],values+['Initial ADMIN bootstrap failed'],[None,*values]):
            with self.assertRaises(ValueError):p.completion_messages(bad)


if __name__=='__main__':unittest.main()
