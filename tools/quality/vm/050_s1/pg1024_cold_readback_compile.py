"""Freeze owned-cold readback against approved932 ABI, no guest or business mutation."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg1023_cold_readback_sources import files

T=Path(__file__).resolve().parents[4]
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
    with p.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(data);f.flush();os.fsync(f.fileno())
def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    target=W/'pg1023-cold-tools-v1';target.mkdir(mode=0o700)
    write(target/'begin.safe.json',json.dumps({'operatorSource':head,'startedUTC':start,'readbackOnly':True,'guestActions':0}).encode())
    old=W/'pg983-bootstrap-tools-v3'
    previous=json.loads((W/'pg983-frozen-v3.safe.json').read_bytes())
    assert previous['actualExit']==0 and previous['productionSource']=='40ef6e894573d2ffab1d1732124960f9c98d5f97'
    for name,digest in previous['fileHashes'].items():
        p=old/name;assert sha(p)==digest
        if name.endswith('.class'):write(target/name,p.read_bytes())
    for name,raw in files().items():
        if name.endswith('.py'):ast.parse(raw)
        write(target/name,raw.encode())
    release=W/'pg932-release-v1'
    cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in (
      'com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
      'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
      'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    commands=[('python-oracle',['python3','-B',str(R/'pg1023_cold_contract_test.py')]),
      ('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg1023ColdOwnedReadback.java'),str(target/'Pg1023ColdOwnedReadbackTest.java')]),
      ('java-oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1023ColdOwnedReadbackTest'])]
    phases=[]
    for phase,command in commands:
        log=target/(phase+'.private.log')
        with log.open('xb')as f:r=subprocess.run(command,cwd=T,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        write(target/(phase+'.exit'),(str(r.returncode)+'\n').encode())
        phases.append({'phase':phase,'command':command,'actualExit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()==head
    code=phases[-1]['actualExit']
    hashes={p.name:sha(p)for p in target.iterdir()if p.is_file()}
    for p in target.iterdir():p.chmod(0o400)
    write(target/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    result={'run':'PG1024-cold-readback-compile-v1','actualExit':code,'operatorSource':head,
      'productionSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','startedUTC':start,
      'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':phases,
      'fileHashes':hashes,'guestActions':0,'readbackOnly':True,'fullColdPreparationAccepted':False,'formalAccepted':False}
    write(W/'pg1024-cold-readback-frozen-v1.safe.json',json.dumps(result,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in result.items()if k not in ('phases','fileHashes')}));raise SystemExit(code)

if __name__=='__main__':main()
