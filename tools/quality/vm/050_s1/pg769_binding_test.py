"""Independent literal actor/source/post/pair join, foreign/missing/notdone rejected."""
import ast
import copy
import unittest
from pg768_sources_test import fixture
from pg769_final import source


def meta():
    return {'actualExit':0,'batchRows':544,'unitExit20':True,'allNewScopesReturnedNormally':True,
        'beforeSha256':'2'*64,'afterSha256':'3'*64,'invocation':'4'*32,'pid':'3100000','ticks':'14200000','pid1Job':'151111',
        'startMonotonicUs':142000000000,'endMonotonicUs':142001000000,'elapsedSeconds':1.0}


class Test(unittest.TestCase):
    def test_current_literal_actor_and_fullpair(self):
        raw=source(*fixture(),meta());tree=ast.parse(raw)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));ast.parse(payload)
        for v in ('pg768-bootstrap-existing-v1','pg769-bootstrap-final-v1','pg750-manifest.sig','2'*64,'3'*64,'4'*32,'3100000','151111','142000000000','142001000000','142030000000',"'batchRows':544",'native_tree(b[','completion_messages('):self.assertIn(v,raw)
        for v in ('pg737','pg738','25e00f13','0d42d02d','2793207',"'batchRows':534",'pg715-manifest'):self.assertNotIn(v,raw)

    def test_foreign_types_and_bounds_rejected(self):
        for k,v in (('actualExit',False),('batchRows',534),('unitExit20',1),('allNewScopesReturnedNormally',False),('beforeSha256',None),('afterSha256','F'*64),('invocation','0'*32),('pid','0'),('ticks',True),('pid1Job','unknown'),('startMonotonicUs',True),('endMonotonicUs',142030000001),('elapsedSeconds',True)):
            value=copy.deepcopy(meta());value[k]=v
            with self.subTest(k=k),self.assertRaises(AssertionError):source(*fixture(),value)


if __name__=='__main__':unittest.main()
