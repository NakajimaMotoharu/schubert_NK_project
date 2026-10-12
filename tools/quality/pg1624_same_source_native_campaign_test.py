"""Independent distinct-session/source baseline and same-session/future/null rejection."""
import copy
import unittest
from pg1624_same_source_native_campaign import qualify_inputs,SOURCE,SERVER

class DistinctCampaignTest(unittest.TestCase):
    def test_two_sources_and_every_session_contract_are_not_inferred(self):
        records=[]
        for cohort in range(2):
            items=[{'index':0,'sessions':1,'sessionIdSha256':format(cohort*8+i+1,'064x'),'startMs':1000,'dumpMs':2000}for i in range(8)]
            records.append({'actualExit':0,'result':{'productionSource':SOURCE,'classByteMismatch':0,'currentNativeSessions':items,'oldNativeImported':False,'qualified1532Tests':3583,'hostOnlyCounters':{'LINE':{'missed':10,'covered':20}}}})
        self.assertEqual(qualify_inputs(records)['distinctSessions'],16);self.assertFalse(qualify_inputs(records)['sameSessionPointUnion'])
        for path,bad in [(('productionSource',),'old-source'),(('classByteMismatch',),1),(('oldNativeImported',),True),(('qualified1532Tests',),1964),(('hostOnlyCounters',),{}),(('currentNativeSessions',),[])]:
            changed=copy.deepcopy(records);changed[1]['result'][path[0]]=bad
            with self.assertRaises(ValueError):qualify_inputs(changed)
        for key,bad in [('sessionIdSha256',records[0]['result']['currentNativeSessions'][0]['sessionIdSha256']),('sessionIdSha256','unknown'),('sessions',2),('sessions',True),('startMs',None),('dumpMs',999),('extra',1)]:
            changed=copy.deepcopy(records);changed[1]['result']['currentNativeSessions'][0][key]=bad
            with self.assertRaises(ValueError):qualify_inputs(changed)
        for value in [None,[],records[:1]]:
            with self.assertRaises(ValueError):qualify_inputs(value)
        self.assertIn('NativeSessions571',SERVER);self.assertIn('classByteMismatch',SERVER)
        self.assertIn('coordinates(xml.read_bytes(),v)',SERVER);self.assertNotIn('ssh',SERVER);self.assertNotIn('systemctl',SERVER)

if __name__=='__main__':unittest.main()
