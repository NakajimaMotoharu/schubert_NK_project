"""Independent actual finite current retirement, all originals/resources retained."""
import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import pg1220_current_full32_terminal_post as previous
import pg1223_completed_runtime_contract as contract
from pg847_configuration import FIELDS

W=previous.W;P=previous.P
SEALS={'before.private.json':'26f40ec04730d8f50c68da873f8781888e7e2b5cd75c8eb476289cc95858835d',
       'after.private.json':'26f6480d7b7cefcf92f792ec7adf77234306418ae41928f875496af21f5dcd18',
       'parent.private.jsonl':'0081125ef04ea7476dc599b9afa3538c2d4252a255a6c252e01b9178065ab600',
       'complete.private':'4fe191fb3223c85ef1ba8dcccc050417c785693a75a2355a2a2127fdcc6d523c'}

def payload():
    s=previous.payload()
    for name,old in previous.SEALS.items():s=s.replace(old,SEALS[name])
    s=s.replace('pg1216-native-stop-v1','pg1232-native-stop-v1').replace('pg1216-native-tools-v1','pg1232-native-tools-v1')
    s=s.replace('allEightOwnedTerminal=true\\n','allTenAlreadyTerminal=true\\n').replace('starts0=true\\noldUnknownNormalized=false','starts0=true\\nruntimeRetiredOnly=true\\noldUnknownNormalized=false')
    marker="require(all(after[k]==before[k]for k in before if k not in ('units','configuration')))"
    c=inspect.getsource(contract).replace('from pg847_configuration import FIELDS','FIELDS='+repr(FIELDS))
    check='import types\nretirement=types.ModuleType("independent_actual_runtime");exec('+repr(c)+',retirement.__dict__)\n'+ORIGINAL
    if s.count(marker)!=1:raise ValueError('exact independent finite delta insertion rejected')
    s=s.replace(marker,check)
    s=s.replace("'run':'PG1220-terminal-final-v1'","'run':'PG1236-completed-runtime-retired-post-v1'").replace("base/'pg1220-terminal-final-v1'","base/'pg1236-completed-runtime-retired-post-v1'")
    s=s.replace("'normalPG877NewScopesSealed':True","'normalCurrentRetirementScopesSealed':True,'runtimeExactEntryRetired':True,'oldFailedScopeNormalClose':False")
    s=s.replace("'ownedExplicitStops':4,'eightTerminalReceipts':True","'ownedExplicitStops':0,'currentOriginalTerminalHistoryRetained':True")
    compile(s,'<independent current finite retirement post>','exec');return s

ORIGINAL=r'''
parser_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
n=next(n for n in ast.parse(parser_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re}
exec(compile(ast.Module(body=[n],type_ignores=[]),'<strict independent actual declaration parser>','exec'),env)
require(retirement.same_except_runtime(before,after,env['exec_record']))
original=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1216-native-stop-v1/after.private.json');raw=original.read_bytes()
require(hashlib.sha256(raw).hexdigest()=='21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36')
require({k:v for k,v in before.items()if k!='native'}==json.loads(raw))
'''

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current source required')
    if(W/'pg1235-retire-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual current normal retirement required')
    build=json.loads((W/'pg1233-frozen-v1.safe.json').read_bytes())
    if build['actualExit']!=0:raise ValueError('current immutable ABI required')
    hashes=build['fileHashes'];receipt=(W/'pg1232-native-tools-v1/pg1232_parent_receipt.py').read_text()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    seals=json.loads(subprocess.check_output(ssh,input=previous.SEAL.replace('pg642-native-stop-v1','pg1232-native-stop-v1').encode(),timeout=20))
    if seals!=SEALS:raise ValueError('actual private qualified seals changed')
    code='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload()
    base=W/'pg1236-completed-runtime-retired-post-v1'
    if any(Path(str(base)+x).exists()for x in ['.private.log','.exit','.safe.json']):raise ValueError('new-only independent post required')
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({k:v for k,v in value.items()if k not in ['proofHashes','toolHashes']}));return r.returncode

if __name__=='__main__':raise SystemExit(main())
