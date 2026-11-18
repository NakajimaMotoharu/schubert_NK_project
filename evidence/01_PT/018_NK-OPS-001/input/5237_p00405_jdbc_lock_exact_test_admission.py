"""Admit the exact test-only styling repair by reusing current immutable Main and SpotBugs."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET
from importlib.util import module_from_spec, spec_from_file_location

HERE=Path(__file__)
spec=spec_from_file_location('jdbc_lock_original',HERE.with_name('5236_p00405_service_db_state_lock_checks.py'))
P=module_from_spec(spec)
spec.loader.exec_module(P)
FIRST=P.ASSURE
FIRST_BUILD=P.BUILD
OUT=P.E/'PG39865-service-db-state-lock-test-static-v2'
read,save,ref,git=P.read,P.save,P.ref,P.git


def current():
    build=read(FIRST_BUILD)
    work=Path(build['cwd'])
    head=git('rev-parse','HEAD').decode().strip()
    assert git('diff','--name-only',build['unitSource'],head,'--','src').decode().splitlines()==[P.CHANGED_TEST]
    old=git('show',f'{build["unitSource"]}:{P.CHANGED_TEST}')
    new=git('show',f'{head}:{P.CHANGED_TEST}')
    assert new.replace(b'  private static final int FIRST_CONNECTOR_CALL = 1;\n',b'',1).replace(
        b'calls.incrementAndGet() == FIRST_CONNECTOR_CALL',b'calls.incrementAndGet() == 1',1)==old
    for path,h in build['sourceInputs'].items():
        assert P.R['sha'](Path(path))==h
    current_classes={m:work/f'src/schubert-nk-{m}/target/classes' for m in P.B['MODS']}
    assert all(P.R['physical'](p)==build['physicalClassHashes'][m] for m,p in current_classes.items())
    return dict(build,originalUnitSource=build['unitSource'],unitSource=head),work,current_classes


def rows(path):
    root=ET.parse(path).getroot()
    ns=root.tag.partition('}')[0]+'}'
    assert not root.findall(ns+'error')
    return [(Path(f.get('name')),int(v.get('beginline')),v.get('rule'),(v.text or '').strip())
            for f in root.findall(ns+'file') for v in f.findall(ns+'violation')]


def index(pairs):
    return Counter((path.name,line,rule,message) for path,line,rule,message in pairs)


def classify(first,new,test_main):
    previous=[
      (file,line+1,rule,msg) for file,line,rule,msg in first
      if file.name==test_main and rule!='AvoidLiteralsInIfCondition']
    current=index(new)
    assert current==index(previous)
    reasons=[]
    for file,line,rule,message in new:
        text=file.read_text().splitlines()[line-1].strip()
        if rule=='DoNotUseThreads':
            assert any(word in text for word in ('executor','worker','Thread.currentThread','CountDownLatch','get('))
            reason='The synthetic JDBC test owns its worker or latch within finite waits and shutdown. It does not run inside a managed container.'
        elif rule=='CloseResource':
            if 'ExecutorService' in message:
                assert 'newVirtualThreadPerTaskExecutor' in text
                reason='A fixture-owned executor is released by the exact test finally with shutdownNow and a finite awaitTermination(5).'
            else:
                assert 'Connection' in message
                reason='The ordinary test uses a memory-only proxy; each acquired caller-owned connection has an explicit close assertion.'
        else:
            raise AssertionError((file.name,line,rule))
        reasons.append(dict(path=str(file),line=line,rule=rule,message=message,anchor=text,
                            exactReason=reason,disposition='NOT_APPLICABLE'))
    for file,line,rule,message in first:
        if file.name!=test_main:
            assert rule=='AvoidCatchingGenericException'
            text=file.read_text().splitlines()[line-1].strip()
            assert 'catch (RuntimeException | Error ' in text
            reasons.append(dict(path=str(file),line=line,rule=rule,message=message,anchor=text,
              exactReason='Exact existing JDBC precedence preserves unknown throwable identity while releasing the owned failed connection. This gives no success result.',
              disposition='NOT_APPLICABLE'))
    assert len(reasons)==25
    return reasons


def admit():
    build,work,classes=current()
    prior=read(FIRST/'manifest.json')
    assert prior['operatorExit']==0 and prior['actualExits']['pmd']==4
    assert prior['scope']['spotbugs']['exactPhysical'] and prior['scope']['spotbugs']['physical']==201
    assert not any(prior['scope']['spotbugs'][k] for k in ('findings','errors','missingClasses'))
    for k in ('checkstyle','spotbugs','pmd'):
        assert ref(Path(prior['scope'][k]['raw']['path']))==prior['scope'][k]['raw']
    fresh=work/'test-static-corrected'
    slot=OUT.resolve()
    slot.mkdir()
    fresh.mkdir(mode=0o700)
    compiled=fresh/'classes'
    compiled.mkdir()
    selectors=[P.TESTROOT+n+'.java' for n in P.SUITES]
    write_paths={}
    for name in selectors:
        f=fresh/Path(name).name
        value=git('show',f'{build["unitSource"]}:{name}')
        assert value==Path(name).read_bytes()
        f.write_bytes(value)
        write_paths[name]=str(f)
    changed=write_paths[P.CHANGED_TEST]
    listpath=slot/'sources.txt'
    listpath.write_text(changed+'\n')
    before=read(FIRST/'begin.json')['commands']
    setup={}
    for label in ('pmd','checkstyle'):
        report=(FIRST.resolve()/(label+'.xml')).as_posix()
        listing=(FIRST.resolve()/'sources.txt').as_posix()
        setup[label]=[part.replace(report,str(slot/(label+'.xml'))).replace(listing,str(listpath))
                      for part in before[label]]
    setup['formatter']=[*before['formatter'][:6],changed]
    replace={str(work/name):write_paths[name] for name in selectors}
    replace[prior['testsDir']]=str(compiled)
    setup['test-compile']=[replace.get(part,part) for part in before['test-compile']]
    save(slot/'begin.json',dict(source=build['sourceCore'],unitSource=build['unitSource'],onlyTestStyleChanged=True,
       commands=setup,original=ref(FIRST/'manifest.json'),inputs={n:ref(Path(f)) for n,f in write_paths.items()},
       heavyweightBuildOrSpotbugsReplayed=False,startedAtUTC=P.R['utc']()))
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(P.Q['run'],name,arg,slot,work) for name,arg in setup.items()]
        results=dict(j.result() for j in jobs)
    exits={n:x['actualExit'] for n,x in results.items()}
    assert exits==dict(pmd=4,checkstyle=0,formatter=0,**{'test-compile':0})
    source_map={str(Path(changed).relative_to(work)):ref(Path(changed))['sha256']}
    cs=P.Q['parse_report']('checkstyle',slot/'checkstyle.xml',work,source_map,set())
    assert cs['hasAllInputRows'] and not cs['findings']
    statuses=classify(rows(FIRST/'pmd.xml'),rows(slot/'pmd.xml'),Path(changed).name)
    assert len(statuses)==25
    manifest=dict(prior,source=build['sourceCore'],unitSource=build['unitSource'],
        actualExits=dict(exits,spotbugs=0),originalRawApplicable1=ref(FIRST/'pre-fix-applicable.json'),
        mainAndPeerSpotbugsExactReused=True,formatterAndTestCompileCurrent=True,
        separateRawPmdScopes=True,testsDir=str(compiled),testClassHashes=P.R['physical'](compiled),
        perSite=statuses,executedTests=0,terminalAtUTC=P.R['utc'](),verifier=ref(HERE))
    save(slot/'manifest.json',manifest)
    save(slot/'admission.json',dict(static=ref(OUT/'manifest.json'),applicable=0,unclassified=0,
        pmdRaw=25,carriedUnchangedMainRaw=4,testsExecuted=0,terminalAtUTC=P.R['utc']()))
    print(exits, len(statuses))


if __name__=='__main__':
    assert sys.argv[1:] in (['static'],['unit'])
    if sys.argv[1]=='static':
        admit()
    else:
        P.ASSURE=OUT
        P.current=current
        raise SystemExit(P.unit())
