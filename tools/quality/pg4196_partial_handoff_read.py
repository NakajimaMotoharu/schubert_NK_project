"""Read only after original host exit255. No lock acquisition, signals, ACK or business action."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
import pg4168_retained_pair_keeper as previous
from pg4188_exact_partial_recover import bootstrap
from pg4176_partial_coordinator import files

SLOT='pg4196-partial-handoff-read-v1'


def payload():
    raw=previous.payload();raw=raw[:raw.index('import time,signal,select,ctypes,dbus,traceback')]
    raw=raw.replace("save=base/('pg4180-retained-pair-keeper-v1-'+MODE)","save=base/'"+SLOT+"'")
    # Prefix includes proc from the fixed read source; no old PID access until called.
    assert any(isinstance(n,ast.FunctionDef)and n.name=='proc'for n in ast.parse(raw).body)
    hashes={n:hashlib.sha256(t.encode()).hexdigest()for n,t in files().items()}
    raw+='\nKEEPER_PROGRAM='+repr(bootstrap('keeper.py',hashes))+'\n'+BODY
    compile(raw,'<partial handoff readonly>','exec');return raw


BODY=r'''
require(not Path('/proc/790010').exists()and not Path('/proc/789928').exists())
matches=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')[:-1]
 except(ProcessLookupError,FileNotFoundError,PermissionError):continue
 if len(args)==5 and args[0]==b'python3'and args[1:3]==[b'-B',b'-c']and args[3]==KEEPER_PROGRAM.encode()and args[4]==b'recover':matches.append(int(p.name))
require(len(matches)==1);keeper=proc(matches[0]);second=proc(matches[0]);require(keeper==second)
state=snapshot();require(not state['flocks']and not state['database']['locks'])
folder=base/'pg4180-retained-pair-keeper-v1-recover'
names=sorted(p.name for p in folder.iterdir());documents={}
for name in ['790010.term-reserved.private.json','789928.term-reserved.private.json','java-terminal.private.json','old-pair-gone.private.json','failure.private.json']:
 p=folder/name
 if p.exists():documents[name]=json.loads(p.read_bytes())
before=Path('/var/lib/pgpt-s1-preservation/pg4160-retained-config-read-v1/observed.private.json').read_bytes();require(hashlib.sha256(before).hexdigest()=='e5fff095e3d770b128150029cefa2b3c501462d1e4f5b41279b5d80500be0d0b');before=json.loads(before)['current']
same={k:state[k]==before[k]for k in ['units','actors','durable','native','startup','runtime']};same['all24']=state['database']['rows']==before['database']['rows'];require(all(same.values()))
private={'keeper':keeper,'keeperSecond':second,'current':state,'documents':documents,'names':names,'configuration':config()}
encoded=json.dumps(private,sort_keys=True).encode()
with(save/'observed.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
result={'actualExit':0,'source':data['source']['commit'],'boot':boot,'BOM':sha,'privateSha256':hashlib.sha256(encoded).hexdigest(),
 'keeperPid':keeper['pid'],'keeperTicks':keeper['ticks'],'keeperArgvSha256':keeper['argvSha256'],'keeperFdCount':len(keeper['fds']),
 'oldPairGone':True,'oldManagementLocksAdvisory0':True,'same':same,'privateDocumentNames':names,
 'old4152Normal':False,'businessActions':0,'signalsIssued':0,'formalAccepted':False}
(save/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result))
'''


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=payload();(out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-','recover'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stdout.safe.json').write_bytes(result.stdout);(out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','payloadSha256':hashlib.sha256(raw.encode()).hexdigest()}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
