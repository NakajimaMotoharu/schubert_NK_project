"""Current failed cohort independent read-only preservation, not recovery authority.

SS343/353/SSC254255; BUG1029/1030/YKT798799. Current Root timeout143,
API namespace226, only Artemis live. Never start/stop/change epoch/config/DB.
"""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg1041_cold_policy_diagnostic import W, P

R=Path(__file__).resolve().parent

PAYLOAD=r'''
import ast,datetime,dbus,hashlib,json,os,pathlib,re,shutil,stat,subprocess
os.umask(0o077)
def require(ok):
 if not ok:raise ValueError('current failed cohort preservation refused')
BOOT='cbca8738-3b24-4090-b77c-bf029677cdd6'
RUN='343a5a1b-d064-47d5-88c2-31c36d7ba7a4'
ACT='ada3f7ff-8287-48d7-9ba9-5cce71f61bd3'
CUTOFF='2026-10-10T12:40:27.396847Z'
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1')
SAVE=BASE/'proven-nested-once-v1/failed-capture-v1'
require(not os.path.lexists(SAVE)and os.geteuid()==0)
raw=(BASE/'after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='044dcfac0913fcdeabb0bc2706c526adeebfcf08140d284153a0c829c46aaafd')
before=json.loads(raw);baseline=before['snapshot'];units=tuple(sorted(baseline['units']))
require(len(units)==10)
helper=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
require(hashlib.sha256(helper).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
parsed=ast.parse(helper);names={'command','show','kernel','configuration_fields'}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names]
require(len(nodes)==len(names));exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pinned readonly primitives>','exec'),globals())
UNITS=set(units);FIELDS=set(baseline['units'][units[0]])
def md(p):
 s=p.lstat();return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def entry(p):
 a=md(p);attrs=sorted(os.listxattr(p,follow_symlinks=False))
 require(not attrs and(stat.S_ISREG(a[4])or stat.S_ISDIR(a[4])))
 value={'metadata':a,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()if stat.S_ISREG(a[4])else None}
 require(md(p)==a);return value
def tree(root):
 return{str(p):entry(p)for p in [root,*sorted(root.rglob('*'))]}
def rows():
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in sorted(baseline['rows']):
  require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',table)is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
 result={}
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;'],33554432).splitlines():
  value=json.loads(line);require(value['table']not in result);result[value['table']]=value['rows']
 require(set(result)==set(baseline['rows'])and len(result)==24);return result
def row_oracle(values):
 require(type(values)is dict and set(values)==set(baseline['rows'])and all(type(v)is list and all(type(r)is dict for r in v)for v in values.values()))
 table='schubert.batch_runs';old=baseline['rows'][table]
 require(all(r in values[table]for r in old))
 require(all(values[t]==baseline['rows'][t]for t in values if t!=table))
 delta=[r for r in values[table]if r not in old]
 steps={'BACKUP_DB','BACKUP_CONFIG','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER','CLEAN_BATCH_RUN','CLEAN_EXPIRY'}
 require(len(old)==594 and len(delta)==10 and{r['step']for r in delta}==steps)
 keys={'run_id','business_date','status','error_code','error_summary','target_count','success_count','failure_count','byte_count','started_at','ended_at','step'}
 require(all(keys<=set(r)for r in delta))
 require(all(r['run_id']==RUN and r['business_date']=='2026-10-10'and r['status']=='SKIPPED'and r['error_code']=='ALREADY_SUCCESSFUL'and r['error_summary']=='step already successful for business date'and all(r[k]==0 for k in ['target_count','success_count','failure_count','byte_count'])and r['started_at']is not None and r['ended_at']is not None and r['started_at']<=r['ended_at']for r in delta))
def original_oracle(current):
 old=baseline['durable']['originals'];root='/var/lib/schubert-nk/maintenance'
 added={root+'/active',root+'/runs/'+RUN+'.run',root+'/attempts/'+ACT+'.begin'}
 require(set(current)==set(old)|added)
 for name,value in old.items():
  now=current[name]
  if name in {root,root+'/runs',root+'/attempts'}:
   require(now['sha256']==value['sha256'])
   require(now['metadata'][:6]==value['metadata'][:6]and now['metadata'][6]>=value['metadata'][6]and now['metadata'][7]>=value['metadata'][7]and now['metadata'][8]>=value['metadata'][8])
  else:require(now==value)
 active=('NKACT1\n'+RUN+'\n'+CUTOFF+'\n'+ACT+'\n').encode('ascii')
 anchor=('NKRUN1\n'+RUN+'\n'+CUTOFF+'\n').encode('ascii')
 for name,wanted in [(root+'/active',active),(root+'/attempts/'+ACT+'.begin',active),(root+'/runs/'+RUN+'.run',anchor)]:
  m=current[name]['metadata'];require(m[2:6]==[0,0,stat.S_IFREG|0o600,1]and pathlib.Path(name).read_bytes()==wanted)
def resource_zero():
 sql="select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0'])
def capture():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 us={u:show(u,FIELDS)for u in units}
 parent=us['schubert-nk-morning-controller.service'];api=us['schubert-nk-api.service']
 require(parent['InvocationID']=='21f20c0cdbe34ce99431a55b10f92285'and parent['Result']=='timeout'and parent['ExecMainStatus']=='143'and parent['MainPID']==parent['ControlPID']=='0'and not parent['Job'])
 require(parent['ExecMainStartTimestampMonotonic']=='34658346852'and parent['ExecMainExitTimestampMonotonic']=='36458395316')
 require(api['InvocationID']=='7dab3e61504949608fabaaac52e024b0'and api['Result']=='exit-code'and api['ExecMainStatus']=='226'and api['MainPID']==api['ControlPID']=='0'and not api['Job'])
 require(not pathlib.Path('/proc/242818').exists())
 live={u:v for u,v in us.items()if v['MainPID']!='0'};require(set(live)=={'artemis.service'})
 broker=live['artemis.service'];require(broker['MainPID']=='253968'and broker['InvocationID']=='0f751fba26c94b22ac693a839fced07d'and broker['ActiveState']=='active'and broker['SubState']=='running')
 proc=pathlib.Path('/proc/253968');actor={'ticks':int((proc/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest(),'cgroup':(proc/'cgroup').read_text()}
 for u in units:
  require(us[u]['LoadState']=='loaded')
  if u!='artemis.service':kernel(u)
 rs=rows();row_oracle(rs)
 durable={}
 for kind,old in baseline['durable'].items():
  root=pathlib.Path(min(old,key=len));durable[kind]=tree(root)
  if kind=='originals':original_oracle(durable[kind])
  else:require(durable[kind]==old)
 release=pathlib.Path('/opt/schubert-nk/current')
 require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1068')
 require(hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d')
 for name,digest in baseline['artifacts'].items():require(hashlib.sha256((release/name).read_bytes()).hexdigest()==digest)
 startup=pathlib.Path('/run/schubert-nk/startup');epoch='ecf22224-112b-46b5-a103-bde3aab63229'
 require({p.name for p in startup.iterdir()}=={'epoch.current',epoch+'.owner',epoch+'.permit',epoch+'.API.start.intent'})
 privateBytes={str(p):p.read_bytes().hex()for p in startup.iterdir()}
 unitFiles={name:entry(pathlib.Path(name))for name in before['unitFiles']}
 require(unitFiles==before['unitFiles'])
 journals={u:command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'-u',u,'--since','2026-10-10 12:40:16 UTC','-o','json','--no-pager']).hex()for u in units}
 native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 resource_zero()
 return{'units':us,'actor':actor,'rows':rs,'durable':durable,'unitFiles':unitFiles,'configuration':{u:show(u,configuration_fields())for u in units},'startup':tree(startup),'privateBytes':privateBytes,'journals':journals,'native':native,'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed'}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 value=capture();require(value==capture())
 SAVE.mkdir(mode=0o700)
 with(SAVE/'observed.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 shutil.copytree('/run/schubert-nk/pt-coverage',SAVE/'native-after',symlinks=False)
 for p in [SAVE/'native-after',*(SAVE/'native-after').rglob('*')]:
  require(not p.is_symlink());os.chmod(p,0o700 if p.is_dir()else 0o600)
  if p.is_file():
   with p.open('rb')as f:os.fsync(f.fileno())
 require(value==capture())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateSnapshotSha256':hashlib.sha256((SAVE/'observed.private.json').read_bytes()).hexdigest(),'batchRows':604,'before594Preserved':True,'new10ExactSkip':True,'other23TablesUnchanged':True,'oldOriginalsBackupCredentialsProofsPreserved':True,'currentSource':value['source'],'parentTimeout143':True,'apiNamespace226':True,'onlyArtemisLive':True,'nativeCount':sum(1 for x in value['native'].values()if x['sha256']is not None),'metadataReferencesReturned':True,'operationAuthority':False,'formalAccepted':False,'startsStopsConfigDbWrites0':True}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):
        raise ValueError('fixed clean source required')
    ast.parse(PAYLOAD)
    base=W/'pg1120-current-failed-capture-v1'
    if Path(str(base)+'.safe.json').exists()or Path(str(base)+'.private.log').exists():
        raise ValueError('existing failed capture preserved')
    os.umask(0o077);start=datetime.datetime.now(datetime.timezone.utc)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes',
         '-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),
         '-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    result=subprocess.run(ssh,input=PAYLOAD.encode(),capture_output=True,timeout=90)
    with Path(str(base)+'.private.log').open('xb')as f:
        f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe=dict(run='PG1120-current-failed-capture-v1',actualExit=result.returncode,
              startedUTC=start.isoformat(),completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              scriptSha256=hashlib.sha256(PAYLOAD.encode()).hexdigest(),
              logSha256=hashlib.sha256(result.stderr).hexdigest(),formalAccepted=False,
              operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    if result.returncode==0:safe.update(json.loads(result.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:
        json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode


if __name__=='__main__':raise SystemExit(main())
