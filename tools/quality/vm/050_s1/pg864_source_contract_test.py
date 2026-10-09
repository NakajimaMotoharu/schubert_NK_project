"""Whole actual generated profile tuple/entry/scope-order closure, no VM."""
import ast,hashlib
from pg864_completed_sources import sources
values=sources();j=values['Pg864CompletedDeployment.java'];p=values['pg864_completed_refs.py'];ast.parse(p)
for literal in ('0.1.0-PG862','0.1.0-PG832','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977','37356ff23d0393924c22079bd4c87fce7c3070155d84704fb1cb143e7b1c60a5','021111b4-6de5-4733-917d-5ac176240ffc','8b153538-1523-4987-a456-6cbea0d345ee','9de2d03c-28c7-4647-97d9-c66ace06048c','cc9ed874-7f4f-450e-a188-8de1e42c8441'):
 assert literal in j
for literal in ('pg861-runtime841-retired-post-v1/after.private.json','4bd686da5660104c6dc6975baa468fd80a015e5ecfcc3896fc26b4f9e2147579','564','complete_configuration','StageReferences','NamespaceFDs','finite_trees','new-epoch.private'):
 assert literal in p
for obsolete in ('pg751','==534','pg492-once','genuine_receipt','completed().isEmpty()','Pg835Pending','0eece14c'):
 assert obsolete not in j+p
main=j[j.index('public static void main'):]
positions=[main.index(x)for x in ('MaintenanceFileLock.create().tryExclusive','StartupAdmissionFile.create().tryExclusive','var batch=Pg407FailedRootRecovery.openDatabase()','schemaLease=lease(','new References(b,s)','MaintenanceRunFiles.create().execute','prepare(mode)','if(mode.equals("activate"))publish','batch.rollback();batch.close()','schema.rollback();schema.close()','refs.release()','phase="A_CLOSE"','phase="COMPLETE"')]
assert positions==sorted(positions)
t=ast.parse(p);execute=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='execute');body=ast.unparse(execute)
assert body.index('refs.__enter__()')<body.index('fds = NamespaceFDs()')<body.index("print('REF_READY'")
assert body.index('refs.__exit__')<body.index('fds.close()')<body.index("print('REF_RELEASED'")
assert 'Set.of("before","epoch","approval","after")'in j
assert 'if(live)pulse()'in j and 'await("REF_RELEASED",false)'in j
assert 'phase="EPOCH_PUBLISH"'in j and 'phase="APPROVAL_PUBLISH"'in j and 'phase="CURRENT_PUBLISH"'in j
assert 'new StartupPermitRecords.Epoch' in j and 'permits.invalidate(BOOT,fresh,ACTIVATION)'in j
print('DEP864004 complete generated fixed tuple/entry/scope/finite phase closure PASS; management PTadded0')
