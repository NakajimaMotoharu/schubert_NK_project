"""PG553 independent SS331/341 cleanup oracle. Root private evidence only; no starts/deletes.
No production maintenance function is called to construct expected values.
"""
import hashlib,json,os,pathlib,stat,subprocess,sys
os.umask(0o077)
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-newrun-preflight-v1')
SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
DIGEST='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'
TABLES=['schubert.'+x for x in ['answers','app_logs','app_users','async_jobs','audio_files','auth_sessions','batch_runs','entry_audio_links','games','inbox_inspection_progress','log_cleanup_progress','login_ip_attempts','media_assets','mq_outbox','notifications','questions','request_inbox','script_entries','script_files','speakers']]+['schubert_web_session.'+x for x in ['pending_context_revocations','web_http_sessions','web_log_outbox','web_receipt_references']]
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
def require(value):
 if not value:raise ValueError('fixed new-run preflight refused')
def accepted(code,length):return type(code)is int and type(length)is int and code==0 and 0<=length<=33554432
def command(args):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 require(accepted(p.returncode,len(p.stdout)));return p.stdout
def stopped():
 values={}
 for u in UNITS:
  raw=command(['/usr/bin/systemctl','show',u,'--property=Id,LoadState,MainPID,ControlPID,Job,InvocationID,ActiveState,SubState'])
  rows=raw.decode().splitlines();v=dict(x.split('=',1) for x in rows)
  require(len(rows)==len(v)==8 and v['Id']==u and v['LoadState']=='loaded' and v['MainPID']==v['ControlPID']=='0' and not v['Job'])
  for p in pathlib.Path('/sys/fs/cgroup/system.slice',u).glob('**/cgroup.procs'):require(not p.read_text().strip())
  values[u]=v
 return values
def metadata(p):
 s=p.lstat();require(not p.is_symlink() and (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)))
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def tree(root):
 value={}
 for p in [root,*sorted(root.rglob('*'))]:
  before=metadata(p);h=None
  if p.is_file():
   digest=hashlib.sha256()
   with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1048576),b''):digest.update(chunk)
   h=digest.hexdigest()
  require(before==metadata(p));value[str(p)]={'metadata':before,'sha256':h}
 return value
def snapshot():
 # One repeatable-read/READ ONLY transaction. All original columns remain private.
 sql="begin isolation level repeatable read read only; set local timezone='UTC';"
 sql+="select json_build_object('lower',now(),'upper',now()+interval '30 minutes','day',(now() at time zone 'Asia/Tokyo')::date);"
 for t in TABLES:sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
 sql+="select json_build_object('historyToday',(select count(*) from schubert.batch_runs where business_date=(now() at time zone 'Asia/Tokyo')::date),'liveSessions',(select count(*) from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid<>pg_backend_pid()));commit;"
 raw=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]);lines=raw.splitlines();require(len(lines)==26)
 header=json.loads(lines[0]);data={}
 for line in lines[1:-1]:
  v=json.loads(line);require(v['table'] not in data);data[v['table']]=v['rows']
 require(set(data)==set(TABLES) and json.loads(lines[-1])=={'historyToday':0,'liveSessions':0});return header,data
def main():
 require(sys.argv[1:]==['prepare'] and os.geteuid()==0 and not ROOT.exists())
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
 release=pathlib.Path('/opt/schubert-nk/current');require(release.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG548'))
 raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==DIGEST and json.loads(raw)['source']['commit']==SOURCE)
 require(pathlib.Path('/var/lib/pgpt-s1-preservation/pg549-completed-activate-v5/complete.private').read_bytes()==b'completedCurrentVerified=true\nmode=activate\nallNewScopesReturnedNormally=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n')
 units=stopped();bounds,rows=snapshot();bounds2,rows2=snapshot();require(rows==rows2 and len(rows['schubert.batch_runs'])==462)
 backup=tree(pathlib.Path('/srv/schubert-nk/backup'));original=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));transfer=tree(pathlib.Path('/srv/schubert-nk/data/transfer'));startup=tree(pathlib.Path('/run/schubert-nk/startup'))
 names=sorted(p.name for p in pathlib.Path('/srv/schubert-nk/backup').iterdir());require(len(names)<=6 and len(names)>0)
 # Even if all six old names qualified, NEW_SUCCESS adds at most one: <=7, no retention deletion.
 require(all(v['sha256'] is None for v in transfer.values()))
 require(not any('intent' in n for n in startup) and units==stopped())
 require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists() and not pathlib.Path('/var/lib/schubert-nk/maintenance/pending').exists())
 require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists())
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
 ROOT.mkdir(mode=0o700)
 evidence={'bounds':bounds,'secondBounds':bounds2,'rows':rows,'units':units,'backup':backup,'original':original,'transfer':transfer,'startup':startup,'backupOldNames':names,'maximumRetainedAfterNew':len(names)+1,'expectedTransferRemoved':sorted(n for n in transfer if n!='/srv/schubert-nk/data/transfer')}
 with (ROOT/'before.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(evidence,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 for p in [ROOT,ROOT.parent]:
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print(json.dumps({'run':'PG553-newrun-preflight-v1','snapshot24':True,'original462':True,'backupOldCount':len(names),'newBackupNoRetentionDelete':True,'transferCandidates':len(transfer)-1,'starts0':True,'beforeSha256':hashlib.sha256((ROOT/'before.private.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()
