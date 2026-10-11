"""Current-769 cold preservation/tenRef proof, not an admission or old close."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

R=Path(__file__).resolve().parent/'vm/050_s1'
sys.path.insert(0,str(R))
from pg1002_cold_readonly import payload as old_payload

OUT=Path('/home/mini/codex/project1/work/pgpt-vm/private/pg1437-cold-ro-v1')
KEYS=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload():
    wanted={'configuration_value','complete_configuration','require','command','metadata','tree','show','cold'}
    nodes=[n for n in ast.parse(old_payload()).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    assert len(nodes)==len(wanted)
    parser=next(n for n in ast.parse((R/'pg477_unit_references.py').read_text()).body
                if isinstance(n,ast.FunctionDef) and n.name=='exec_record')
    config=(R/'pg847_configuration.py').read_text()
    prefix='import os,pathlib,stat,subprocess,json,hashlib,re,datetime\n'
    prefix+='CONFIG_CONTRACT={};exec('+repr(config)+',CONFIG_CONTRACT)\nCONFIG_FIELDS=CONFIG_CONTRACT["FIELDS"]\n'
    prefix+=ast.unparse(ast.Module(body=nodes+[parser],type_ignores=[]))+'\n'
    body=r'''
os.umask(0o077)
BOOT='3d69f5af-6bac-46b1-a540-7591c4a79a0d'
SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
BOM='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'
BASELINE='d0dc7150002ad27fe7a7ef982e0eaa0233ba523d3e1b38ea14084666df37e839'
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation')
raw=(BASE/'pg1400-existing-admin-independent-post-v1/after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()==BASELINE)
old=json.loads(raw);require(old['source']==SOURCE and old['manifestSha256']==BOM)
UNITS=sorted(old['units']);require(len(UNITS)==10)
FIELDS=set('Id LoadState ActiveState SubState Job MainPID ControlPID InvocationID Type Restart RemainAfterExit Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL'.split())
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
require(pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
save=BASE/'pg1437-current-cold-readonly-v1';save.mkdir(mode=0o700)
def snapshot():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={};configuration={}
 for name in UNITS:
  state=show(name);require(cold(state))
  cg=pathlib.Path('/sys/fs/cgroup/system.slice')/name
  if cg.exists():
   for d in [cg,*[p for p in cg.rglob('*') if p.is_dir()]]:
    require(not(d/'cgroup.procs').read_text().strip() and 'populated 0\n' in (d/'cgroup.events').read_text())
  units[name]=state
  current=complete_configuration(command(['systemctl','show',name,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode(),name)
  require(CONFIG_CONTRACT['same'](old['configuration'][name],current,exec_record))
  require(show(name)==state);configuration[name]=current
 durable={}
 for key in ['backup','credentials','originals','oldProofs']:
  root=pathlib.Path(os.path.commonpath(list(old[key])))
  observed=tree(root);require(observed==old[key] and observed==tree(root));durable[key]=observed
 for path,expected in old['unitFilesActual'].items():
  require(hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==expected)
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in old['rows']:
  require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table) is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
 sql+='commit;';rows={}
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
  value=json.loads(line);require(value['table'] not in rows);rows[value['table']]=value['rows']
 require(rows==old['rows'] and len(rows)==24)
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==release)
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM)
 data=json.loads(manifest);require(data['source']['commit']==SOURCE and len(data['artifacts'])==187)
 command(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-rawin','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(BASE/'pg1292-manifest.sig')],4096)
 artifacts={}
 for record in data['artifacts']:
  name=record['path'];require(not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts)
  p=release/name;m=metadata(p);require(stat.S_ISREG(m[4]) and m[2]==0 and m[5]==1 and m[6]==record['size'])
  require(hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'] and metadata(p)==m);artifacts[name]=record['sha256']
 for p in ['/run/schubert-nk/startup','/run/schubert-nk/pt-coverage','/var/lib/schubert-nk/maintenance/active']:
  require(not os.path.lexists(p))
 peers=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"],4096)
 require(peers.splitlines()==[b'0',b'0'])
 return {'boot':BOOT,'source':SOURCE,'units':units,'configuration':configuration,'durable':durable,'rows':rows,'artifacts':artifacts}
import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for name in UNITS:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 first=snapshot();second=snapshot();require(first==second)
finally:
 failures=[]
 for name in reversed(refs):
  try:manager.UnrefUnit(name)
  except Exception as failure:failures.append(type(failure).__name__)
 try:bus.close()
 except Exception as failure:failures.append(type(failure).__name__)
 require(not failures)
encoded=json.dumps(first,sort_keys=True).encode()
with(save/'after.private.json').open('xb') as f:f.write(encoded);f.flush();os.fsync(f.fileno())
result={'run':'PG1437-current-cold-readonly-v1','actualExit':0,'boot':BOOT,'source':SOURCE,'tenColdFull18Full32Twice':True,'all24DbRowsUnchanged':True,'durableEntries':{k:len(v)for k,v in first['durable'].items()},'signedArtifacts':len(first['artifacts']),'signatureVerified':True,'allMetadataRefsClosed':True,'nativeStartupTmpfsAbsent':True,'oldTmpfsRestored':False,'oldNativeMustRemainInHostCapture':True,'oldNormalCloseInferred':False,'permissionIssued':False,'businessActions':0,'formalAccepted':False,'privateAfterSha256':hashlib.sha256(encoded).hexdigest()}
with(save/'result.safe.json').open('x') as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(result,sort_keys=True))
'''
    value=prefix+body
    ast.parse(value)
    return value


def main():
    os.umask(0o077);OUT.mkdir(mode=0o700)
    source=payload().encode()
    with (OUT/'payload.private.py').open('xb') as f:f.write(source)
    args=['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(KEYS/'known_hosts'),
          '-o','ConnectTimeout=10','-i',str(KEYS/'vm-access'),'-p','22222','ubuntu@127.0.0.1','sudo','-n','python3','-']
    with (OUT/'observer.private.log').open('xb') as log:
        result=subprocess.run(args,input=source,stdout=log,stderr=log);log.flush();os.fsync(log.fileno())
    record={'run':'PG1437-current-cold-readonly-v1','actualExit':result.returncode,'payloadSha256':hashlib.sha256(source).hexdigest(),'formalAccepted':False}
    if result.returncode==0:
        value=json.loads((OUT/'observer.private.log').read_bytes());record['safeGuestResult']=value
    with (OUT/'manifest.safe.json').open('x') as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(record));return result.returncode


if __name__=='__main__':raise SystemExit(main())
