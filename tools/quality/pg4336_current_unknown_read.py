"""BUG1349 bounded read under the retained original owner; no ACK, gate or action."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, SSH
from pg4152_exact_failed_done_recover import process, durable
from pg4060_original_profile_dual_stack import once
import pg4160_retained_config_read as old_read

SLOT = 'pg4336-current-unknown-read-v1'
ORIGINAL = W / 'pg4316-current-failed-dispatch-v1-recover'
PIN = '87ef52f80156a0c83ae1451a08f1b20508797c6072c9b86263af90b163569182'


def payload():
    raw = (W / 'pg4316-current-failed-dispatch-v1-artifact/dispatch.private.py').read_text()
    if hashlib.sha256(raw.encode()).hexdigest() != PIN:
        raise ValueError('unchanged original driver required')
    raw = raw[:raw.index('import time,sys,traceback')]
    raw = once(raw, "save=base/('pg4316-current-failed-dispatch-v1-'+MODE)",
               "save=base/'" + SLOT + "'")
    # No recovery reservation in a diagnostic. Keep every source/profile check.
    raw = once(raw, "require(not os.path.lexists(save/'run-reserved.private'));(save/'run-reserved.private').write_bytes(b'one failed-DONE recovery; no replay\\n')", '')
    proc = next(n for n in ast.parse(old_read.BODY).body
                if isinstance(n, ast.FunctionDef) and n.name == 'proc')
    return raw + '\n' + ast.get_source_segment(old_read.BODY, proc) + '\n' + BODY


BODY = r'''
import time
folder=base/'pg4316-current-failed-dispatch-v1-recover'
before=json.loads((folder/'before.private.json').read_bytes())
captures=json.loads((folder/'terminal-before.private.json').read_bytes())
owned=json.loads((folder/'owned.private.json').read_bytes())
require(owned=={'pid':815726,'ticks':15409721,'backend':815747,'argvSha256':'5312514ace02eda3eb8f4f4941095f5e334dc00859d52aa2a5a811a626c7b698'})
sys.path.insert(0,str(frozen))
import recovery_terminal as terminal_contract
from pg526_term_witness import FIELDS as TERMINAL_FIELDS
def show(unit):
 value=dict(line.split('=',1)for line in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(TERMINAL_FIELDS))],1048576).decode().splitlines())
 require(set(value)==TERMINAL_FIELDS);return value
def differences(a,b,path=''):
 if type(a)is dict and type(b)is dict:
  result=[]
  for key in sorted(set(a)|set(b)):
   p=path+'/'+str(key)
   result.extend([p]if key not in a or key not in b else differences(a[key],b[key],p))
  return result
 return []if a==b else[path]
java=proc(owned['pid']);require(java['ticks']==owned['ticks']and java['argvSha256']==owned['argvSha256'])
parentpid=int(java['authority']['PPid']);parent=proc(parentpid)
require(java['authority']['Uid']=='0\t0\t0\t0'and java['authority']['Gid']=='0\t0\t0\t0')
require(parent['authority']['Uid']=='0\t0\t0\t0'and parent['authority']['Gid']=='0\t0\t0\t0')
caddy=show('caddy.service');require(terminal_contract.normal_terminal(captures['caddy.service'],caddy))
terminal_contract.kernel_empty('caddy.service');require(not Path('/proc/'+captures['caddy.service']['MainPID']).exists())
samples=[]
for unused in range(4):
 samples.append(snapshot())
 time.sleep(.05)
fixedkeys=['units','actors','detailedActors','durable','native','startup','runtime']
pairs=[{key:differences(a[key],b[key])for key in fixedkeys if a[key]!=b[key]}for a,b in zip(samples,samples[1:])]
same={key:all(s[key]==before[key]for s in samples)for key in ['durable','native','startup','runtime']}
same['all24']=all(s['database']['rows']==before['database']['rows']for s in samples)
same['remainingActors']=all(s['actors']=={u:a for u,a in before['actors'].items()if u!='caddy.service'}for s in samples)
require(all(same.values()))
configurations=config();require(declaration_contract['same_configurations'](configurations,config(),CONFIG_CONTRACT['same'],exec_record))
private={'java':java,'python':parent,'javaSecond':proc(owned['pid']),'pythonSecond':proc(parentpid),
 'samples':samples,'pairDifferences':pairs,'configuration':configurations,'caddyBefore':captures['caddy.service'],'caddyAfter':caddy,
 'documents':{p.name:json.loads(p.read_bytes())for p in folder.iterdir()if p.name in ['failure.private.json','owned.private.json']},
 'names':sorted(p.name for p in folder.iterdir())}
sha_private=save_private('observed.private.json',private)
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,
 'privateSha256':sha_private,'javaPid':java['pid'],'javaTicks':java['ticks'],'javaArgvSha256':java['argvSha256'],'javaFdCount':len(java['fds']),
 'pythonPid':parent['pid'],'pythonTicks':parent['ticks'],'pythonArgvSha256':parent['argvSha256'],'pythonFdCount':len(parent['fds']),
 'caddyNormalTerminalData':True,'same':same,'changedTopLevelKeysPerPair':[sorted(p)for p in pairs],
 'changedPathCountsPerPair':[{k:len(v)for k,v in p.items()}for p in pairs],
 'managementFlockCounts':[len(s['flocks'])for s in samples],'managementAdvisoryCounts':[len(s['database']['locks'])for s in samples],
 'recordedBackendPresent':[any(p['pid']==owned['backend']for p in s['database']['peers'])for s in samples],
 'originalFailedPairAvailable':False,'signalStopStartRevokeAck':0,'originalUnknownNotNormalized':True,'formalAccepted':False}
save_private('manifest.safe.json',result);print(json.dumps(result))
'''


def main():
    start = json.loads((ORIGINAL / 'start.safe.json').read_bytes())
    ssh = json.loads((ORIGINAL / 'ssh.private.json').read_bytes())
    if process(start['owner']['pid']) != start['owner'] or process(ssh['pid']) != ssh:
        raise ValueError('original host owner/SSH must remain identical')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload()
    compile(raw, '<current retained-owner readonly diagnostic>', 'exec')
    with (out / 'payload.private.py').open('x') as f:
        f.write(raw)
    # Deliberately no management_gate: original58917 retains that gate.
    result = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-', 'inspect'],
                            input=raw.encode(), capture_output=True, timeout=180)
    with (out / 'stdout.private.log').open('xb') as f:
        f.write(result.stdout)
    with (out / 'stderr.private.log').open('xb') as f:
        f.write(result.stderr)
    value = {'actualExit': result.returncode, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
             'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'operationsIssued': 0}
    if result.returncode == 0:
        value['result'] = json.loads(result.stdout)
    durable(out / 'manifest.safe.json', value)
    print(json.dumps(value))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
