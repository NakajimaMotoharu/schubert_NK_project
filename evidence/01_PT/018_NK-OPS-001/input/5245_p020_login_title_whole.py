"""Verify the offline comparison module on one frozen source with the exact whole-suite roster."""
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve()
R=runpy.run_path(str(HERE.with_name('5227_p020_definition_uniqueness_run.py')))
ROOT,E,B,JDK,TC=(R[n] for n in ('ROOT','E','B','JDK','TC'))
git,read,ref,save,step,physical=(R[n] for n in ('git','read','ref','save','step','physical'))
PREVIOUS=E/'PG39830-p020-definition-green144-v3'
DOC=Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
PHASES = {
    'PG39904-p020-approved-login-title148-v1': ('530_P020*', PREVIOUS, 144, 148),
    'PG39906-p020-approved-login-title148-v2': ('530_P020*', PREVIOUS, 144, 148),
    'PG39922-p020-approved-all-brand153-v1': (
        '534_P020*', E/'PG39904-p020-approved-login-title148-v1', 148, 153),
    'PG39923-p020-approved-all-brand153-v2': (
        '534_P020*', E/'PG39904-p020-approved-login-title148-v1', 148, 153),
    'PG39944-p020-cache-and-session161-v1': (
        '538_P020*', E/'PG39923-p020-approved-all-brand153-v2', 153, 161),
    'PG39946-p020-cache-and-session161-v2': (
        '538_P020*', E/'PG39923-p020-approved-all-brand153-v2', 153, 161),
    'PG39964-p020-invalid-range165-v1': (
        '540_P020*', E/'PG39944-p020-cache-and-session161-v1', 161, 165),
    'PG39965-p020-invalid-range165-v2': (
        '540_P020*', E/'PG39944-p020-cache-and-session161-v1', 161, 165),
    'PG39990-p020-search-empty170-v1': (
        '549_P020*', E/'PG39965-p020-invalid-range165-v2', 165, 170),
    'PG40014-p020-game-onchange176-v1': (
        '555_P020*', E/'PG39990-p020-search-empty170-v1', 170, 176),
    'PG40034-p020-l01-required-actions-v1': (
        '561_P020*', E/'PG40014-p020-game-onchange176-v1', 176, 182),
    'PG40035-p020-l01-required-actions-v2': (
        '561_P020*', E/'PG40014-p020-game-onchange176-v1', 176, 182),
    'PG40056-p020-error-disclosure187-v1': (
        '572_P020*', E/'PG40035-p020-l01-required-actions-v2', 182, 187),
    'PG40057-p020-error-disclosure187-v2': (
        '572_P020*', E/'PG40035-p020-l01-required-actions-v2', 182, 187),
    'PG40074-p020-o01-restart192-v1': (
        '582_P020*', E/'PG40057-p020-error-disclosure187-v2', 187, 192),
    'PG40075-p020-o01-restart192-v2': (
        '582_P020*', E/'PG40057-p020-error-disclosure187-v2', 187, 192),
    'PG40088-p020-s08-voice198-v1': (
        '592_P020*', E/'PG40075-p020-o01-restart192-v2', 192, 198),
    'PG40089-p020-s08-voice198-v2': (
        '592_P020*', E/'PG40075-p020-o01-restart192-v2', 192, 198),
    'PG40104-p020-u01-menu204-v1': (
        '605_P020*', E/'PG40089-p020-s08-voice198-v2', 198, 204),
    'PG40105-p020-u01-menu204-v2': (
        '605_P020*', E/'PG40089-p020-s08-voice198-v2', 198, 204),
    'PG40107-p020-u01-menu204-v3': (
        '605_P020*', E/'PG40089-p020-s08-voice198-v2', 198, 204),
    'PG40122-p020-path-contract-red206-v1': (
        '615_P020*', E/'PG40107-p020-u01-menu204-v3', 204, 206),
    'PG40124-p020-path-contract-green206-v1': (
        '615_P020*', E/'PG40107-p020-u01-menu204-v3', 204, 206),
    'PG40128-p020-path-contract-green206-v2': (
        '615_P020*', E/'PG40107-p020-u01-menu204-v3', 204, 206),
    'PG40206-p020-a02-session-census-red208-v1': (
        '671_P020*', E/'PG40128-p020-path-contract-green206-v2', 206, 2),
    'PG40208-p020-a02-session-census-green208-v1': (
        '671_P020*', E/'PG40128-p020-path-contract-green206-v2', 206, 208),
}
TEST_PACKAGE='dev.codex.schubert.characterization.'
JAVA_DIR=Path(TEST_PACKAGE.rstrip('.').replace('.','/'))
CHANGES={str(B/where/JAVA_DIR/file) for where,file in (
    ('src/main/java','ArtifactComparator.java'),('tests/java','ArtifactComparatorTest.java'))}
L01_CHANGES=CHANGES | {str(B/where/JAVA_DIR/file) for where,file in (
    ('src/main/java','CorrelatedLogEvidenceValidator.java'),
    ('tests/java','CorrelatedMenuActionContractTest.java'))}


def frozen_source(snapshot, source, old_begin, plan, changed_paths):
    base=plan['values']['characterizationBase']
    assert base==old_begin['source']
    delta=set(git('diff','--name-only',base,source,'--',str(B)).decode().splitlines())
    assert delta==changed_paths
    assert not git('diff','--name-only','HEAD','--',str(B))
    hashes={}
    for name,old_hash in old_begin['inputHashes'].items():
        data=git('show',f'{source}:{name}')
        f=snapshot/name
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(data)
        current=ref(f)['sha256']
        assert (current!=old_hash)==(name in delta)
        hashes[name]=current
    assert len([p for p in hashes if p.startswith(str(B/'baseline/current')+'/')])==27
    assert len([p for p in hashes if p.startswith(str(B/'src/main/java')+'/')])==6
    return hashes


def main(name):
    pattern,previous_run,previous_count,expected=PHASES[name]
    plan=read(next(DOC.glob(pattern)))
    assert all(ref(Path(x['path']))==x for x in plan['values']['oracleReferences'])
    old=read(previous_run/'manifest.json')
    previous=read(previous_run/'begin.json')
    assert old['expected']==previous['expected']==previous_count
    assert old['stages']['unit']['actualExit']==0
    sdk={label:Path(pin['path']) for label,pin in previous['tools'].items()}
    assert all(ref(p)==previous['tools'][n] for n,p in sdk.items())
    assert ref(JDK/'java')==previous['jdk']
    assert ref(JDK/'javac')==previous.get('javaC',read(PREVIOUS/'begin.json')['javaC'])
    selection=previous['exactScope']
    assert len(selection)==20 and len(set(selection))==20
    source=git('rev-parse','HEAD').decode().strip()
    out=E/name
    owned=ROOT.parent/'pgpt-runs/PG379'/name.lower()
    out.mkdir()
    owned.mkdir(mode=0o700)
    snapshot=owned/'snapshot'
    a02_red = 'a02-session-census-red' in name
    if a02_red:
        changed_paths = {str(B/'tests/java'/JAVA_DIR/'ArtifactComparatorTest.java')}
    elif 'path-contract-' in name:
        changed_paths = {str(B / 'tests/java' / JAVA_DIR / file)
                         for file in ('ArtifactComparatorTest.java', 'GateContractValidatorNegativeTest.java')}
        if '-green' in name:
            changed_paths |= {str(B / 'src/main/java' / JAVA_DIR / file)
                              for file in ('ArtifactComparator.java', 'GateContractValidator.java')}
    else:
        changed_paths = L01_CHANGES if 'l01-required-actions' in name else CHANGES
    inputs=frozen_source(snapshot,source,previous,plan,changed_paths)
    tests=owned/'testclasses'
    temp=owned/'tmp'
    xml=out/'xml'
    for path in (tests,temp,xml):
        path.mkdir(mode=0o700)
    main_classes=snapshot/B/'target/classes'
    session=name.split('-')[0]+'-FIXED-OBSERVATIONS-'+str(expected)
    cp=':'.join(str(p) for label,p in sdk.items() if 'jacoco' not in label)
    mv=[str(R['MAVEN']),'-o','-B','-ntp','-N',f'-Dmaven.repo.local={TC}/m2/repository',
        '-f',str(snapshot/B/'pom.xml'),'compile']
    test=[str(JDK/'javac'),'-Xlint:all','-Werror','--release','25','-cp',f'{main_classes}:{cp}',
          '-sourcepath',str(snapshot/B/'tests/java'),'-d',str(tests),
          *(str(snapshot/B/'tests/java'/JAVA_DIR/(n+'.java')) for n in selection)]
    exec_file=out.resolve()/'jacoco.exec'
    agent=sdk['org.jacoco.agent-0.8.15-runtime.jar']
    init=owned/'class-init.log'
    selectors = [("--select-class", TEST_PACKAGE+n) for n in selection]
    if a02_red:
        selectors = [("--select-method", TEST_PACKAGE+'ArtifactComparatorTest#'+method)
                     for method in ('rejectsContradictoryActivityOfTheNewestSessionInBothReports',
                                    'rejectsActivityReportsThatOmitBothNewerSessions')]
    unit=[str(JDK/'java'),'-Xmx1g','-Djava.awt.headless=true','-Duser.language=ja','-Duser.country=JP',
          '-Duser.timezone=Asia/Tokyo','-Dchr.unitProjectRoot='+str(snapshot),'-Djava.io.tmpdir='+str(temp),
          '-Xlog:class+init=info:file='+str(init),f'-javaagent:{agent}=destfile={exec_file},sessionid={session},append=false',
          '-jar',str(sdk['junit-platform-console-standalone-1.13.4.jar']),'execute',
          '--disable-banner','--details=summary','--fail-if-no-tests','--class-path',
          f'{main_classes}:{tests}:{snapshot/B/"tests/resources"}:{cp}','--reports-dir',str(xml.resolve()),
          *(piece for pair in selectors for piece in pair),
          '--config=junit.jupiter.execution.parallel.enabled=false']
    save(out/'begin.json',dict(groupStart=plan['eventId'],source=source,snapshot=str(snapshot),expected=expected,
        exactScope=selection,selectors=selectors,sourceInputsUnchangedOutside=sorted(changed_paths),inputHashes=inputs,session=session,
        tools=previous['tools'],jdk=previous['jdk'],javaC=ref(JDK/'javac'),original=ref(previous_run/'manifest.json'),backendActions=0,
        startedAtUTC=R['utc']()))
    stages={}
    for label,cmd in (('main',mv),('test',test),('unit',unit)):
        stages[label]=step(label,cmd,owned,out,180)
        if stages[label]['actualExit']:
            break
    if stages.get('unit',{}).get('actualExit')==0:
        cli=[str(JDK/'java'),'-jar',str(sdk['org.jacoco.cli-0.8.15-nodeps.jar'])]
        commands={
          'coverage':[*cli,'report',str(exec_file),'--classfiles',str(main_classes),'--xml',str(out.resolve()/'coverage.xml')],
          'execinfo':[*cli,'execinfo',str(exec_file)],
          'classinfo':[*cli,'classinfo',str(main_classes)],
        }
        for label,cmd in commands.items():
            stages[label]=step(label,cmd,owned,out)
    assert all(ref(snapshot/name)['sha256']==h for name,h in inputs.items())
    value=dict(source=source,expected=expected,run=name,session=session,classesDir=str(main_classes),
        testsDir=str(tests),inputHashes=inputs,mainPhysical=physical(main_classes),testPhysical=physical(tests),
        initLog=ref(init) if init.is_file() else None,stages=stages,newAcceptance=0,official=False,
        sourceInputsUnchanged=True,actualBackendActions=0,terminalAtUTC=R['utc'](),
        xmlHashes={p.name:ref(p)['sha256'] for p in sorted(xml.glob('*.xml'))},verifier=ref(HERE))
    save(out/'manifest.json',value)
    print({k:a['actualExit'] for k,a in stages.items()},ref(out/'manifest.json'))
    return next((a['actualExit'] for a in stages.values() if a['actualExit']),0)


if __name__=='__main__':
    raise SystemExit(main(sys.argv[1]))
