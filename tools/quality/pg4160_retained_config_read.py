"""SSC276/287 bounded read under original retained exclusion; no second gate, signal or ACK."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
import pg4112_canonical_epoch_owned_stage as previous
from pg4060_original_profile_dual_stack import once

SLOT='pg4160-retained-config-read-v1'


def payload():
    raw=previous.payload('inspect');raw=raw[:raw.index('import dbus\nbus=')]
    raw=raw.replace(previous.INSPECT,SLOT)
    raw=once(raw,"  if name in expected_inv:require(v['InvocationID']==expected_inv[name] and v['ActiveState']=='active' and v['SubState']=='running')",
             "  if name in expected_inv:require(v['InvocationID']==expected_inv[name])")
    raw=once(raw,'import base64,selectors','import base64')
    return raw+'\n'+BODY


BODY=r'''
import sys
require(not Path('/proc/761848').exists())
def proc(pid):
 p=Path('/proc')/str(pid);rawcmd=(p/'cmdline').read_bytes();status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 fields={k:status[k].strip()for k in ['PPid','Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']}
 fds={}
 for f in(p/'fd').iterdir():
  s=f.stat();fds[f.name]={'target':str(f.readlink()),'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'fdinfo':(p/'fdinfo'/f.name).read_text()}
 children=sorted({int(c)for task in(p/'task').iterdir()for c in(task/'children').read_text().split()})
 return {'pid':pid,'ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256(rawcmd).hexdigest(),'authority':fields,'cgroup':(p/'cgroup').read_text(),'children':children,'fds':fds}
java=proc(790010);parent=proc(789928)
require(java['ticks']==14181503 and java['argvSha256']=='ed8889ef439ebe28100f5a4d4cee289004c55e9bfb108a7a314c37d25aaf7af2'and java['authority']['PPid']=='789928')
require(java['authority']['Uid'].split()==['0']*4 and parent['authority']['Uid'].split()==['0']*4 and not java['children']and parent['children']==[790010])
reference=Path('/var/lib/pgpt-s1-preservation/pg4080-failed-ordinary-full-capture-v1/observed.private.json').read_bytes();require(hashlib.sha256(reference).hexdigest()=='fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8');reference=json.loads(reference)['second']
runtime=Path('/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover')
baseline=json.loads((runtime/'before.private.json').read_bytes());captures=json.loads((runtime/'terminal-before.private.json').read_bytes())
sys.path.insert(0,str(frozen));import recovery_terminal as terminal_contract
from pg526_term_witness import FIELDS as TERMINAL_FIELDS
def show(unit):
 result=dict(line.split('=',1)for line in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(TERMINAL_FIELDS))],1048576).decode().splitlines());require(set(result)==TERMINAL_FIELDS);return result
now=show('caddy.service');normal=terminal_contract.normal_terminal(captures['caddy.service'],now);terminal_contract.kernel_empty('caddy.service')
configs=config();differences={};declarations={}
for unit,value in configs.items():
 before=reference['configuration'][unit];differences[unit]=[k for k in sorted(value)if value[k]!=before[k]]
 declarations[unit]=CONFIG_CONTRACT['same'](before,value,exec_record)
current_state=snapshot()
same={k:baseline[k]==current_state[k]for k in ['durable','native','startup','runtime']}
same['all24']=baseline['database']['rows']==current_state['database']['rows']
same['remainingActors']=current_state['actors']=={u:a for u,a in baseline['actors'].items()if u!='caddy.service'}
private={'current':current_state,'configuration':configs,'configurationReference':reference['configuration'],
 'caddyBefore':captures['caddy.service'],'caddyAfter':now,'java':java,'python':parent,'javaSecond':proc(790010),'pythonSecond':proc(789928)}
encoded=json.dumps(private,sort_keys=True).encode();(save/'observed.private.json').write_bytes(encoded)
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateSha256':hashlib.sha256(encoded).hexdigest(),
 'caddyNormalTerminalData':normal,'caddyOldPidAndKernelEmpty':True,'same':same,'configurationChangedFields':{u:v for u,v in differences.items()if v},
 'allDeclarativeConfigurationStillSame':all(declarations.values()),'javaPid':java['pid'],'javaTicks':java['ticks'],'javaFdCount':len(java['fds']),
 'pythonPid':parent['pid'],'pythonTicks':parent['ticks'],'pythonArgvSha256':parent['argvSha256'],'pythonFdCount':len(parent['fds']),
 'recordedBackendCurrentlyPresent':any(p['pid']==790031 for p in current_state['database']['peers']),
 'managementFlockCount':len(current_state['flocks']),'managementAdvisoryCount':len(current_state['database']['locks']),
 'dbPeerRoleCounts':{role:sum(row['user']==role for row in current_state['database']['peers'])for role in {row['user']for row in current_state['database']['peers']}},
 'originalUnknownNotNormalized':True,'signalStopStartRevokeAck':0,'formalAccepted':False}
(save/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result))
'''


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir()
    raw=payload();compile(raw,'<retained-owner read only>','exec');(out/'payload.private.py').write_text(raw)
    # Original observer owns the host gate and guest M/A. Acquiring it again would deadlock.
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','payloadSha256':hashlib.sha256(raw.encode()).hexdigest()}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
