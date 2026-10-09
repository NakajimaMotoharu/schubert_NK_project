"""Fixed source102 code-only pending9de2 deployment; completed-source path is forbidden."""
import ast
from pathlib import Path
from pg798_probe_sources import helper as readonly_helper

R=Path(__file__).resolve().parent
SOURCE='102cdf1d365ab321f74b523237590eee764ae858'
DIGEST='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'
OLD_SOURCE='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'
OLD_DIGEST='a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'


def java():
    raw=(R/'Pg498PendingDeployment.java').read_text().replace('Pg498PendingDeployment','Pg799PendingDeployment').replace('pg498','pg799').replace('PG498','PG799').replace('pg799-pending-tools-v2','pg799-pending-tools-v1')
    raw=raw.replace('PG495','PG796').replace('pg495','pg796').replace('PG489','PG750')
    raw=raw.replace('f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44',DIGEST).replace('652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c',OLD_DIGEST)
    raw=raw.replace('Pg490PendingMigration.RUN','UUID.fromString("9de2d03c-28c7-4647-97d9-c66ace06048c")').replace('Pg490PendingMigration.CUTOFF','java.time.Instant.parse("2026-10-09T05:42:22.532331Z")').replace('Pg490PendingMigration.ACTIVATION','UUID.fromString("021111b4-6de5-4733-917d-5ac176240ffc")')
    raw=raw.replace('static String SOURCE,DIGEST;','static String SOURCE,DIGEST;\n  static Pg797OwnedDatabase lease;\n  static boolean lossReported;\n  static long lastPulse,maxGap;\n  static void pulse()throws Exception{if(lease==null)return;long now=System.nanoTime();if(lastPulse!=0)maxGap=Math.max(maxGap,now-lastPulse);if(lastPulse!=0&&now-lastPulse>=TimeUnit.SECONDS.toNanos(30))throw new java.sql.SQLException("owned database observation interval exceeded");lease.verify();lastPulse=now;}')
    raw=raw.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}', 'for(;;){if(lease!=null&&!lossReported)try{pulse();}catch(Exception|Error lost){System.err.println("PG799_DB_NOT_CONFIRMED ownershipNotInferred=true");lossReported=true;}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}')
    raw=raw.replace('while(System.nanoTime()<deadline){','while(System.nanoTime()<deadline){pulse();')
    raw=raw.replace('void check(String name)throws Exception{','void check(String name)throws Exception{\n      pulse();')
    raw=raw.replace('phase="REFERENCE_SCOPE";var refs=new References(pid,database);','lease=new Pg797OwnedDatabase(database,new Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG799-fixed-pending","schubert_nk",true,true));pulse();phase="REFERENCE_SCOPE";var refs=new References(pid,database);')
    raw=raw.replace('phase="DATABASE_CLOSE";database.rollback();database.close();','pulse();phase="DATABASE_CLOSE";database.rollback();database.close();lease.confirmClosed();')
    # No heartbeat after an actual normal DB close, while waiting for the ten Ref releases.
    raw=raw.replace('while(System.nanoTime()<deadline){pulse();','while(System.nanoTime()<deadline){if(!phase.equals("REFERENCE_CLOSE"))pulse();')
    raw=raw.replace('require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));','require(arguments(args) && args[0].equals("'+SOURCE+'") && args[1].equals("'+DIGEST+'") && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));')
    raw=raw.replace('phase="COMPLETE_PUBLISH";privateWrite','phase="COMPLETE_PUBLISH";privateWrite(SAVE.resolve("observations.private"),("maxGapNanos="+maxGap+"\\n").getBytes(StandardCharsets.US_ASCII));privateWrite')
    return raw


def snapshot_library():
    raw=readonly_helper().replace('pg787-retired-post-v1/after.private.json','pg800-probe-post-v1/after.private.json')
    lines=raw.splitlines(keepends=True);tree=ast.parse(raw)
    for node in reversed(tree.body):
        if isinstance(node,ast.FunctionDef)and node.name=='main' or isinstance(node,ast.If)and "__name__"in ast.unparse(node.test):del lines[node.lineno-1:node.end_lineno]
    raw=''.join(lines)
    raw=raw.replace('def holder():','def holder(db_required=True):').replace("argv[-3]==b'Pg798DatabaseProbe' and argv[-2] in (b'verify',b'recover') and argv[-1]==b''","argv[-4:]==[b'Pg799PendingDeployment',b'"+SOURCE+"',b'"+DIGEST+"',b'']")
    raw=raw.replace('PG798-fixed-recovery','PG799-fixed-pending')
    raw=raw.replace("require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')","if db_required:require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')")
    return raw


def approval_oracle():
    tree=ast.parse((R/'pg498_pending_refs.py').read_text());nodes=[]
    for node in tree.body:
        if isinstance(node,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'APPROVAL','NEW_APPROVAL'}for t in node.targets)or isinstance(node,ast.FunctionDef)and node.name=='approval_only':nodes.append(node)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]));return raw.replace('PG495','PG796').replace('f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44',DIGEST)


REFS=r'''
import sys,os,pathlib,json,hashlib,stat,time
import pg799_snapshot as h
from pg777_reference_capability import CaptureReferences
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg799-pending-codeonly')
def save(name,value):
 with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def snapshot(db_required):
 owner=h.holder(db_required);h.parent();units={u:h.show(u)for u in h.ORDER+h.EXTRA}
 for u,v in units.items():
  h.require(v['MainPID']==v['ControlPID']=='0'and not v['Job']and v['ActiveState']in ('inactive','failed'));h.kernel_empty(u)
 value=h.snapshot();h.require(owner==h.holder(db_required));return {**value,'units':units,'current':str(pathlib.Path('/opt/schubert-nk/current').readlink())}
def main():
 os.umask(0o077);h.require(os.geteuid()==0 and len(sys.argv)==4 and sys.argv[1].isdigit()and sys.argv[2]==SOURCE and sys.argv[3]==DIGEST);h.load_definitions()
 h.require(not os.path.lexists(SAVE));SAVE.mkdir(mode=0o700)
 with CaptureReferences():
  before=snapshot(True);h.require(before==snapshot(True)and {k:before[k]for k in ('rows','trees','configuration')}==h.baseline()['capturedSnapshot']and before['current']=='/opt/schubert-nk/releases/0.1.0-PG750')
  save('refs-before.private.json',before);print('REF_READY',flush=True);changed=False
  for line in sys.stdin.buffer:
   phase=line.rstrip(b'\n');h.require(phase in (b'before',b'after',b'release'));actual=snapshot(phase!=b'release')
   if phase==b'before':h.require(not changed and actual==before)
   else:
    h.require(actual['rows']==before['rows']and actual['units']==before['units']and actual['configuration']==before['configuration']and approval_only(before['trees'],actual['trees'])and actual['current']=='/opt/schubert-nk/releases/0.1.0-PG796')
    h.require(pathlib.Path(APPROVAL).read_bytes()==NEW_APPROVAL);changed=True
   if phase==b'release':
    h.require(changed);save('refs-after.private.json',actual)
    q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
    h.require(h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']);break
   print('REF_CHECKED',flush=True)
  else:raise ValueError('owner channel ended early')
 print('REF_RELEASED',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as failure:
  print('REF_FAILED',flush=True);print('PG799_REFERENCE_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  while True:time.sleep(1)
'''


def refs():return 'SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\n'+approval_oracle()+'\n'+REFS


def before_freeze():
    return r'''import os,pathlib,sys
import pg799_snapshot as h
assert os.geteuid()==0
h.load_definitions();h.parent()
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG750')
assert not os.path.lexists('/var/lib/pgpt-s1-preservation/pg799-pending-codeonly')
for unused in range(2):
 h.parent()
 for u in h.ORDER+h.EXTRA:
  v=h.show(u);assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(u)
 assert h.snapshot()==h.baseline()['capturedSnapshot']
q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']
print('PG799_FREEZE_GUARD full24TreesOriginalSame=true all10Kernel0=true businessResource0=true')
'''
