"""Read-only full current seal for actual four-owned stop. Business oracle separate."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1559_pending_runtime_sources import refs,TOOLS
from pg1577_current_root_done_receipt import payload as receipt

OWNED={'artemis.service':('118964','6e745372ba4e4c7683cda767c607b93c',3222133,'2a7089f6e2bbbbe31a74253fab119bd63b0055019e386c3a6f372a19d6e004b6'),'schubert-nk-api.service':('158794','2111873a431743359c0627a8f5e394c8',3310542,'28ede1b8e4b75a93d305d37ae4cde215d56ac6cbea33ead731c09c8ca56df86a'),'schubert-nk-web.service':('159826','fb683eeb6d3b4e90b66c1576f9108a0c',3311883,'886dc4d85c506bb05a3b22e2f4260067a062170e8e78cb326a32fe7d29a857ac'),'caddy.service':('161708','b62723b53ece4420b783a627e3548012',3314902,'8ffd9e85b36aeea3c9aee774d9953a1c3ec022b925b0d413ad644e9d53ce9c0a')}

BODY=r'''
SAVE=BASE/'pg1578-current-completed-seal-v1';require(not os.path.lexists(SAVE))
before_raw=(BASE/'pg1573-current-resume-once-v1/before.private.json').read_bytes();require(hashlib.sha256(before_raw).hexdigest()=='cc8ec852ca75bb2cf980ec97176ec771dab17bc0ffa4b3c2936f1c76db93345d');before=json.loads(before_raw)
def capture():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 proof=types.ModuleType('actual_current_done');exec(GUARD,proof.__dict__);require(proof.result['endMonotonicUs']==33583425972 and proof.result['elapsedSeconds']==1539.994702)
 us={u:show(u)for u in UNITS};actors={}
 require({u for u,v in us.items()if v['MainPID']!='0'}==set(OWNED))
 for unit,(pid,inv,ticks,argv_sha)in OWNED.items():
  v=us[unit];require(v['MainPID']==pid and v['InvocationID']==inv and v['ControlPID']=='0'and not v['Job']and v['ActiveState']=='active'and v['SubState']=='running'and v['Result']=='success')
  p=pathlib.Path('/proc')/pid;require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==argv_sha and(p/'cgroup').read_text()=='0::/system.slice/'+unit+'\n')
  status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x);process={k:status[k].strip()for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']}
  if unit in IDENTITIES:qualify_actor(unit,process,str((p/'exe').readlink()),(p/'cmdline').read_bytes())
  actors[unit]={'ticks':ticks,'argvSha256':argv_sha,'cgroup':(p/'cgroup').read_text(),'process':process}
 for unit in set(UNITS)-set(OWNED):kernel_empty(unit)
 configuration={u:complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode(),u)for u in UNITS}
 for u,v in configuration.items():require(CONFIG_CONTRACT['same'](before['configuration'][u],v,exec_record))
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in before['rows']:
  require(re.fullmatch('[a-z_]+\\.[a-z_]+',table)is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
 sql+='commit;';rs={}
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],67108864).splitlines():
  row=json.loads(line);require(row['table']not in rs);rs[row['table']]=row['rows']
 require(set(rs)==set(before['rows'])and len(rs)==24)
 unit_files={}
 for path,expected in old['unitFilesActual'].items():
  p=pathlib.Path(path);m=metadata(p);sha=hashlib.sha256(p.read_bytes()).hexdigest();require(UNIT_VECTOR['matches'](expected,m,sha)and metadata(p)==m);unit_files[path]={'metadata':m,'sha256':sha}
 durable={k:tree(pathlib.Path(os.path.commonpath(list(before['durable'][k]))))for k in before['durable']}
 for k in ['credentials','oldProofs']:require(durable[k]==before['durable'][k])
 require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
 current=pathlib.Path('/opt/schubert-nk/current');release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544');require(current.readlink()==release)
 raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==BOM);data=json.loads(raw);require(data['source']['commit']==SOURCE and len(data['artifacts'])==187)
 command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(BASE/'pg1544-manifest.sig')],4096)
 for record in data['artifacts']:
  p=release/record['path'];m=metadata(p);require(stat.S_ISREG(m[4])and m[2]==0 and m[5]==1 and m[6]==record['size']and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']and metadata(p)==m)
 runtime=tree(pathlib.Path('/run/systemd/system'));expected_runtime=before['oneTimeRuntime'];require(set(runtime)==set(expected_runtime))
 for path,v in runtime.items():require(v=={'metadata':expected_runtime[path]['metadata'],'sha256':expected_runtime[path]['sha256']})
 startup=tree(pathlib.Path('/run/schubert-nk/startup'));native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 return{'units':us,'actors':actors,'configuration':configuration,'rows':rs,'unitFiles':unit_files,'durable':durable,'runtime':runtime,'startup':startup,'native':native,'source':SOURCE,'manifestSha256':BOM,'genuineCompletion':proof.result,'pid1':proof.rows,'run':'15700a87-9117-4f63-a0ff-768dd604d0f1','cutoff':'2026-10-11T21:18:59.040097Z','activation':'9e706936-a3c9-4a09-bb66-e2b1e8bbef66','authority':False,'businessFullOraclePending':True}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 current=capture();require(current==capture());SAVE.mkdir(mode=0o700)
 with(SAVE/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(current,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 require(current==capture())
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'privateBeforeSha256':hashlib.sha256((SAVE/'before.private.json').read_bytes()).hexdigest(),'currentFourOwnedLive':True,'genuineCompletion':current['genuineCompletion'],'tables':24,'configurationFields':32,'signedArtifacts':187,'normalMetadataReferences':True,'startsStopsReloadWrites0':True,'businessFullOraclePending':True,'formalAccepted':False}))
'''

def payload():
    nodes=[]
    for n in ast.parse(refs()).body:
        if isinstance(n,ast.Try):break
        nodes.append(n)
    from pg1195_completed_resume_a01 import qualify_actor
    import inspect
    guard=receipt();guard=guard[:guard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1577-current-root-done-receipt-v1')")]
    identities={'schubert-nk-api.service':('999','981',('980','981','982','986'),'/opt/jdk-25.0.4/bin/java','dev.codex.schubert.nk.api.bootstrap.ApiProcessMain'),'schubert-nk-web.service':('997','980',('980','982','986'),'/opt/jdk-25.0.4/bin/java','dev.codex.schubert.nk.web.bootstrap.WebProcessMain'),'caddy.service':('993','978',('978',),'/usr/bin/caddy',None)}
    s="import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/"+TOOLS+"')\nsys.argv=['readonly-current-completed','verify','2']\n"+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\nGUARD='+repr(guard)+'\nOWNED='+repr(OWNED)+'\nIDENTITIES='+repr(identities)+'\n'+inspect.getsource(qualify_actor)+'\n'+BODY
    compile(s,'<actual current fullseal before ownstop>','exec');return s

def main():
    os.umask(0o077);out=W/'pg1578-current-completed-seal-v1';out.mkdir(mode=0o700)
    genuine=json.loads((W/'pg1577-current-root-done-receipt-v1.safe.json').read_bytes())
    if genuine['actualExit']!=0 or genuine['source']!='4d6bcbddb417b76d27e52d5d9640752c300edccf':raise ValueError('actual current source genuine receipt required')
    raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120);(out/'stderr.private.log').write_bytes(result.stderr)
    safe={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'authority':False,'formalAccepted':False}
    if result.returncode==0:safe.update(json.loads(result.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode

if __name__=='__main__':raise SystemExit(main())
