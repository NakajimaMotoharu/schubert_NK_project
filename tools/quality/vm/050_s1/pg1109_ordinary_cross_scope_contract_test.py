"""Literal independent shared-ancestor graph; all other fields/bytes remain exact."""
import copy
import stat
import unittest
from pg1109_ordinary_cross_scope_contract import compare


def baseline():
    regular=['signed',[7,52,0,0,stat.S_IFREG|0o400,1,64,11,11],[],'2'*64]
    private=['pgpt-s1-preservation',[7,51,0,0,stat.S_IFDIR|0o700,4,4096,10,10],[],None]
    run=['run',[12,41,0,0,stat.S_IFDIR|0o755,20,560,10,10],[],None]
    inventories=[[copy.deepcopy(regular)]for _ in range(7)]
    for i in (3,4):inventories[i]=[copy.deepcopy(regular)for _ in range(3)]+[copy.deepcopy(private),copy.deepcopy(regular)]
    inventories[6]=[copy.deepcopy(regular),run,copy.deepcopy(regular)]
    return {'snapshot':{'tables':24,'current':'fixed'},'heldWholeMetadata':inventories}


def observed():
    v=baseline();v['heldWholeMetadata'][6][1][1][7:]=[21,21]
    for i in (3,4):v['heldWholeMetadata'][i][3][1][5]=7;v['heldWholeMetadata'][i][3][1][7:]=[22,22]
    return v


class CrossScope(unittest.TestCase):
    def test_only_explicit_known_effects_and_no_input_rebase(self):
        old=baseline();new=observed();saved=copy.deepcopy(new)
        self.assertTrue(compare(old,new,20,30,True));self.assertEqual(saved,new)
    def test_each_ancestor_identity_security_size_time_and_signed_row_refuses(self):
        for i in range(9):
            v=observed();v['heldWholeMetadata'][6][1][1][i]+=100
            with self.assertRaises(ValueError):compare(baseline(),v,20,30,True)
        for inv,row in ((0,0),(3,4),(6,2)):
            for field in range(9):
                v=observed();v['heldWholeMetadata'][inv][row][1][field]+=1
                with self.assertRaises(ValueError):compare(baseline(),v,20,30,True)
        v=observed();v['heldWholeMetadata'][3][4][3]='3'*64
        with self.assertRaises(ValueError):compare(baseline(),v,20,30,True)
    def test_null_unknown_missing_scope_and_absent_private_proof_refuse(self):
        for old,new,b,e,p in ((None,observed(),20,30,True),(baseline(),None,20,30,True),
          (baseline(),observed(),20,30,False),(baseline(),observed(),31,30,True)):
            with self.assertRaises(ValueError):compare(old,new,b,e,p)
        v=observed();v['snapshot']['tables']=23
        with self.assertRaises(ValueError):compare(baseline(),v,20,30,True)


if __name__=='__main__':unittest.main()
