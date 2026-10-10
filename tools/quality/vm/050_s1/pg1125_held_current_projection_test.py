"""Real-shaped four ancestors plus full release records; independent strict faults."""
import copy
import unittest
from pg1125_held_current_projection import project


class ProjectionTest(unittest.TestCase):
    def fixture(self):
        # Independent shape: direct namespace is NOT this full fd-held list.
        group=[
            ['/',[1,2,0,0,16877,19,4096,10,10],[],None],
            ['opt',[1,3,0,0,16877,10,4096,10,10],[],None],
            ['schubert-nk',[1,4,0,0,16877,3,4096,10,10],[],None],
            ['releases',[1,5,0,0,16877,4,4096,10,10],[],None],
            ['0.1.0-PG1068',[1,6,0,0,16877,3,4096,10,10],[],None],
            ['VERSION',[1,7,0,0,33060,1,13,10,10],[],'a'*64],
            ['api',[1,8,0,0,16877,2,4096,10,10],[],None],
            ['api.jar',[1,9,0,0,33060,1,10,10,10],[],'b'*64]]
        now={'':{'metadata':[1,6,0,0,16877,3,4096,10,10],'sha256':None},
             'VERSION':{'metadata':[1,7,0,0,33060,1,13,10,10],'sha256':'a'*64},
             'api':{'metadata':[1,8,0,0,16877,2,4096,10,10],'sha256':None},
             'api/api.jar':{'metadata':[1,9,0,0,33060,1,10,10,10],'sha256':'b'*64}}
        ancestors=[dict(name=name,value=dict(metadata=copy.deepcopy(md),sha256=None))
                   for name,md,_,_ in group[:4]]
        return group,now,ancestors,'0.1.0-PG1068'

    def test_full_held_schema_not_direct_namespace(self):
        args=self.fixture();before=copy.deepcopy(args)
        value=project(*args)
        self.assertEqual(set(value),{'','VERSION','api','api/api.jar'})
        self.assertEqual(value['api/api.jar'],dict(metadata=[1,9,0,0,33060,1,10,10,10],
                          sha256='b'*64,acl=[],target=None))
        self.assertEqual(args,before)

    def test_all_nine_metadata_and_name_hash_acl_rejected(self):
        for index in range(9):
            args=list(self.fixture());args[0][-1][1][index]+=1
            with self.subTest(index=index),self.assertRaises(ValueError):project(*args)
        for field,bad in [(0,'wrong'),(2,['foreign']),(3,'c'*64)]:
            args=list(self.fixture());args[0][-1][field]=bad
            with self.assertRaises(ValueError):project(*args)
        args=list(self.fixture());args[0][4][0]='0.1.0-PG932'
        with self.assertRaises(ValueError):project(*args)

    def test_missing_extra_reorder_null_unknown_parent(self):
        args=list(self.fixture());args[0][-2:]=reversed(args[0][-2:])
        with self.assertRaises(ValueError):project(*args)
        args=list(self.fixture());args[0].pop()
        with self.assertRaises(ValueError):project(*args)
        args=list(self.fixture());args[1]['extra']={}
        with self.assertRaises(ValueError):project(*args)
        for index in range(3):
            args=list(self.fixture());args[index]=None
            with self.assertRaises(ValueError):project(*args)
        args=list(self.fixture());args[2][1]['name']='unknown'
        with self.assertRaises(ValueError):project(*args)


if __name__=='__main__':unittest.main()
