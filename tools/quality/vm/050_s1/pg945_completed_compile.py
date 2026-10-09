"""Fresh full helper ABI, independent generated oracles and immutable source slots.
No actual guest operation; installed e016 classes, new candidate40ef remains unused.
"""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg942_completed_sources import sources
from pg864_compile_v2 import regenerated
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
if __name__=='__main__':
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain']);head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    for name in ('pg943_completed_binding_test.py',):subprocess.run(['python3','-B',str(R/name)],check=True)
    assert json.loads((W/'pg938-independent-stage-post-v1.safe.json').read_bytes())['actualExit']==0
    old=W/'pg864-completed-tools-v3';frozen=json.loads((W/'pg864-frozen-v3.safe.json').read_bytes());assert frozen['actualExit']==0
    target=W/'pg942-completed-tools-v1';assert not target.exists();target.mkdir(mode=0o700)
    for name,digest in frozen['fileHashes'].items():
        f=old/name;assert hashlib.sha256(f.read_bytes()).hexdigest()==digest
        if name.endswith('.class')and not regenerated(name)and not name.startswith('Pg864CompletedDeployment'):
            with(target/name).open('xb')as stream:os.fchmod(stream.fileno(),0o400);stream.write(f.read_bytes())
    raw=sources()
    for n,value in raw.items():
        if n.endswith('.py'):ast.parse(value)
        with(target/n).open('x')as stream:os.fchmod(stream.fileno(),0o400);stream.write(value);stream.flush();os.fsync(stream.fileno())
    release=W/'pg862-release-v1';cp=':'.join(map(str,(target,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*')))
    m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(m2/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),*[str(target/n)for n in raw if n.endswith('.java')]])]+[(n,[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,n])for n in ('Pg942CompletedDeploymentTest','Pg797OwnedDatabaseTest','Pg798DatabaseScopeTest')]
    logs={}
    for phase,args in commands:
        log=W/('pg945-'+phase+'-v1.private.log')
        with log.open('xb')as stream:r=subprocess.run(args,stdout=stream,stderr=stream);stream.flush();os.fsync(stream.fileno())
        logs[phase]=hashlib.sha256(log.read_bytes()).hexdigest()
        if r.returncode:print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':logs[phase]}));raise SystemExit(r.returncode)
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in target.iterdir()}
    for p in target.iterdir():p.chmod(0o400)
    with(target/'payload-sha256.json').open('x')as stream:os.fchmod(stream.fileno(),0o400);json.dump(files,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    assert not subprocess.check_output(['git','status','--porcelain'])and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
    safe={'run':'PG945-compile-v1','actualExit':0,'operatorSource':head,'installedSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','candidateSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','fileHashes':files,'logHashes':logs,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMutation0':True,'formalAccepted':False,'toolsDirectory':'pg942-completed-tools-v1'}
    with(W/'pg945-frozen-v1.safe.json').open('x')as stream:json.dump(safe,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'actualExit':0,'files':len(files),'Werror0':True,'independentOracle0':True,'guestMutation0':True,'formalAccepted':False}))
