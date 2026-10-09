"""Independent new genuine/current-source/date boundary fixtures, no stop authority."""
import copy,unittest
import pg963_current_stop_binding as p
def fixture():
    return{'actualExit':0,'productionSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','batchRun':'eeae04ea-713c-4f2d-888d-358fb4bed274','cutoff':'2026-10-09T23:31:22.087768Z','activation':'091663ce-1cf4-47e7-8311-218ebb0c8653','genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':202580374989},'beforeSha256':'b'*64,'parentEndedUTC':'2026-10-09T23:51:21.087768Z','ownedUnits':{u:{'MainPID':str(4000000+i),'InvocationID':str(i+1).zfill(32),'ActiveState':'active','SubState':'running'}for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}}
class Test(unittest.TestCase):
    def test_whole_new_source_scope_and_original_clock(self):
        v=p.generate(fixture());j=v['Pg963NativeStop.java'];r=v['pg963_native_refs.py']
        for x in ('40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','eeae04ea-713c-4f2d-888d-358fb4bed274','091663ce-1cf4-47e7-8311-218ebb0c8653','lease.confirmClosed()','maxGapNanos','Pg387TrustedDeployment.LABEL="PG932"'):
            self.assertIn(x,j)
        for x in ('0bb4d6f3b9e74cdc91c553748a4cd018','201380374989','pg960-completed-readonly-v1',"signed_cfg=json.loads(original)['configuration']",'manager.LoadUnit(u);manager.RefUnit(u)','complete_configuration(', 'len(old)==24'):
            self.assertIn(x,r, 'missing references contract: '+x)
        # Receipt checks the deadline as START + the original thirty-minute budget.
        self.assertIn('START+1800000000',v['pg963_parent_receipt.py'])
        for s in v.values():
            for old in ('Pg877','pg877','PG862','e01612fcd7f2752df5ae0836b78538fd5e87f120','19022204-8a9e-418d-ba2a-9967ff923dc2'):self.assertNotIn(old,s)
    def test_foreign_not_genuine_and_owned_fields_refused(self):
        for k,value in (('actualExit',143),('productionSource','0'*40),('batchRun','93cb976e-c36c-47a3-b9e2-0ad28d2996de'),('activation','0dfe0b7f-0e36-4b81-9086-500d896d1187'),('cutoff','2026-10-09T19:07:23.894279Z'),('parentEndedUTC','2026-10-09T23:00:00.000000Z'),('beforeSha256',None)):
            f=fixture();f[k]=value
            with self.assertRaises((ValueError,TypeError)):p.generate(f)
        for k,value in (('genuineRootDone',False),('genuinePid1StartDone',False),('endMonotonicUs',201380374988),('endMonotonicUs',203180374990)):
            f=fixture();f['genuineCompletion'][k]=value
            with self.assertRaises(ValueError):p.generate(f)
        for k,value in (('MainPID','0'),('InvocationID',''),('ActiveState','inactive'),('SubState','exited')):
            f=fixture();f['ownedUnits']['schubert-nk-api.service'][k]=value
            with self.assertRaises(ValueError):p.generate(f)
    def test_utc_midnight_does_not_extend_monotonic_budget(self):
        f=fixture();f['parentEndedUTC']='2026-10-10T00:00:00.000000Z';f['genuineCompletion']['endMonotonicUs']=203180374989
        self.assertTrue(p.bindings(f))
        f['genuineCompletion']['endMonotonicUs']+=1
        with self.assertRaises(ValueError):p.bindings(f)
if __name__=='__main__':unittest.main()
