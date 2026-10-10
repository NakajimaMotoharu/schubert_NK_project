"""Independent literal vectors: no Production codec/actual-derived expected."""
import copy
import unittest
from pg1083_cold_publication_contract_test import fixture,actual,E,C
from pg1097_partial_exchange_contract import partial


def pending():
    result=actual('after');old=copy.deepcopy(fixture()[C][C+'/current']);old['metadata'][8]=23
    result[C][C+'/pg1088-current.part']=old
    return result


class Partial(unittest.TestCase):
    def test_fixed_pending_exchange_preserves_old_identity_and_all_public_values(self):
        self.assertTrue(partial(fixture(),pending(),E,20,30))

    def test_old_nine_fields_acl_target_hash_and_unknown_entries_refuse(self):
        for index in range(9):
            v=pending();v[C][C+'/pg1088-current.part']['metadata'][index]+=100
            with self.assertRaises(ValueError):partial(fixture(),v,E,20,30)
        for field,value in [('acl',['foreign']),('target','/foreign'),('sha256','0'*64)]:
            v=pending();v[C][C+'/pg1088-current.part'][field]=value
            with self.assertRaises(ValueError):partial(fixture(),v,E,20,30)
        v=pending();v[C][C+'/unknown']=copy.deepcopy(v[C][C+'/pg1088-current.part'])
        with self.assertRaises(ValueError):partial(fixture(),v,E,20,30)

    def test_null_missing_epoch_and_old_current_refuse(self):
        for value in (None,{},actual('after'),actual('before')):
            with self.assertRaises(ValueError):partial(fixture(),value,E,20,30)
        with self.assertRaises(ValueError):partial(fixture(),pending(),None,20,30)


if __name__=='__main__':unittest.main()
