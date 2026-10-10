"""Fixed old-holder exclusion, readonly directory SPI/writer/UUID refusal, graph only."""
import base64
import datetime
import hashlib
import json
import os
import subprocess
from pg1041_cold_policy_diagnostic import GUEST as previous,W,P


def main():
    os.umask(0o077);out=W/'pg1043-cold-graph-diagnostic-v1';out.mkdir(mode=0o700)
    compiled_root=W/'pg1042-cold-graph-probe-v1';compiled=json.loads((compiled_root/'compile.safe.json').read_bytes())
    if compiled['actualExit']!=0:raise ValueError('compiled readonly graph required')
    payloads={}
    for name,digest in compiled['classHashes'].items():
        data=(compiled_root/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('probe class changed')
        payloads[name.rpartition('/')[2]]={'base64':base64.b64encode(data).decode(),'sha256':digest}
    raw=previous.replace("root=parent/'diagnostic-v1'","root=parent/'graph-diagnostic-v1'")
    begin="target=classdir/'Pg1040ColdRunPolicyProbe.class'";end="cp=str(root)"
    if raw.count(begin)!=1 or raw.count(end)!=1:raise ValueError('fixed class transfer refused')
    replacement="""for name,entry in CLASS_PAYLOADS.items():
 assert name in ('Pg1042ColdReadonlyGraphProbe.class','Pg1042ColdReadonlyGraphProbe$TraceIo.class')
 target=classdir/name;data=base64.b64decode(entry['base64'],validate=True);assert hashlib.sha256(data).hexdigest()==entry['sha256']
 with target.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(data);f.flush();os.fsync(f.fileno())
"""
    raw=raw[:raw.index(begin)]+replacement+raw[raw.index(end):]
    raw=raw.replace('dev.codex.schubert.nk.batch.file.Pg1040ColdRunPolicyProbe','dev.codex.schubert.nk.batch.file.Pg1042ColdReadonlyGraphProbe')
    raw='CLASS_PAYLOADS='+repr(payloads)+'\n'+raw
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=raw.encode(),capture_output=True,timeout=90)
    with(out/'diagnostic.private.log').open('xb')as f:f.write(result.stdout);f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'run':'PG1043-cold-graph-diagnostic-v1','actualExit':result.returncode,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classHashes':compiled['classHashes'],'scriptSha256':hashlib.sha256(raw.encode()).hexdigest(),'logSha256':hashlib.sha256(result.stdout+result.stderr).hexdigest(),'dataOnly':True,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    for line in(result.stdout+result.stderr).decode('ascii').splitlines():
        if line.startswith('PG1042_'):print(line)
    print(json.dumps(safe));raise SystemExit(result.returncode)


if __name__=='__main__':main()
