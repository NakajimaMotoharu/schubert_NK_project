"""New-only corrected preflight, streaming retained-scope logs and start-source receipt."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1050_cold_tree_preflight import payload as previous
from pg1041_cold_policy_diagnostic import P, W


def payload():
    raw = previous()
    old = 'PG1050-cold-tree-preflight-v1'
    if raw.count(old) != 2 or raw.count('tree-preflight-v1') != 3:
        raise ValueError('fixed corrected preflight labels refused')
    return raw.replace(old, 'PG1051-cold-tree-preflight-v2').replace("/tree-preflight-v1'", "/tree-preflight-v2'")


def dispatch(run, name, script):
    if (run, name) not in {
        ('PG1051-cold-tree-preflight-v2', 'pg1051-cold-tree-preflight-v2'),
        ('PG1055-cold-tree-preflight-v3', 'pg1055-cold-tree-preflight-v3'),
        ('PG1056-cold-metadata-handoff-v1', 'pg1056-cold-metadata-handoff-v1'),
    }:
        raise ValueError('fixed preflight dispatch identity refused')
    os.umask(0o077)
    out = W / name
    out.mkdir(mode=0o700)
    raw = script.encode()
    source = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    begin = {'run':run,'operatorSource':source,
             'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'scriptSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    with (out/'guest-script.private.py').open('xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    with (out/'begin.safe.json').open('x') as f:
        json.dump(begin,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
    ssh = ['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),
           '-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with (out/'result.private.log').open('xb') as log:
        proc = subprocess.Popen(ssh,stdin=subprocess.PIPE,stdout=log,stderr=log)
        proc.stdin.write(raw); proc.stdin.close()
        actual = proc.wait()
        log.flush(); os.fsync(log.fileno())
    result=dict(begin,actualExit=actual,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                logSha256=hashlib.sha256((out/'result.private.log').read_bytes()).hexdigest())
    if actual==0:
        observed=json.loads((out/'result.private.log').read_bytes())
        if observed['run']!=begin['run'] or observed['actualExit']!=0:
            raise ValueError('actual result label refused')
        result['observed']=observed
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(result,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(result)); raise SystemExit(actual)


def main():
    dispatch('PG1051-cold-tree-preflight-v2','pg1051-cold-tree-preflight-v2',payload())


if __name__=='__main__':
    main()
