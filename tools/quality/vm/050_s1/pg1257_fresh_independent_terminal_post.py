"""Independent actual fresh stop seals/full24-full32-187/native/resources, no stop."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg1220_current_full32_terminal_post as previous
from pg1247_fresh_owned_stop_sources import CHANGES,SOURCE,W

P=previous.P
SSH=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']

def payload(seals):
    if type(seals)is not dict or set(seals)!=set(previous.SEALS)or any(type(v)is not str or len(v)!=64 or any(c not in '0123456789abcdef'for c in v)for v in seals.values()):raise ValueError('complete actual fresh stop seals required')
    s=previous.payload()
    for name,digest in previous.SEALS.items():s=s.replace(digest,seals[name])
    for old,new in CHANGES:s=s.replace(old,new)
    s=s.replace('Pg1247','Pg1253').replace('pg1247','pg1253').replace('PG1247','PG1253')
    s=s.replace('pg1220-terminal-final-v1','pg1257-fresh-terminal-post-v1').replace('PG1220-terminal-final-v1','PG1257-fresh-terminal-post-v1')
    compile(s,'<actual new-only independent fresh terminal post>','exec');return s

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current source required')
    if(W/'pg1256-stop-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual fresh normal reverse-stop required')
    build=json.loads((W/'pg1254-frozen-v1.safe.json').read_bytes())
    if build['actualExit']!=0 or build['productionSource']!=SOURCE:raise ValueError('qualified current immutable ABI required')
    names=[n.replace('1216','1253')for n in ['Pg1216NativeStop.class','Pg1216NativeStop$References.class','pg1216_native_refs.py','pg1216_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1216_parent_receipt.py','pg1216_durable.py','pg1216_configuration.py','pg1216_configuration_capture.py','pg1216_row_bound.py','pg1216_stable_journal.py']]
    hashes={n:build['fileHashes'][n]for n in names}
    receipt=(W/'pg1253-native-tools-v1/pg1253_parent_receipt.py').read_text()
    seals=json.loads(subprocess.check_output(SSH,input=previous.SEAL.replace('pg642-native-stop-v1','pg1253-native-stop-v1').encode(),timeout=20))
    code='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload(seals)
    base=W/'pg1257-fresh-terminal-post-v1'
    if any(Path(str(base)+suffix).exists()for suffix in ['.safe.json','.private.log','.exit']):raise ValueError('new-only independent post slot required')
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(SSH,input=code.encode(),capture_output=True,timeout=90)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({k:v for k,v in value.items()if k not in {'proofHashes','toolHashes'}}));return r.returncode

if __name__=='__main__':raise SystemExit(main())
