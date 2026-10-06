"""PG478 independent SS331/341 cleanup oracle. Root private evidence only; no starts/deletes.
No production maintenance function is called to construct expected values.
"""
import datetime,hashlib,json,os,pathlib,stat,subprocess,sys
os.umask(0o077)
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2')
SOURCE='cce61f63900b1479f9f8dbdc338e222b1c8c38a3'
DIGEST='613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667'
TABLES=['schubert.'+x for x in ['answers','app_logs','app_users','async_jobs','audio_files','auth_sessions','batch_runs','entry_audio_links','games','inbox_inspection_progress','log_cleanup_progress','login_ip_attempts','media_assets','mq_outbox','notifications','questions','request_inbox','script_entries','script_files','speakers']]+['schubert_web_session.'+x for x in ['pending_context_revocations','web_http_sessions','web_log_outbox','web_receipt_references']]
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
def require(value):
 if not value:raise ValueError('fixed new-run preflight refused')
def accepted(code,length):return code==0 and 0<=length<=33554432
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
 sql+="select json_build_object('historyToday',(select count(*) from schubert.batch_runs where business_date=(now() at time zone 'Asia/Tokyo')::date),'liveSessions',(select count(*) from pg_stat_activity where usename in ('schubert_batch','schubert_migration','schubert_api','schubert_web')));commit;"
 raw=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]);lines=raw.splitlines();require(len(lines)==26)
 header=json.loads(lines[0]);data={}
 for line in lines[1:-1]:
  v=json.loads(line);require(v['table'] not in data);data[v['table']]=v['rows']
 require(set(data)==set(TABLES) and json.loads(lines[-1])=={'historyToday':0,'liveSessions':0});return header,data
def main():
 require(sys.argv[1:]==['prepare'] and os.geteuid()==0 and not ROOT.exists())
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54')
 release=pathlib.Path('/opt/schubert-nk/current');require(release.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG477'))
 raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==DIGEST and json.loads(raw)['source']['commit']==SOURCE)
 require(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-acceptance/complete.private').read_text()=='allNewScopesReturnedNormally=true\npartialDeploymentAcceptedSeparately=true\noldCloseUnknown=true\nstarts0=true\ndeployReplay0=true\npermits0=true\nddl0=true\n')
 units=stopped();bounds,rows=snapshot();bounds2,rows2=snapshot();require(rows==rows2 and len(rows['schubert.batch_runs'])==411)
 backup=tree(pathlib.Path('/srv/schubert-nk/backup'));original=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));transfer=tree(pathlib.Path('/srv/schubert-nk/data/transfer'));startup=tree(pathlib.Path('/run/schubert-nk/startup'))
 names=sorted(p.name for p in pathlib.Path('/srv/schubert-nk/backup').iterdir());require(len(names)==6 and len(backup)==20)
 # Even if all six old names qualified, NEW_SUCCESS adds at most one: <=7, no retention deletion.
 require(len(transfer)==6 and all(v['sha256'] is None for v in transfer.values()))
 require(len(startup)==66 and not any('intent' in n for n in startup) and units==stopped())
 ROOT.mkdir(mode=0o700)
 evidence={'bounds':bounds,'secondBounds':bounds2,'rows':rows,'units':units,'backup':backup,'original':original,'transfer':transfer,'startup':startup,'backupOldNames':names,'maximumRetainedAfterNew':7,'expectedTransferRemoved':sorted(n for n in transfer if n!='/srv/schubert-nk/data/transfer')}
 with (ROOT/'before.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(evidence,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 for p in [ROOT,ROOT.parent]:
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print('PG478_PREFLIGHT snapshot24=true original411=true oldBackup6Preserved=true newBackupNoRetentionDelete=true transferFiveEmptyExpected=true starts0=true')
if __name__=='__main__':main()
