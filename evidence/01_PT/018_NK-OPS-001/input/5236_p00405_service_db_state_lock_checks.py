"""Analyze the current Bootstrap closure and run only the exact two synthetic JDBC port suites."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import gzip
import json
import runpy
import sys
from xml.etree import ElementTree as ET

HERE=Path(__file__)
B=runpy.run_path(str(HERE.with_name('5235_p00405_service_db_state_lock_build.py')))
R=B['R']
Q=runpy.run_path(str(HERE.with_name('5224_f03_storage_bootstrap_module_static.py')))
E=B['E']
BUILD=B['OUT']/'manifest.json'
JDK,TC,ROOT=R['JDK'],R['TC'],R['ROOT']
read,save,ref,git=R['read'],R['save'],R['ref'],R['git']
PKG='dev.codex.schubert.nk.api.bootstrap.'
TESTROOT='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/'
SUITES=('ServiceDatabaseAdmissionPortTest','ServiceDatabaseSourcePortTest')
CHANGED_TEST=TESTROOT+SUITES[1]+'.java'
CASE='dbSource016ConnectorFailureReleasesTheStateLockForAnotherThread()'
ASSURE=E/'PG39864-service-db-state-lock-static-v1'
UNIT=E/'PG39866-service-db-state-lock-unit-v1'


def compiler_tools():
    repo=TC/'m2/repository'
    return dict(junit=TC/'junit-platform-console-standalone-1.13.4.jar',
        jspecify=repo/'org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',
        agent=repo/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar',
        cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar')


def current():
    build=read(BUILD)
    assert build['actualExit']==0 and build['inputHashesReverified']
    assert build['unitSource']==git('rev-parse','HEAD').decode().strip()
    work=Path(build['cwd'])
    classes={m:work/f'src/schubert-nk-{m}/target/classes' for m in B['MODS']}
    assert all(R['physical'](p)==build['physicalClassHashes'][m] for m,p in classes.items())
    return build,work,classes


def create_tests(build,work):
    paths={TESTROOT+suite+'.java' for suite in SUITES}
    old_source=read(next(E.glob('PG39476*/manifest.json')))['source']
    for name in sorted(paths):
        data=git('show',f'{build["unitSource"]}:{name}')
        before=git('show',f'{old_source}:{name}')
        if name==CHANGED_TEST:
            assert b'dbSource016ConnectorFailureReleasesTheStateLockForAnotherThread' in data
            assert data[:data.index(b'\n\n  @Test\n  void dbSource016')]+b'\n}\n'==before
        else:
            assert before==data
        assert Path(name).read_bytes()==data
        file=work/name
        file.parent.mkdir(parents=True,exist_ok=True)
        if file.exists():
            assert file.read_bytes()==data
        else:
            file.write_bytes(data)
    return sorted(paths)


def replace_recipe(paths,old_home,work,extra):
    result=[]
    for part in paths:
        for previous,new in extra.items():
            if part==previous:
                part=new
                break
        result.append(part.replace(str(old_home),str(work)))
    return result


def static():
    build,work,classes=current()
    paths=create_tests(build,work)
    out=ASSURE.resolve()
    out.mkdir()
    tc=compiler_tools()
    compiled=work/'selected-test-classes'
    compiled.mkdir()
    cp=':'.join(map(str,[classes['bootstrap'],classes['storage'],tc['jspecify']]))
    sources={s:ref(work/s)['sha256'] for s in (B['MAIN'],CHANGED_TEST)}
    quick=next(E.glob('PG39810*/begin.json'))
    original=read(quick)['exactCommands']
    previous_home=Path(read(next(E.glob('PG39804*/compile/manifest.json')))['cwd'])
    commands={}
    pmd_xml=out/'pmd.xml'
    cs_xml=out/'checkstyle.xml'
    listing=out/'sources.txt'
    listing.write_text(''.join(f'{work/s}\n' for s in sources))
    for lbl,dest in (('pmd',pmd_xml),('checkstyle',cs_xml)):
        prior=original[lbl]
        old_list=quick.resolve().with_name('sources.txt')
        names={str(old_list):str(listing),'@'+str(old_list):'@'+str(listing),
               str(quick.resolve().with_name(lbl+'.xml')):str(dest)}
        commands[lbl]=replace_recipe(prior,previous_home,work,names)
    commands['formatter']=[*original['formatter'][:6],*[str(work/s) for s in sources]]
    boot_path=next(E.glob('PG39812*/begin.json'))
    boot=read(boot_path)['command']
    aux=out/'spotbugs-aux.txt'
    aux.write_text((boot_path.parent/'spotbugs-aux.txt').read_text().replace(str(previous_home),str(work)))
    replace_paths={str(boot_path.resolve().with_name('spotbugs-aux.txt')):str(aux),
              str(boot_path.resolve().with_name('spotbugs.xml')):str(out/'spotbugs.xml')}
    commands['spotbugs']=replace_recipe(boot[:-2]+[boot[-1]],previous_home,work,replace_paths)
    commands['test-compile']=[str(JDK/'javac'),'--release','25','-g','-proc:none','-implicit:none',
        '-encoding','UTF-8','-Xlint:all','-Werror','-cp',cp+':'+str(tc['junit']),'-d',str(compiled),
        *(str(work/test) for test in paths)]
    save(out/'begin.json',dict(source=build['sourceCore'],unitSource=build['unitSource'],build=ref(BUILD),
        commands=commands,sourceHashes=sources,selectedTests={s:ref(work/s)['sha256'] for s in paths},
        activeRuntimeActions=0,startedAtUTC=R['utc']()))
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(Q['run'],name,args,out,work) for name,args in commands.items()]
        stages=dict(job.result() for job in jobs)
    stage_exits={key:row['actualExit'] for key,row in stages.items()}
    expected={'pmd':4,'checkstyle':0,'formatter':0,'spotbugs':0,'test-compile':0}
    physical=set(build['physicalClassHashes']['bootstrap'])
    reports={x:Q['parse_report'](x,out/(x+'.xml'),work,sources,physical)
             for x in ('pmd','checkstyle','spotbugs')}
    tests=R['physical'](compiled)
    save(out/'manifest.json',dict(actualExits=stage_exits,source=build['sourceCore'],unitSource=build['unitSource'],
       operatorExit=0 if stage_exits==expected else 1,scope=reports,toolchain={n:ref(file) for n,file in tc.items()},
       testsDir=str(compiled),testClassHashes=tests,declaredClassPaths={m:str(p) for m,p in classes.items()},
       executedTests=0,staticRawOnly=True,whole451Accepted=False,terminalAtUTC=R['utc'](),verifier=ref(HERE)))
    print(stage_exits,reports)
    return 0 if stage_exits==expected else 1


def unit():
    build,work,classes=current()
    a=read(ASSURE/'manifest.json')
    admission=read(ASSURE/'admission.json')
    assert admission['static']==ref(ASSURE/'manifest.json') and not admission['applicable'] and not admission['unclassified']
    assert a['operatorExit']==0 and a['source']==build['sourceCore'] and a['unitSource']==build['unitSource']
    assert R['physical'](Path(a['testsDir']))==a['testClassHashes']
    jars=compiler_tools()
    assert {n:ref(p) for n,p in jars.items()}==a['toolchain']
    slot=UNIT.resolve()
    slot.mkdir()
    tmp=work/'unit-tmp'
    xml=slot/'xml'
    tmp.mkdir(mode=0o700)
    xml.mkdir()
    test_cp=':'.join(map(str,[a['testsDir'],classes['bootstrap'],classes['storage'],jars['jspecify']]))
    label='PG39866-SERVICE-DB-STATE-LOCK-32'
    ex=slot/'jacoco.exec'
    logs=work/'class-init.log'
    command=[str(JDK/'java'),'-Xmx1g','-Djava.awt.headless=true','-Duser.language=ja','-Duser.country=JP',
        '-Duser.timezone=Asia/Tokyo','-Djava.io.tmpdir='+str(tmp),
        f'-Xlog:class+init=info:file={logs}',f'-javaagent:{jars["agent"]}=destfile={ex},sessionid={label},append=false',
        '-jar',str(jars['junit']),'execute','--disable-banner','--details=summary','--fail-if-no-tests',
        '--class-path',test_cp,'--reports-dir',str(xml),
        *[x for name in SUITES for x in ('--select-class',PKG+name)],
        '--config=junit.jupiter.execution.parallel.enabled=false']
    save(slot/'begin.json',dict(source=build['sourceCore'],unitSource=build['unitSource'],session=label,
       expected=32,newName=CASE,command=command,knownInputs=ref(ASSURE/'admission.json'),startedAtUTC=R['utc']()))
    _,r=Q['run']('unit',command,slot,work)
    stages={'unit':r}
    if ex.is_file():
        c=[str(JDK/'java'),'-jar',str(jars['cli'])]
        _,row=Q['run']('execinfo',[*c,'execinfo',str(ex)],slot,work)
        stages['execinfo']=row
    if logs.is_file():
        (slot/'class-init.log.gz').write_bytes(gzip.compress(logs.read_bytes(),mtime=0))
    save(slot/'manifest.json',dict(actualExits={n:x['actualExit'] for n,x in stages.items()},source=build['sourceCore'],
       unitSource=build['unitSource'],run=label,casesExpected=32,
       originalStatic=ref(ASSURE/'manifest.json'),build=ref(BUILD),
       classes=classes['bootstrap'].as_posix(),applicationActions=0,tests=[PKG+n for n in SUITES],
       files={str(p.relative_to(slot)):ref(p)['sha256'] for p in slot.rglob('*') if p.is_file()},
       terminalAtUTC=R['utc'](),verifier=ref(HERE)))
    print({n:x['actualExit'] for n,x in stages.items()})
    return r['actualExit']


if __name__=='__main__':
    assert sys.argv[1:] in (['static'],['unit'])
    raise SystemExit(static() if sys.argv[1]=='static' else unit())
