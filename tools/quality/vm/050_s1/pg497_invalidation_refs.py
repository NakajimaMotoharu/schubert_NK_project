"""SSC205: fresh M/A/DB canonical invalidation AFTER actual owned handoff.
No live stop, fabricated intent, start or old-scope acceptance. Full bytes private.
"""
import ast,hashlib,json,os,pathlib,stat,subprocess,sys
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg497-canonical-invalidation-v1')
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
ORDER=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']
EXTRA=['schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
FIELDS=set('Id,LoadState,ActiveState,SubState,MainPID,ControlPID,Job,InvocationID,ExecMainCode,ExecMainStatus,Result,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL,Restart,Type,RemainAfterExit'.split(','))
PARENT='52accf6d68f44487b6e0b3635c20396f'
PINS={'pg481_native_owned_stop.py':'99b24d0b0169fd8e7c6075f01096b6efeedaa953ee759e63eaa0e33f64fcb865','pg480_backup_refs.py':'0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7','pg466_term_witness.py':'e257ac5b9dea23ba91f68231717ee787b839f5d08d95fd67d62ac3c20b568a78','pg471_native_term_witness.py':'f6b800cb5597ebfd7348e172f09b708d3813b991f7452ae1c938e9d2fa3866d1'}
HANDOFF=pathlib.Path('/var/lib/pgpt-s1-preservation/pg497-owned-tool-handoff-v1')
def verified_definitions():
 source=pathlib.Path('/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6/pg496_timeout_owned.py').read_bytes()
 if hashlib.sha256(source).hexdigest()!='8f1296267c0f584679cc70aaa0ee6a8f964cad217b75d76c4c9caf1832216ca4':raise ValueError('immutable source differs')
 names={'require','parent_value','epoch_value','command','show','tick','holder','kernel_empty','save','load_definitions','baseline','rows','snapshot','configuration','parent'}
 definitions=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names]
 if len(definitions)!=len(names):raise ValueError('immutable definitions differ')
 class FixedHolder(ast.NodeTransformer):
  def visit_Constant(self,node):
   if node.value==b'Pg496TimeoutRecovery':return ast.copy_location(ast.Constant(b'Pg497CanonicalInvalidation'),node)
   if isinstance(node.value,str):return ast.copy_location(ast.Constant(node.value.replace('PG496-fixed-recovery','PG497-fixed-recovery')),node)
   return node
 module=ast.Module(body=[FixedHolder().visit(n) for n in definitions],type_ignores=[])
 exec(compile(ast.fix_missing_locations(module),'<pinned readonly owner/snapshot definitions>','exec'),globals())
def quiescent():
 parent();owner=holder();record=json.loads((HANDOFF/'complete.private.json').read_text())
 require(record=={'ownedTerm':True,'allOldPeersLocksGone':True,'allTenKernelEmpty':True,'all24RowsAndOriginalValuesUnchanged':True,'source':'38899a05b5c2daeecfc5af8ea5ae748e29954c60','oldCloseNotInferred':True,'currentStillIssued':True,'starts':0,'revoke':0})
 require(not pathlib.Path('/proc/19311').exists())
 values=json.loads((HANDOFF/'before.private.json').read_text())['units']
 for u in ORDER+EXTRA:
  require(show(u)==values[u]);kernel_empty(u)
 require(owner==holder());return values
def main():
 require(os.geteuid()==0 and len(sys.argv)==2 and sys.argv[1] in ['verify','capture','terminal','revoked'])
 load_definitions();values=quiescent();action=sys.argv[1]
 if action=='verify':return
 require(ROOT.is_dir() and ROOT.stat().st_uid==ROOT.stat().st_gid==0 and stat.S_IMODE(ROOT.stat().st_mode)==0o700)
 if action=='capture':
  data=snapshot();require(data==snapshot());save('snapshot-before.private.json',json.dumps(data,sort_keys=True).encode());save('units-before.private.json',json.dumps(values,sort_keys=True).encode());return
 before=json.loads((ROOT/'snapshot-before.private.json').read_text());actual=snapshot()
 if action=='revoked':
  require(epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True));root='/run/schubert-nk/startup';leaf=root+'/epoch.current'
  require(set(before['trees'][root])==set(actual['trees'][root]))
  # Only canonical current content/inode and the containing directory metadata may change.
  for p in [root,leaf]:actual['trees'][root][p]=before['trees'][root][p]
 require(before==actual and quiescent()==values)
 save(action+'.private.json',json.dumps({'allTenKernelEmpty':True,'all24TablesPreserved':True,'starts':0,'stops':0,'intentRetirements':0,'oldCloseNotInferred':True},sort_keys=True).encode())
if __name__=='__main__':
 verified_definitions();main()
