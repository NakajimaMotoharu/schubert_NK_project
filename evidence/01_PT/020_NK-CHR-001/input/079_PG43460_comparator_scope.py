from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, subprocess
r=Path.cwd().parent/'pgpt-runs/PG379'
v2=r/'PG43460-comparator-name-types-current-v2'
v3=r/'PG43460-comparator-name-types-current-v3'
ref=r/'PG43030-chr-nk-only-definition-v1'
get=lambda path:json.loads(path.read_bytes())
def put(path,data):
    with path.open('x') as out:
        out.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def pin(path):
    return {'path':str(path),'sha256':sha256(Path(path).read_bytes()).hexdigest()}
def now():return datetime.now(timezone.utc).isoformat()
d=get(v2/'begin.json')
p=get(ref/'begin.json')
assert get(v2/'terminal.json')['results']=={'scopeGuard':0,'style':0,'compileMain':0,'compileTest':1}
assert subprocess.check_output(['git','diff','--name-only',d['source'],'HEAD','--','program/characterization']).strip()==b''
for item in d['sourceFiles']+d['deps']+d['syntheticResources']:
    assert pin(item['path'])==item
physical=get(v2/'physical.json')['currentPhysical']
for file,digest in physical.items():
    assert pin(v2/'product'/file)['sha256']==digest
helpers=[]
for name in ('CorrelatedLogEvidenceValidatorTest.java','CorrelatedMenuActionContractTest.java'):
    qualified=[Path(x) for x in p['commands']['compile-tests'] if x.endswith('/'+name)]
    assert len(qualified)==1
    qual,=qualified
    current=qual.relative_to(ref/'snapshot')
    for source in [p['source'],d['source'],'HEAD']:
        assert current.read_bytes()==subprocess.check_output(['git','show',f'{source}:{current}'])
    assert current.read_bytes()==qual.read_bytes()
    helpers.append(current)
v3.mkdir()
for n in ('tests','reports','temp'):
    (v3/n).mkdir()
cmds={}
for k in ('compileTest','unit','analyse'):
    args=[]
    for arg in d['commands'][k]:
        for n in ['tests','reports','temp','initialization.log','unit.exec']:
            arg=arg.replace(str(v2/n),str(v3/n))
        arg=arg.replace('sessionid=PG43460-DEF25,','sessionid=PG43460-DEF25-V3,')
        args.append(arg)
    cmds[k]=args
cmds['compileTest']+=list(map(str,helpers))
put(v3/'begin.json',dict(source=d['source'],startedAtUTC=now(),originalBegin=pin(v2/'begin.json'),
    originalTerminal=pin(v2/'terminal.json'),originalPhysical=pin(v2/'physical.json'),
    earlierHelperQualification=pin(ref/'begin.json'),helpers=[pin(h) for h in helpers],commands=cmds))
results={}
try:
    for k,cmd in cmds.items():
        with (v3/f'{k}.stdout').open('xb') as out,(v3/f'{k}.stderr').open('xb') as err:
            results[k]=subprocess.run(cmd,stdout=out,stderr=err,timeout=65).returncode
        if results[k]:
            break
finally:
    put(v3/'terminal.json',dict(source=d['source'],results=results,terminalAtUTC=now()))
print(results)
assert results=={k:0 for k in cmds}
