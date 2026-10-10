"""Source-fixed new-only cold operator build against qualified PG932 ABI."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1037_cold_preparation_sources import files

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):
    with path.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(data);f.flush();os.fsync(f.fileno())


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean source required')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    out=W/'pg1037-cold-tools-v1';out.mkdir(mode=0o700)
    write(out/'begin.safe.json',json.dumps({'operatorSource':source,'startedUTC':start,'formalAccepted':False}).encode())
    previous=json.loads((W/'pg983-frozen-v3.safe.json').read_bytes())
    if previous['actualExit']!=0 or previous['productionSource']!='40ef6e894573d2ffab1d1732124960f9c98d5f97':raise ValueError('qualified helpers required')
    for name,digest in previous['fileHashes'].items():
        p=W/'pg983-bootstrap-tools-v3'/name
        if sha(p)!=digest:raise ValueError('old helper changed')
        if name.endswith('.class'):write(out/name,p.read_bytes())
    for name,text in files().items():
        if name.endswith('.py'):ast.parse(text)
        write(out/name,text.encode())
    release=W/'pg932-release-v1';cp=':'.join(map(str,[out,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[('python-oracle',['python3','-B',str(HERE/'pg1037_cold_preparation_sources_test.py'),'-v']),
              ('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(out),str(out/'Pg1037ColdOwnedPreparation.java'),str(out/'Pg1037ColdOwnedPreparationTest.java')]),
              ('java-oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1037ColdOwnedPreparationTest'])]
    phases=[]
    for phase,command in commands:
        log=out/(phase+'.private.log')
        with log.open('xb')as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        write(out/(phase+'.exit'),(str(r.returncode)+'\n').encode())
        phases.append({'phase':phase,'command':command,'actualExit':r.returncode,'logSha256':sha(log)})
        if r.returncode:break
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=source:raise ValueError('source moved during build')
    hashes={p.name:sha(p)for p in out.iterdir()if p.is_file()}
    for p in out.iterdir():p.chmod(0o400)
    write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    value={'run':'PG1038-cold-preparation-compile-v1','actualExit':phases[-1]['actualExit'],'operatorSource':source,'productionSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':phases,'fileHashes':hashes,'guestActions':0,'formalAccepted':False,'fullColdPreparationAccepted':False}
    write(W/'pg1038-cold-preparation-frozen-v1.safe.json',json.dumps(value,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in value.items()if k not in ('phases','fileHashes')}));raise SystemExit(value['actualExit'])


if __name__=='__main__':main()
