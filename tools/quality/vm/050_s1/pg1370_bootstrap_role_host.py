"""Compile/run actual held-directory fault fixture against current signed jars; VM actions0."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed tool sources required')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']):raise ValueError('current main source unchanged required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    release=W/'pg1292-release-v1';manifest=json.loads((release/'RELEASE-MANIFEST.json').read_bytes())
    if manifest['source']['commit']!=SOURCE or sha(release/'RELEASE-MANIFEST.json')!='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99':raise ValueError('exact current signed candidate required')
    for value in manifest['artifacts']:
        path=release/value['path']
        if path.stat().st_size!=value['size']or sha(path)!=value['sha256']:raise ValueError('whole187 current byte match required')
    target=W/'pg1370-bootstrap-role-host-v1';target.mkdir(mode=0o700)
    old=W/'pg1334-native-tools-v1';frozen=json.loads((W/'pg1335-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE:raise ValueError('current frozen independent fixture ABI required')
    fixtures={name:digest for name,digest in frozen['fileHashes'].items()if name.startswith('dev/codex/schubert/nk/batch/file/BackupPublicationFixture')and name.endswith('.class')}
    if len(fixtures)!=4:raise ValueError('complete independent fixture nested class set required')
    for name,digest in fixtures.items():
        if sha(old/name)!=digest:raise ValueError('fixture byte qualification required')
        path=target/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write((old/name).read_bytes())
    sources=[R/'Pg1370BootstrapRoleDirectory.java',R/'Pg1370BootstrapRoleDirectoryTest.java']
    cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    phases={};start=datetime.datetime.now(datetime.timezone.utc)
    commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),*map(str,sources)]),
              ('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'dev.codex.schubert.nk.batch.file.Pg1370BootstrapRoleDirectoryTest'])]
    for phase,args in commands:
        log=target/(phase+'.private.log')
        with log.open('xb')as f:
            r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases[phase]={'actualExit':r.returncode,'logSha256':sha(log)}
        if r.returncode:break
    current=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    same=current==head and not subprocess.check_output(['git','status','--porcelain'])
    result={'run':'PG1370-bootstrap-role-host-v1','actualExit':r.returncode,'productionSource':SOURCE,'operatorSource':head,'sameOperatorHead':same,'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceHashes':{p.name:sha(p)for p in sources},'fixtureHashes':fixtures,'phases':phases,'vmActions0':True,'syntheticRootTmpfsOnly':True,'productionPtDelta':0,'formalAccepted':False}
    with(target/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps({k:v for k,v in result.items()if k not in ('sourceHashes','fixtureHashes')}))
    return r.returncode if same else 1

if __name__=='__main__':raise SystemExit(main())
