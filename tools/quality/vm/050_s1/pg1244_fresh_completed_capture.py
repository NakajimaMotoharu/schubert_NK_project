"""Read-only fresh Root full current seal; independent session oracle, no stop."""
import inspect
import pg1120_current_failed_capture as library
import pg1222_completed_retirement_preflight as transport
import pg1243_fresh_day_rows_oracle as row_oracle
import pg847_configuration as configuration
from pg1242_fresh_ordinary_done_receipt import payload as receipt
from pg1195_completed_resume_a01 import qualify_actor

def payload():
    prefix=library.PAYLOAD[:library.PAYLOAD.index('def row_oracle(')]
    prefix=prefix.replace('failed-capture-v1','fresh-completed-capture-v1')
    prefix=prefix.replace(',33554432).splitlines()',',67108864).splitlines()')
    guard=receipt();guard=guard[:guard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1242-fresh-ordinary-done-receipt-v1')")]
    identities={'schubert-nk-api.service':('999','981',('980','981','982','986'),'/opt/jdk-25.0.4/bin/java','dev.codex.schubert.nk.api.bootstrap.ApiProcessMain'),'schubert-nk-web.service':('997','980',('980','982','986'),'/opt/jdk-25.0.4/bin/java','dev.codex.schubert.nk.web.bootstrap.WebProcessMain'),'caddy.service':('993','978',('978',),'/usr/bin/caddy',None)}
    code=prefix+'\nGUARD='+repr(guard)+'\nROW_ORACLE='+repr(inspect.getsource(row_oracle))+'\nCONFIG_ORACLE='+repr(inspect.getsource(configuration))+'\nIDENTITIES='+repr(identities)+'\n'+inspect.getsource(qualify_actor)+'\n'+BODY
    compile(code,'<fresh same-source full capture>','exec');return code

BODY=r'''
import types
fresh=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1238-fresh-day-ordinary-before-v1/before.private.json').read_bytes()
require(hashlib.sha256(fresh).hexdigest()=='57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e');sealed=json.loads(fresh)['current']
data=types.ModuleType('independent_fresh_rows');exec(ROW_ORACLE,data.__dict__)
cfg=types.ModuleType('independent_configuration');exec(CONFIG_ORACLE,cfg.__dict__)
parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
n=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');ns={'re':re};exec(compile(ast.Module(body=[n],type_ignores=[]),'<strict actual declaration parser>','exec'),ns)
OWNED={'schubert-nk-api.service':('669495','e5406d7517cc40958fdcf68008d23f23',6220542),'schubert-nk-web.service':('670731','4236e5a9bfd94fe09ca34323687bc5c3',6221973),'caddy.service':('672790','ea56ffeed963402d8ff67a43b33ea123',6224235),'artemis.service':('606091','a1f58ea9067d4ebb815d73a783f109e2',6146861)}
def capture():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 proof=types.ModuleType('actual_fresh_done');exec(GUARD,proof.__dict__)
 require(proof.result['endMonotonicUs']==62400649336)
 us={u:show(u,FIELDS)for u in units};actors={}
 require({u for u,v in us.items()if v['MainPID']!='0'}==set(OWNED))
 for u,(pid,inv,ticks)in OWNED.items():
  v=us[u];require(v['MainPID']==pid and v['InvocationID']==inv and not v['Job']and v['ControlPID']=='0'and v['ActiveState']=='active'and v['SubState']=='running'and v['Result']=='success')
  p=pathlib.Path('/proc')/pid;require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks and(p/'cgroup').read_text()=='0::/system.slice/'+u+'\n')
  status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x);process={k:status[k].strip()for k in {'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}}
  if u in IDENTITIES:qualify_actor(u,process,str((p/'exe').readlink()),(p/'cmdline').read_bytes())
  actors[u]={'ticks':ticks,'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'cgroup':(p/'cgroup').read_text(),'process':process}
 for u in set(units)-set(OWNED):kernel(u)
 configuration={u:show(u,cfg.FIELDS)for u in units}
 require(all(cfg.same(sealed['configuration'][u],configuration[u],ns['exec_record'])for u in units))
 rs=rows();summary=data.session_post(sealed['rows'],rs,data.instant('2026-10-10T20:03:22.718197Z'))
 unitFiles={p:entry(pathlib.Path(p))for p in before['unitFiles']};require(unitFiles==before['unitFiles'])
 durable={k:tree(pathlib.Path(min(v,key=len)))for k,v in sealed['extraDurable'].items()}
 durable['originals']=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));durable['backup']=tree(pathlib.Path('/srv/schubert-nk/backup'))
 for k in sealed['extraDurable']:require(durable[k]==sealed['extraDurable'][k])
 runtime=tree(pathlib.Path('/run/systemd/system'));require(runtime==sealed['runtime'])
 release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1068')
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d')
 artifacts=json.loads(manifest)['artifacts'];require(len(artifacts)==187)
 for a in artifacts:
  path=pathlib.PurePosixPath(a['path']);require(not path.is_absolute()and'..'not in path.parts)
  value=(release/a['path']).read_bytes();require(len(value)==a['size']and hashlib.sha256(value).hexdigest()==a['sha256'])
 startup=tree(pathlib.Path('/run/schubert-nk/startup'));native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 return{'units':us,'actors':actors,'configuration':configuration,'rows':rs,'unitFiles':unitFiles,'durable':durable,'runtime':runtime,'startup':startup,'native':native,'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','manifestSha256':hashlib.sha256(manifest).hexdigest(),'genuineCompletion':proof.result,'pid1':proof.rows,'run':'9f651096-aef9-4fba-90b0-a653e99f035a','cutoff':'2026-10-10T20:03:22.718197Z','activation':'27accac0-c118-4c98-9244-02625a2d88a7','dataSummary':summary,'authority':False}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 current=capture();require(current==capture());SAVE.mkdir(mode=0o700)
 with(SAVE/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(current,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 require(current==capture())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateBeforeSha256':hashlib.sha256((SAVE/'before.private.json').read_bytes()).hexdigest(),'actualExit':0,'tables':24,'configurationFields':32,'signedPayloadArtifacts':187,'currentFourOwnedLive':True,'genuineCompletion':current['genuineCompletion'],'sessionSummary':current['dataSummary'],'businessFullOraclePending':True,'normalMetadataReferences':True,'configurationWritesStartsStops0':True,'formalAccepted':False,'rawExported':False}))
'''

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1244-fresh-completed-capture-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<fresh actual full read-only capture transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
