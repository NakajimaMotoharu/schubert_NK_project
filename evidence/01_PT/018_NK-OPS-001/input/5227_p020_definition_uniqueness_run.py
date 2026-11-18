"""Run synthetic characterization tests in isolated local scratch, with pinned original tool inputs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path.cwd()
E=Path('evidence/01_PT/018_NK-OPS-001/evidence')
D=Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
PACKAGE='dev.codex.schubert.characterization.'
B=Path('program/characterization')
P=Path('dev/codex/schubert/characterization')
TC=ROOT.parent/'toolchain'
JDK=TC/'jdk-25.0.4/bin'
METHODS=('rejectsRepeatedCaseDefinitionEvenWhenTwentyFourCasesStillCompare',
         'rejectsRepeatedDifferenceDefinitionEvenWhenSixteenRulesStillMatch')
MAIN_PATH=B/'src/main/java'/P/'ArtifactComparator.java'
TEST_PATH=B/'tests/java'/P/'ArtifactComparatorTest.java'
GATE_SOURCE=B/'src/main/java'/P/'GateCli.java'
GATE_TEST=B/'tests/java'/P/'GateCliTest.java'
PHASE_CHANGES={'red':{TEST_PATH},'green':{TEST_PATH,MAIN_PATH},
               'corrected':{TEST_PATH,MAIN_PATH,GATE_SOURCE,GATE_TEST}}
MAVEN=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ref(p):
    return dict(path=str(p),sha256=sha(p))


def git(*cmd):
    return subprocess.check_output(['git',*cmd],timeout=60)


def read(p):
    return json.loads(Path(p).read_bytes())


def save(p,v):
    with Path(p).open('x') as f:
        json.dump(v,f,ensure_ascii=False,indent=2)
        f.write('\n')


def get_sdk(original):
    repo=TC/'m2/repository'
    extras={
        'junit-platform-console-standalone-1.13.4.jar':TC,
        'org.jacoco.cli-0.8.15-nodeps.jar':TC,
        'org.jacoco.agent-0.8.15-runtime.jar':repo/'org/jacoco/org.jacoco.agent/0.8.15',
        'jspecify-1.0.1.jar':repo/'org/jspecify/jspecify/1.0.1',
        'playwright-1.55.0.jar':repo/'com/microsoft/playwright/playwright/1.55.0',
    }
    for name in ('jackson-annotations','jackson-core','jackson-databind'):
        extras[name+'-2.19.2.jar']=repo/'com/fasterxml/jackson/core'/name/'2.19.2'
    sdk={name:folder/name for name,folder in extras.items()}
    assert {n:sha(p) for n,p in sdk.items()}==original['sdkHashes']
    return sdk


def step(label, command, work, public, timeout=90):
    env={'JAVA_HOME':str(JDK.parent),'PATH':f'{JDK}:/usr/bin:/bin',
         'HOME':os.environ['HOME'],'LANG':'C.UTF-8'}
    start=utc()
    receipt=dict(command=command,cwd=str(work),startUTC=start)
    save(public/(label+'-begin.json'),receipt)
    path=public/(label+'.log')
    with path.open('xb') as log:
        try:
            code=subprocess.run(command,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            code=124
        log.flush()
        os.fsync(log.fileno())
    receipt.update(actualExit=code,terminalAtUTC=utc(),log=ref(path))
    save(public/(label+'-exit.json'),receipt)
    return receipt


def physical(folder):
    return {str(p.relative_to(folder)):sha(p) for p in sorted(folder.rglob('*.class'))}


def collect_inputs(source, original, allowed_tests, helpers, phase):
    history=original['sourceHashes']
    tree={Path(p) for p in git('ls-tree','-r','--name-only',source,'--',str(B)).decode().splitlines()}
    assert tree==set(map(Path,history))
    changed=set(map(Path,git('diff','--name-only',original['sourceCore'],source,'--',str(B)).decode().splitlines()))
    assert changed==PHASE_CHANGES[phase]
    test_root=B/'tests/java'/P
    allowed={test_root/(name+'.java') for name in allowed_tests}
    allowed.update(Path(row['path']) for row in helpers)
    assert allowed<=tree
    main={path for path in tree if path.is_relative_to(B/'src/main/java')}
    assert len(main)==6
    inputs=main|allowed|{path for path in tree if not path.is_relative_to(B/'tests/java')}
    data={str(p):git('show',f'{source}:{p}') for p in sorted(inputs|{Path('pom.xml')})}
    hashes={p:hashlib.sha256(raw).hexdigest() for p,raw in data.items()}
    for p in inputs-changed:
        assert hashes[str(p)]==history[str(p)]
    assert len([p for p in data if p.startswith(str(B/'baseline/current')+'/')])==27
    return data,hashes,sorted(map(str,main)),[str(test_root/(n+'.java')) for n in allowed_tests]


def main(phase):
    assert phase in PHASE_CHANGES and os.getuid()!=0
    start=read(next(D.glob('507_*')))
    parent,old_unit,old_package=[Path(x['path']) for x in start['values']['oracleReferences']]
    for path,pin in zip((parent,old_unit,old_package),start['values']['oracleReferences'],strict=True):
        assert ref(path)==pin
    original=read(old_package)
    assert read(old_unit)['success']==142
    audit=read(next(E.glob('PG37004*/manifest.json')))
    sdk=get_sdk(original)
    selection=['ArtifactComparatorTest','CorrelatedLogEvidenceValidatorTest'] if phase=='red' else original['selectedSuites']
    source=git('rev-parse','HEAD').decode().strip()
    assert not git('diff','--name-only','HEAD','--',str(B))
    data,inputs,srcs,selected=collect_inputs(source,original,selection,audit['helperReferences'],phase)
    name={'red':'PG39822-p020-definition-red-v1','green':'PG39826-p020-definition-green144-v1',
          'corrected':'PG39828-p020-definition-green144-v2'}[phase]
    out=E/name
    work=ROOT.parent/'pgpt-runs/PG379'/name.lower()
    assert not out.exists() and not work.exists()
    out.mkdir()
    work.mkdir(mode=0o700)
    snapshot=work/'snapshot'
    for loc,bytes_ in data.items():
        path=snapshot/loc
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(bytes_)
    cp=':'.join(str(p) for name,p in sdk.items() if 'jacoco' not in name)
    test=work/'testclasses'
    tmp=work/'case-temp'
    xml=out/'xml'
    for folder in (test,tmp,xml):
        folder.mkdir(mode=0o700)
    if phase=='red':
        classes=work/'mainclasses'
        classes.mkdir()
        compile_main=[str(JDK/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,
                      '-d',str(classes),*(str(snapshot/p) for p in srcs)]
        expression=[x for n in METHODS for x in ('--select-method',PACKAGE+'ArtifactComparatorTest#'+n)]
    else:
        classes=snapshot/B/'target/classes'
        compile_main=[str(MAVEN),'-o','-B','-ntp','-N',f'-Dmaven.repo.local={TC}/m2/repository',
                      '-f',str(snapshot/B/'pom.xml'),'compile']
        expression=[x for n in selection for x in ('--select-class',PACKAGE+n)]
    expected=2 if phase=='red' else 144
    build=ref(snapshot/'pom.xml')
    save(out/'begin.json',dict(groupStart=start['eventId'],source=source,phase=phase,snapshot=str(snapshot),origin=ref(old_package),
        exactScope=selection,expected=expected,inputHashes=inputs,rootPom=build,tools={n:ref(p) for n,p in sdk.items()},
        jdk=ref(JDK/'java'),javaC=ref(JDK/'javac'),temp=str(tmp),os=os.uname().sysname,
        kernel=os.uname().release,startedAtUTC=utc(),backendActions=0))
    stages={}
    stages['main']=step('main',compile_main,work,out)
    if stages['main']['actualExit']==0:
        stages['test']=step('test',[str(JDK/'javac'),'-Xlint:all','-Werror','--release','25',
            '-cp',str(classes)+':'+cp,'-sourcepath',str(snapshot/B/'tests/java'),'-d',str(test),
            *(str(snapshot/path) for path in selected)],work,out)
    session=name.split('-')[0]+'-COMMON-'+str(expected)
    if stages.get('test',{}).get('actualExit')==0:
        agent=sdk['org.jacoco.agent-0.8.15-runtime.jar']
        coverage=[f'-javaagent:{agent}=destfile={out.resolve()/"jacoco.exec"},sessionid={session},append=false'] if phase!='red' else []
        cmd=[str(JDK/'java'),'-Xmx1g','-Djava.awt.headless=true','-Duser.language=ja','-Duser.country=JP',
             '-Duser.timezone=Asia/Tokyo','-Dchr.unitProjectRoot='+str(snapshot),
             '-Djava.io.tmpdir='+str(tmp),'-Xlog:class+init=info:file='+str(work/'class-init.log'),*coverage,
             '-jar',str(sdk['junit-platform-console-standalone-1.13.4.jar']),'execute',
             '--disable-banner','--details=summary','--fail-if-no-tests','--class-path',
             ':'.join([str(classes),str(test),str(snapshot/B/'tests/resources'),cp]),
             '--reports-dir',str(xml.resolve()),*expression,'--config=junit.jupiter.execution.parallel.enabled=false']
        stages['unit']=step('unit',cmd,work,out,180)
    if phase!='red' and stages.get('unit',{}).get('actualExit')==0:
        cli=[str(JDK/'java'),'-jar',str(sdk['org.jacoco.cli-0.8.15-nodeps.jar'])]
        exec_=str(out.resolve()/'jacoco.exec')
        stages['coverage']=step('coverage',[*cli,'report',exec_,'--classfiles',str(classes),
                                 '--xml',str(out.resolve()/'coverage.xml')],work,out)
        stages['execinfo']=step('execinfo',[*cli,'execinfo',exec_],work,out)
        stages['classinfo']=step('classinfo',[*cli,'classinfo',str(classes)],work,out)
    init=work/'class-init.log'
    assert all(sha(snapshot/p)==h for p,h in inputs.items())
    value=dict(source=source,phase=phase,expected=expected,run=name,session=session,classesDir=str(classes),
         testsDir=str(test),inputHashes=inputs,mainPhysical=physical(classes),testPhysical=physical(test),
         initLog=None if not init.is_file() else ref(init),stages=stages,newAcceptance=0,official=False,
         sourceInputsUnchanged=True,actualBackendActions=0,terminalAtUTC=utc(),
         xmlHashes={p.name:sha(p) for p in sorted(xml.glob('*.xml'))},verifier=ref(Path(__file__)))
    save(out/'manifest.json',value)
    print({k:v['actualExit'] for k,v in stages.items()},ref(out/'manifest.json'))
    return next((row['actualExit'] for row in stages.values() if row['actualExit']!=0),0)


if __name__=='__main__':
    assert len(sys.argv)==2
    raise SystemExit(main(sys.argv[1]))
