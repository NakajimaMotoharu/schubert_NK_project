"""BUG771 read-only admission/whole original preservation; all raw DB stays Root private.
No service start/stop, request/intent retirement, chmod config, repair or credential read.
"""
import datetime,hashlib,json,os,pathlib,stat,subprocess,sys
os.umask(0o077)
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2')
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg479-archive-diagnosis')
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
RUN='49437eda-1681-43a9-883a-424eb55a6166'
INV='795eec6b633244148b40b26d0251a8ed'
FIELDS='Id,LoadState,ActiveState,SubState,MainPID,ControlPID,Job,InvocationID,ExecMainCode,ExecMainStatus,Result,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL,Restart,Type,RemainAfterExit'
UNITS=['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-api.service','schubert-nk-web.service','artemis.service','caddy.service','schubert-nk-bootstrap-admin.service']
def cmd(args,limit=33554432):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 if p.returncode or len(p.stdout)>limit:raise ValueError('bounded readonly capture refused')
 return p.stdout
def metadata(p):
 s=p.lstat()
 if not (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)):raise ValueError('nonregular capture refused')
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def tree(root):
 out={}
 for p in [root,*sorted(root.rglob('*'))]:
  a=metadata(p);h=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
  if a!=metadata(p):raise ValueError('unstable capture refused')
  out[str(p)]={'metadata':a,'sha256':h}
 return out
def preserved(before,after):
 for name,old in before.items():
  if name not in after:return False
  new=after[name]
  if old['sha256'] is not None:
   if old!=new:return False
  elif old['metadata'][:5]!=new['metadata'][:5]:return False
 return True
def main():
 assert sys.argv[1:] in [['before-terminal'],['after-terminal']]
 assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
 phase=sys.argv[1];target=ROOT/(phase+'.private.json');assert not target.exists()
 before=json.loads((BASE/'before.private.json').read_text())
 units={u:dict(x.split('=',1) for x in cmd(['/usr/bin/systemctl','show',u,'--property='+FIELDS],65536).decode().splitlines()) for u in UNITS}
 assert all(set(v)==set(FIELDS.split(',')) for v in units.values())
 assert units[UNITS[0]]['InvocationID']==INV
 sql="begin isolation level repeatable read read only; set local timezone='UTC';"
 for t in before['rows']:sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
 sql+='commit;'
 raw=cmd(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]);rows={}
 for line in raw.splitlines():v=json.loads(line);assert v['table'] not in rows;rows[v['table']]=v['rows']
 assert set(rows)==set(before['rows'])
 new=[v for v in rows['schubert.batch_runs'] if v['run_id']==RUN]
 old=[v for v in rows['schubert.batch_runs'] if v['run_id']!=RUN]
 dbsame=old==before['rows']['schubert.batch_runs'] and all(rows[t]==before['rows'][t] for t in rows if t!='schubert.batch_runs')
 backup=tree(pathlib.Path('/srv/schubert-nk/backup'));original=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));transfer=tree(pathlib.Path('/srv/schubert-nk/data/transfer'))
 keep=preserved(before['backup'],backup) and preserved(before['original'],original) and before['transfer']==transfer
 modes={}
 for name,expected in [('common.yml',0o100640),('api.yml',0o100640),('web.yml',0o100640),('batch.yml',0o100640),('backup-profile.json',0o100640),('inbox-inspector.env',0o100640),('api.env',0o100600),('web.env',0o100600)]:
  p=pathlib.Path('/proc/1/root/etc/schubert-nk')/name;s=p.stat()
  modes[name]={'actualMode':s.st_mode,'expectedMode':expected,'oldSuffixMode':0o100600 if name.endswith('.env') else 0o100640,'uid':s.st_uid,'gid':s.st_gid,'links':s.st_nlink,'aclAbsent':'system.posix_acl_access' not in os.listxattr(p)}
 assert all(v['actualMode']==v['expectedMode'] and v['uid']==0 and v['links']==1 and v['aclAbsent'] for v in modes.values())
 mismatch=[k for k,v in modes.items() if v['actualMode']!=v['oldSuffixMode']];assert mismatch==['inbox-inspector.env']
 kernel={u:[p.read_text().strip() for p in pathlib.Path('/sys/fs/cgroup/system.slice',u).glob('**/cgroup.procs')] for u in UNITS}
 evidence={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'boot':BOOT,'units':units,'kernel':kernel,'rows':rows,'backup':backup,'original':original,'transfer':transfer,'modes':modes,'newRunRows':new,'allOldDbSame':dbsame,'oldPhysicalPreserved':keep}
 ROOT.mkdir(mode=0o700,exist_ok=True)
 with target.open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(evidence,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print(json.dumps({'phase':phase,'oldDatabaseAllSame':dbsame,'oldPhysicalPreserved':keep,'newRows':len(new),'newStatuses':sorted(v['status'] for v in new),'wrongOldSuffix':mismatch,'parent':{k:units[UNITS[0]][k] for k in ['MainPID','InvocationID','ActiveState','SubState','ExecMainStatus','Result']},'privateSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'normalCloseInferred':False}))
 assert dbsame and keep and len(new)==2 and all(v['status']=='RUNNING' for v in new)
if __name__=='__main__':main()
