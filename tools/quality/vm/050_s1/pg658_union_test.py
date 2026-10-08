"""Source/qualification/single-session/duplicate refusal independent vectors."""
import copy
import unittest
from pg658_same_source_union import admissible,MODULES


class Union(unittest.TestCase):
    def test_two_distinct_same_source_not_other_historical_native(self):
        a={'actualExit':0,'productionSource':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5','currentNativeStreams':8,'selected':[{}for _ in range(8)],'singleSessions':[{'sessions':1,'sessionIdSha256':str(i)}for i in range(8)],'frozenHostManifestSha256':'067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b','moduleCounters':{m:{'classByteMismatch':0}for m in MODULES},'run':'first','hostExecHashes':{m:'same'for m in MODULES}}
        b=copy.deepcopy(a);b['run']='second';b['singleSessions']=[{'sessions':1,'sessionIdSha256':str(i)}for i in range(8,16)]
        self.assertTrue(admissible(a,b))
        for key,value in (('productionSource','0'*40),('actualExit',1),('currentNativeStreams',7),('selected',[]),('singleSessions',a['singleSessions']),('frozenHostManifestSha256','0'*64),('run','first'),('hostExecHashes',{'six':'other'}),('moduleCounters',{'fixed':{'classByteMismatch':1}})):
            bad=copy.deepcopy(b);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):admissible(a,bad)
        bad=copy.deepcopy(b);bad['singleSessions'][0]['sessions']=2
        with self.assertRaises(ValueError):admissible(a,bad)
        for key,value in (('actualExit',False),('moduleCounters',{}),('hostExecHashes',{})):
            bad=copy.deepcopy(b);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):admissible(a,bad)


if __name__=='__main__':unittest.main()
