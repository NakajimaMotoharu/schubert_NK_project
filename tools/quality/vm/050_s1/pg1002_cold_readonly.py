"""Fresh readonly cold observer; old tmpfs is absence, not successful retirement.
Raw database/filesystem values remain solely inside the guest private0700 snapshot.
"""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
GUEST=r'''
import datetime,hashlib,json,os,pathlib,re,stat,subprocess
os.umask(0o077)
def require(v):
 if not v:raise ValueError('cold readonly invariant refused')
def command(a,limit=33554432):
 r=subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 require(r.returncode==0 and len(r.stdout)<=limit);return r.stdout
def metadata(p):
 s=p.lstat();require(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode))
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def tree(p):
 result={}
 for x in [p,*sorted(p.rglob('*'))]:
  m=metadata(x);sha=hashlib.sha256(x.read_bytes()).hexdigest()if x.is_file()else None
  require(m==metadata(x));result[str(x)]={'metadata':m,'sha256':sha}
 return result
def show(name):
 pairs=[v.split('=',1)for v in command(['systemctl','show',name,'--property='+','.join(sorted(FIELDS))],1048576).decode().splitlines()]
 v=dict(pairs);require(len(v)==len(pairs)and set(v)==FIELDS);return v
def cold(v):
 return (v['LoadState']=='loaded'and v['ActiveState']=='inactive'and v['SubState']=='dead'
  and v['MainPID']==v['ControlPID']=='0'and v['Job']==v['InvocationID']==''and v['Result']=='success'
  and v['KillMode']=='control-group'and v['SendSIGKILL']=='no'
  and all(v[k]=='0'for k in ['ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic']))
def snapshot():
 units={}
 for name in old['units']:
  a=show(name);require(cold(a))
  group=pathlib.Path('/sys/fs/cgroup/system.slice')/name
  if group.exists():
   for p in [group,*[p for p in group.rglob('*')if p.is_dir()]]:
    require(not(p/'cgroup.procs').read_text().strip()and'populated 0\n'in(p/'cgroup.events').read_text())
  require(a==show(name));units[name]=a
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in old['rows']:
  require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
 sql+='commit;';rows={}
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
  v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
 require(rows==old['rows']and len(rows)==24 and len(rows['schubert.batch_runs'])==594)
 durable={}
 for key in ['backup','credentials','originals','oldProofs']:
  root=pathlib.Path(os.path.commonpath(list(old[key])))
  value=tree(root);require(value==old[key]and value==tree(root));durable[key]=value
 config={};config_differences=[]
 for name in units:
  fields=sorted(old['configuration'][name])
  raw=command(['systemctl','show',name,'--property='+','.join(fields)],1048576).decode()
  v=complete_configuration(raw,name);require(set(v)==set(fields));config[name]=v
  for key in fields:
   if key not in ['ExecStart','ExecStop']and v[key]!=old['configuration'][name][key]:
    config_differences.append({'unit':name,'field':key})
 require(str(pathlib.Path('/opt/schubert-nk/current').readlink())==str(RELEASE))
 original=(RELEASE/'RELEASE-MANIFEST.json').read_bytes()
 require(hashlib.sha256(original).hexdigest()==BOM)
 manifest=json.loads(original);require(manifest['source']['commit']==SOURCE)
 require(len(manifest['artifacts'])==187 and len(manifest['migrations'])==29)
 pin=pathlib.Path('/etc/schubert-nk/deployment-key/pin.der');sig=pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig')
 require(hashlib.sha256(pin.read_bytes()).hexdigest()==PIN_HASH and hashlib.sha256(sig.read_bytes()).hexdigest()==SIG_HASH)
 command(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey',str(pin),'-rawin','-in',str(RELEASE/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],4096)
 artifacts={}
 for record in manifest['artifacts']:
  path=record['path'];require(path not in artifacts and not pathlib.PurePosixPath(path).is_absolute()and'..'not in pathlib.PurePosixPath(path).parts)
  p=RELEASE/path;m=metadata(p)
  require(stat.S_ISREG(m[4])and m[2]==0 and m[5]==1 and m[6]==record['size']and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']and m==metadata(p));artifacts[path]=record['sha256']
 approval=pathlib.Path('/etc/schubert-nk/release-approval/current')
 require(approval.read_bytes()==('NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256='+BOM+'\n').encode())
 peers=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"],4096)
 require(peers.splitlines()==[b'0',b'0'])
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=metadata(p)
  require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0])
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    x=f[5].split(':');require((int(x[0],16),int(x[1],16),int(x[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
 require(not pathlib.Path('/run/schubert-nk/startup').exists()and not pathlib.Path('/run/schubert-nk/pt-coverage').exists())
 require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
 return {'boot':BOOT,'units':units,'rows':rows,'durable':durable,'configuration':config,
  'configurationDifferencesExceptExecutionHistory':config_differences,'artifacts':artifacts}
require(os.geteuid()==0 and pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and BOOT!='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json');raw=base.read_bytes()
require(hashlib.sha256(raw).hexdigest()==BASELINE_HASH);old=json.loads(raw)
FIELDS=set('Id LoadState ActiveState SubState Job MainPID ControlPID InvocationID Type Restart RemainAfterExit Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL'.split())
first=snapshot();second=snapshot();require(first==second)
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1002-cold-readonly-v1');save.mkdir(mode=0o700)
snapshot_raw=json.dumps(first,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:f.write(snapshot_raw);f.flush();os.fsync(f.fileno())
result={'run':'PG1002-cold-readonly-v1','boot':BOOT,'actualExit':0,'source':SOURCE,'all24RowsUnchangedTwice':True,'batchRows':594,
 'allTenColdKernelEmptyTwice':True,'durableTreesUnchanged':{k:len(v)for k,v in first['durable'].items()},
 'signedArtifacts':187,'signatureVerifiedWithPinnedKey':True,'configDifferenceFields':first['configurationDifferencesExceptExecutionHistory'],
 'full32ColdConfigurationAccepted':False,'currentStartupAbsent':True,'currentNativeAbsent':True,
 'oldTmpfsSuccessfullyRetired':False,'oldNativeRestored':False,'oldCompletionMadeSuccessfulByColdBoot':False,
 'clientAdvisoryFlock0':True,'businessStartStopReloadMigrationWrites':0,'afterPrivateSha256':hashlib.sha256(snapshot_raw).hexdigest(),
 'formalAccepted':False,'fullColdPreparationAccepted':False}
with(save/'result.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(result,sort_keys=True))
'''

def payload():
    root=W/'pg932-release-v1'
    manifest=json.loads((root/'RELEASE-MANIFEST.json').read_bytes())
    # Manifest source key is validated against the actual immutable host candidate,
    # not a guessed schema key inserted into a guest verifier.
    assert manifest['source']['commit']=='40ef6e894573d2ffab1d1732124960f9c98d5f97'
    prefix='\n'.join(f'{k}={v!r}'for k,v in {
      'BOOT':'cbca8738-3b24-4090-b77c-bf029677cdd6','SOURCE':manifest['source']['commit'],
      'BASELINE_HASH':'c76227aee0b0c82877c750db53115c004aeef8e99f0c8f3682b94fbd1a56ff32',
      'BOM':hashlib.sha256((root/'RELEASE-MANIFEST.json').read_bytes()).hexdigest(),
      'PIN_HASH':hashlib.sha256((P/'pg381-release-pin.der').read_bytes()).hexdigest(),
      'SIG_HASH':hashlib.sha256((P/'pg932-manifest-v1.sig').read_bytes()).hexdigest()}.items())
    helper=W/'pg963-native-tools-v1/pg963_configuration_capture.py'
    frozen=json.loads((W/'pg963-frozen-v1.safe.json').read_bytes())
    assert hashlib.sha256(helper.read_bytes()).hexdigest()==frozen['fileHashes'][helper.name]
    code=helper.read_text().replace('FIELDS','CONFIG_FIELDS')
    source=prefix+'\n'+code+'\nRELEASE=__import__("pathlib").Path("/opt/schubert-nk/releases/0.1.0-PG932")\n'+GUEST
    ast.parse(source);return source

def capture(name,script):
    os.umask(0o077);out=W/name;assert not out.exists();out.mkdir(mode=0o700)
    with(out/'guest-script.private.py').open('x')as f:f.write(script)
    started=datetime.datetime.now(datetime.timezone.utc)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes',
      '-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    r=subprocess.run(ssh,input=script.encode(),capture_output=True,timeout=120)
    with(out/'stderr.private.log').open('xb')as f:f.write(r.stderr)
    safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),
      'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),
      'scriptSha256':hashlib.sha256(script.encode()).hexdigest(),'stderrSha256':hashlib.sha256(r.stderr).hexdigest(),
      'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe,sort_keys=True));raise SystemExit(r.returncode)

if __name__=='__main__':capture('pg1002-cold-readonly-v1',payload())
