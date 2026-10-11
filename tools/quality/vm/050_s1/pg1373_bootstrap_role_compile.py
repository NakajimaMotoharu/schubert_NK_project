"""Freeze exact current full management ABI + qualified one-role helper, no VM mutation."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg1372_bootstrap_role_sources as source

R=Path(__file__).resolve().parent;W=source.W;SOURCE=source.SOURCE
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean immutable tool source required')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']):raise ValueError('unchanged current main source required')
    if (W/'pg1368-bootstrap-fixed-ref-handoff-v1.exit').read_bytes()!=b'0\n':raise ValueError('prior exact owner recovery0 required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc)
    subprocess.run(['python3','-B',str(R/'pg1372_bootstrap_role_sources_test.py')],check=True)
    target=W/'pg1372-bootstrap-role-tools-v1';target.mkdir(mode=0o700)
    base=W/'pg1334-native-tools-v1';frozen=json.loads((W/'pg1335-frozen-v1.safe.json').read_bytes())
    rolebase=W/'pg1371-bootstrap-role-host-v2';role=json.loads((rolebase/'manifest.safe.json').read_bytes())
    if frozen['actualExit']!=0 or role['actualExit']!=0 or role['productionSource']!=SOURCE:raise ValueError('qualified full ABI and19fault-role fixture required')
    # The first fixture manifest pinned source/dependencies, not generated class bytes.
    # This bounded replay has a byte-qualification trigger before VM transfer, no new PT credit.
    role_classes={str(p.relative_to(rolebase)):sha(p)for p in rolebase.rglob('*.class')}
    for name,digest in role['sourceHashes'].items():
        if sha(R/name)!=digest:raise ValueError('unchanged independent role source required')
    release=W/'pg1292-release-v1';repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    role_cp=':'.join(map(str,(rolebase,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    for name,digest in role['runtimeLibraryHashes'].items():
        if sha(repo/name)!=digest:raise ValueError('same qualified fixture runtime required')
        role_cp+=':'+str(repo/name)
    role_log=W/'pg1373-role-byte-oracle-v1.private.log'
    with role_log.open('xb')as f:
        role_result=subprocess.run([str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',role_cp,'dev.codex.schubert.nk.batch.file.Pg1370BootstrapRoleDirectoryTest'],stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    if role_result.returncode!=0 or role_classes!={str(p.relative_to(rolebase)):sha(p)for p in rolebase.rglob('*.class')}:raise ValueError('same byte full fault fixture qualification required')
    for name,digest in frozen['fileHashes'].items():
        if name.endswith('.class')and '/'not in name:
            if sha(base/name)!=digest:raise ValueError('flat ABI SHA required')
            with(target/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write((base/name).read_bytes())
    for name in ('Pg1370BootstrapRoleDirectory.class','Pg1370BootstrapRoleDirectory$1.class','Pg1370BootstrapRoleDirectory$Io.class'):
        p=rolebase/'dev/codex/schubert/nk/batch/file'/name
        if not p.is_file():raise ValueError('complete qualified native role class family required')
        dst=target/'dev/codex/schubert/nk/batch/file'/name;dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(p.read_bytes())
    values=source.files();values['Pg1372BootstrapRoleArgumentTest.java']=(R/'Pg1372BootstrapRoleArgumentTest.java').read_text()
    for name,raw in values.items():
        if name.endswith('.py'):ast.parse(raw)
        with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(raw)
    release=W/'pg1292-release-v1';cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(repo/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    phases={}
    commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg1372BootstrapRolePreparation.java'),str(target/'Pg1372BootstrapRoleArgumentTest.java')]),
              ('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1372BootstrapRoleArgumentTest'])]
    for phase,argv in commands:
        log=W/('pg1373-'+phase+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(argv,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases[phase]={'actualExit':r.returncode,'logSha256':sha(log)}
        if r.returncode:break
    hashes={str(p.relative_to(target)):sha(p)for p in target.rglob('*')if p.is_file()}
    for p in target.rglob('*'):
        if p.is_file():p.chmod(0o400)
    with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(hashes,f,sort_keys=True)
    same=head==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain'])
    result={'actualExit':r.returncode,'productionSource':SOURCE,'operatorSource':head,'sameOperatorHead':same,'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fileHashes':hashes,'phases':phases,'roleFixtureManifestSha256':sha(rolebase/'manifest.safe.json'),'roleClassHashesQualified':role_classes,'roleByteOracleExit':role_result.returncode,'roleByteOracleLogSha256':sha(role_log),'qualificationTrigger':'same actual generated role class bytes before VM transfer; first manifest had source but no class hashes; no new PT credit','formalAccepted':False,'vmActions0':True}
    with(W/'pg1373-frozen-v1.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps({k:v for k,v in result.items()if k!='fileHashes'}));return r.returncode if same else 1

if __name__=='__main__':raise SystemExit(main())
