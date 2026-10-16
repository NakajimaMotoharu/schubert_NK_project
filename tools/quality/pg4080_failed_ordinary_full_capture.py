"""SSC287 read-only profile input: current all-unit configuration, ordinary identities and FD sets."""
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg4052_failed_current_capture as base
from pg4058_original_read_profile import contracts
import pg4078_ordinary_actor_policy as policy

SLOT = 'pg4080-failed-ordinary-full-capture-v1'


def payload():
    raw = base.payload(); raw = raw[:raw.index('import dbus\nbus=')]
    raw = raw.replace('pg4052-failed-current-capture-v1', SLOT)
    return raw + '\n' + contracts() + '\nACTOR_POLICY=' + repr(inspect.getsource(policy)) + '\n' + BODY


BODY = r'''
actor_policy={};exec(ACTOR_POLICY,actor_policy)
fields+=',Type,Restart,RemainAfterExit,KillMode,SendSIGKILL,TimeoutStopUSec'
accounts={'schubert-nk-api.service':('schubert-api',['schubert-api','schubert','schubert-read','schubert-web']),
 'schubert-nk-web.service':('schubert-web',['schubert-web','schubert','schubert-read']),
 'caddy.service':('caddy',['caddy']),'artemis.service':('schubert-artemis',['schubert-artemis'])}
def nss(unit):
 account,names=accounts[unit]
 raw=command(['/usr/bin/getent','passwd',account],1024);require(raw.endswith(b'\n')and raw.count(b'\n')==1)
 p=raw[:-1].decode('ascii').split(':');require(len(p)==7 and p[0]==account and p[1]=='x')
 uid=int(p[2]);gid=int(p[3]);groups=[]
 for name in names:
  raw=command(['/usr/bin/getent','group',name],1024);require(raw.endswith(b'\n')and raw.count(b'\n')==1)
  g=raw[:-1].decode('ascii').split(':');require(len(g)==4 and g[0]==name and g[1]=='x')
  value=int(g[2]);require(value not in groups)
  if name==account:require(value==gid)
  groups.append(value)
 return {'uid':uid,'gid':gid,'groups':sorted(groups)}
def detailed(unit,expected):
 pid=expected['pid'];p=Path('/proc')/str(pid);status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 required={k:status[k]for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']}
 fixed=nss(unit);require(actor_policy['identity'](required,fixed['uid'],fixed['gid'],fixed['groups']))
 require(str((p/'exe').readlink())==('/usr/bin/caddy'if unit=='caddy.service'else'/opt/jdk-25.0.4/bin/java'))
 require((p/'cgroup').read_text()=='0::/system.slice/'+unit+'\n')
 children=sorted({int(c)for task in(p/'task').iterdir()for c in(task/'children').read_text().split()});require(not children)
 fds={}
 for fd in sorted((p/'fd').iterdir(),key=lambda x:int(x.name)):
  target=str(fd.readlink());s=fd.stat();info=dict(line.split(':',1)for line in(p/'fdinfo'/fd.name).read_text().splitlines()if ':'in line)
  fds[fd.name]={'target':target,'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],
                 'flags':info['flags'].strip(),'mountId':info['mnt_id'].strip()}
 require(int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==expected['ticks']and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==expected['argvSha256'])
 return {'identity':expected,'authority':required,'nss':fixed,'children':children,'fds':fds}
def full():
 value=snapshot();cfg={}
 for unit in old['units']:
  text=command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],1048576).decode();actual=complete_configuration(text,unit)
  require(CONFIG_CONTRACT['same'](old['configuration'][unit],actual,exec_record));cfg[unit]=actual
 for filename,expected in old['unitFilesActual'].items():
  p=Path(filename);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==expected)
 value['configuration']=cfg;value['unitFilesActual']=old['unitFilesActual'];value['detailedActors']={unit:detailed(unit,a)for unit,a in value['actors'].items()}
 return value
import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 first=full();second=full();require(first['units']==second['units']and first['actors']==second['actors']and first['configuration']==second['configuration'])
 require(first['database']['rows']==second['database']['rows']and first['durable']==second['durable']and first['native']==second['native']and first['startup']==second['startup']and first['runtime']==second['runtime'])
 require(not second['flocks']and not second['database']['locks'])
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
require(current.resolve(strict=True)==root and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
encoded=json.dumps({'first':first,'second':second,'source':data['source']['commit'],'BOM':sha,'boot':boot},sort_keys=True).encode()
with(save/'observed.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
names=[Path(p).name for p in second['startup']if p!='/run/schubert-nk/startup']
profile={'entryCount':len(names),'permitStartIntent':'permit-start.intent'in names,'serviceStartIntents':sum(n.endswith('.start.intent')for n in names),
 'launchRecords':sum(n.endswith('.launch')for n in names),'ownerRecords':sum(n.endswith('.owner')for n in names),'permitRecords':sum(n.endswith('.permit')for n in names),'epochCurrent':'epoch.current'in names}
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateSha256':hashlib.sha256(encoded).hexdigest(),
 'allTenFullConfigurationAndUnitFilesVerified':True,'all24OriginalBackupNativeStable':True,'ordinaryIdentityAllFourVerified':True,
 'detailedActorsStableTwice':first['detailedActors']==second['detailedActors'],'actorFdCounts':{k:len(v['fds'])for k,v in second['detailedActors'].items()},
 'nativeExecCount':sum(Path(p).suffix=='.exec'for p in second['native']),'dbPeerCount':len(second['database']['peers']),'managementAdvisoryAndFlock0':True,
 'startupProfile':profile,'metadataRefsClosed':len(refs)==10,'stateChangingActions':0,'recoveryAuthorityIssued':False,'formalAccepted':False}
(save/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result))
'''


def main():
    os.umask(0o077); out = W / SLOT; out.mkdir()
    raw = payload(); compile(raw, '<current ordinary full actor capture>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=180)
    (out / 'stdout.safe.json').write_bytes(r.stdout); (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'source': base.SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if not r.returncode: value['result'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
