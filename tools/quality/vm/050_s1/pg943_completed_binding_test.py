"""Independent whole generated profile, not filename-only checks or borrowed old result."""
import ast,unittest
from pg942_completed_sources import sources
class Test(unittest.TestCase):
    def test_current_genuine_issued_and_exact_signed_source(self):
        v=sources();j=v['Pg942CompletedDeployment.java'];p=v['pg942_completed_refs.py'];ast.parse(p)
        for literal in ('93cb976e-c36c-47a3-b9e2-0ad28d2996de','0dfe0b7f-0e36-4b81-9086-500d896d1187','22ba4479-64b2-4a3c-b2f9-ba720045e821','2026-10-09T19:07:23.894279Z','2026-10-09T19:31:23.759513Z','2913a5e9001f1e16431499005a37dfec3ce5476a21e907ef3dfd95793fe638fd','09c13154c30c568c19323eef91bf1a8a2037236abaabbf9ce5b39888c966cfc7','40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','0.1.0-PG932','0.1.0-PG862'):
            self.assertIn(literal,j)
        self.assertIn('initial?StartupPermitRecords.State.ISSUED:StartupPermitRecords.State.INVALID',j)
        for obsolete in ('9de2d03c','021111b4','8b153538','pg864','Pg864','PG832','==564','== 564'):
            self.assertNotIn(obsolete,j+p)
        for literal in ('pg935-current-preflight-v1/after.private.json','4aa97f5a256d8d74283f83310b6c8e042dc0f8ca0bcd957bc68abed2fce257cb',"baseline['trees'] = retained_trees(baseline)",'expected_old_approval','==584','StageReferences','NamespaceFDs','finite_trees','new-epoch.private'):
            self.assertIn(literal,p)
    def test_all_entry_scope_dynamic_slots_and_capture_before_release(self):
        v=sources();j=v['Pg942CompletedDeployment.java'];p=v['pg942_completed_refs.py']
        main=j[j.index('public static void main'):]
        points=[main.index(x)for x in ('MaintenanceFileLock.create().tryExclusive','StartupAdmissionFile.create().tryExclusive','var batch=Pg407FailedRootRecovery.openDatabase()','schemaLease=lease(','new References(b,s)','MaintenanceRunFiles.create().execute','prepare(mode)','if(mode.equals("activate"))publish','batch.rollback();batch.close()','schema.rollback();schema.close()','refs.release()','phase="A_CLOSE"','phase="COMPLETE"')]
        self.assertEqual(sorted(points),points)
        self.assertIn('save=BASE.resolve("pg942-"+mode+"-v1")',j)
        tree=ast.parse(p);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='execute');body=ast.unparse(fn)
        self.assertLess(body.index('refs.__enter__()'),body.index('fds = NamespaceFDs()'))
        self.assertLess(body.index('refs.__exit__'),body.index('fds.close()'))
        slots=[n for n in ast.walk(fn)if isinstance(n,ast.Compare)and any(isinstance(t,ast.Tuple)and any(isinstance(x,ast.Constant)and isinstance(x.value,str)and 'prepare-ro' in x.value for x in t.elts)for t in n.comparators)]
        self.assertEqual(1,len(slots));self.assertEqual(tuple('/var/lib/pgpt-s1-preservation/pg942-'+m+'-v1'for m in ('prepare-ro','verify','activate')),ast.literal_eval(slots[0].comparators[0]))
        for literal in ('if(live)pulse()','await("REF_RELEASED",false)','new StartupPermitRecords.Epoch','permits.invalidate(BOOT,fresh,ACTIVATION)','!fresh.equals(BOOT)','!fresh.equals(ACTIVATION.id())'):
            self.assertIn(literal,j)
        for name in ('Pg797OwnedDatabase.java','Pg798DatabaseScope.java'):self.assertIn(name,v)
        for forbidden in ('StartUnit','StopUnit','RestartUnit','daemon-reload','--resume','completed().isEmpty()'):
            self.assertNotIn(forbidden,j+p)
if __name__=='__main__':unittest.main()
