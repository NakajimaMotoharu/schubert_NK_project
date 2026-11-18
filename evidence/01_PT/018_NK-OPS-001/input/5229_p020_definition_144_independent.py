"""Check the exact 144 tool tests, bytecode, independent coverage and project tool findings."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import re
import runpy
import subprocess

HERE=Path(__file__)
R=runpy.run_path(str(HERE.with_name('5227_p020_definition_uniqueness_run.py')))
E=R['E']
read,save,ref=R['read'],R['save'],R['ref']
TAG=R['PACKAGE']+'ArtifactComparatorTest'
MAP_RULE='UseConcurrentHashMap'
PMD_FILE_DECISIONS={
 'ArtifactComparator.java': {
   75:'Current artifacts are accumulated in a TreeMap local to one compare call; key order is stable.',
   76:'NK artifacts are accumulated in a TreeMap local to one compare call; key order is stable.',
   104:'DIF rules are first-seen and ordered in the calling thread; insertion order controls unused DIF diagnostics.',
   255:'The artifact index is built privately in each call and used after that call returns to its caller.'},
 'GateCli.java': {
   164:'Source verification builds this report in one call and serializes it before returning.',
   260:'Preflight builds this one report serially after its local checks and writes it without sharing the map.',
   311:'Current repeat comparison writes this local report after serial ordered file comparisons.',
   382:'Gate reporting builds this entry-ordered local result before serialization and does not return a mutable map.',
   553:'Promotion writes this local baseline manifest before return; the reported ordinary tests use isolated copies.',
   624:'The prefixed index is a new ordered map filled by one caller-thread iteration.',
   630:'The file hash index is accumulated in lexical order by one caller and is never shared while mutable.'},
 'ArtifactComparatorTest.java': {
   805:'A local Current observation map belongs solely to this test invocation and its own temporary directory.',
   806:'A local NK observation map belongs solely to this test invocation and its own temporary directory.'},
 'GateCliTest.java': {
   80:'Local ordered property fixture for missing project root retains a deliberate null sentinel.',
   123:'Local ordered source verification fixture uses a single test and restores all changed system properties.',
   209:'Local negative preflight property map is constructed before withProperties consumes it.',
   306:'Local gate report properties are used by the test thread only and restored after the callback.',
   598:'Local negative fixture uses a null value to model missing chr.dbUrl, consumed serially.',
   618:'Local per-port properties are populated and consumed by one test thread.',
   646:'Local fixture property map has one owner prior to use by the test thread.',
   768:'Local map saves old nullable values for deterministic serial restoration in finally.'},
}
FINITE={
 (572,'CloseResource'):'The test owns the executor; finally cancels, releases its latch and waits up to ten seconds for termination.',
 (572,'DoNotUseThreads'):'The owned finite JUnit executor implements the independent concurrent serialization test, outside any container.',
 (575,'DoNotUseThreads'):'Submitting one callable models concurrent ownership; completion is bounded by its get and finally termination.',
 (589,'DoNotUseThreads'):'The JUnit fixture stops its own executor in finally and does not own a service or container.',
 (590,'DoNotUseThreads'):'The bounded await verifies owned JUnit shutdown rather than managing any application threads.',
}


def all_cases(slot):
    terminal=read(slot/'manifest.json')
    tuples={}
    for name,h in terminal['xmlHashes'].items():
        path=slot/'xml'/name
        assert ref(path)['sha256']==h
        xml=ET.parse(path).getroot()
        for case in xml.findall('testcase'):
            k=(case.get('classname'),case.get('name'))
            assert k not in tuples
            statuses=[c.tag for c in case if c.tag in ('failure','error','skipped')]
            assert len(statuses)<2
            tuples[k]=statuses[0] if statuses else 'PASS'
    return tuples


def validate_pmd(path,static):
    assert ref(path.resolve())==static['reports']['pmd']['raw']
    root=ET.parse(path).getroot()
    n=root.tag.partition('}')[0]+'}'
    used=[]
    for node in root.findall(n+'file'):
        source=Path(node.get('name'))
        for row in node.findall(n+'violation'):
            line=int(row.get('beginline'))
            rule=row.get('rule')
            anchor=source.read_text().splitlines()[line-1].strip()
            if rule==MAP_RULE:
                reason=PMD_FILE_DECISIONS[source.name][line]
                assert 'new ' in anchor and 'Map<' in anchor
            else:
                assert source.name=='GateCliTest.java'
                reason=FINITE[line,rule]
                assert any(text in anchor for text in
                    ('Executors.newVirtualThreadPerTaskExecutor','executor.submit','executor.shutdownNow','executor.awaitTermination'))
            used.append(dict(source=ref(source),line=line,rule=rule,message=(row.text or '').strip(),
                anchor=anchor,disposition='NOT_APPLICABLE',reason=reason))
    assert len(used)==26
    return used


def unfiltered(unit,slot,current,out,previous):
    pinned=read(E/'PG31432-generated-code-supplemental-tool-v1/compile.json')
    for pin in pinned['dependencies']:
        assert ref(Path(pin['path']))['sha256']==pin['sha256']
    source=next(E.glob('PG38642*/begin.json'))
    current_tool=read(source)
    assert ref(Path(current_tool['tool']['path']))==current_tool['tool']
    qualified=read(source.with_name('manifest.json'))
    assert qualified['actualExit']==0 and qualified['optionalNonLineOutputByteExact']
    prefix=qualified['optionalCommand'][:5]
    assert prefix[3:] == ['org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement','--line-deficits']
    command=[*prefix,str(slot/'jacoco.exec'),*[str(current/p) for p in sorted(unit['mainPhysical'])]]
    result=subprocess.run(command,capture_output=True,timeout=90)
    assert result.returncode==0 and not result.stderr
    detail=out/'raw.tsv'
    detail.write_bytes(result.stdout)
    keys={p.removesuffix('.class') for p in unit['mainPhysical']}
    measures={}
    deficits=[]
    line_deficits=[]
    for line in result.stdout.decode().splitlines():
        bits=line.split('\t')
        assert bits[0] in ('CLASS','METHOD','DEFICIT')
        if bits[0]=='CLASS':
            label,crc,present=bits[1:4]
            measures[label]=(crc,present,bits[6:])
        elif bits[0]=='METHOD':
            misses=[x for x in bits[5:] if int(x.split(':')[1])]
            if misses:
                deficits.append(dict(className=bits[1],method=bits[2],descriptor=bits[3],misses=misses))
        else:
            line_deficits.append(bits[1:])
    assert set(measures)==keys
    ex=(slot/'execinfo.log').read_text()
    assert ex.count('Session "')==1 and 'Session "'+unit['session']+'"' in ex
    ids={n:(h,int(hit)) for h,hit,_,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
    totals=Counter()
    for name,(crc,present,counters) in measures.items():
        values={k:(int(m),int(h)) for k,m,h in (row.split(':') for row in counters)}
        for k,(miss,hit) in values.items():
            totals[k,'missed']+=miss
            totals[k,'covered']+=hit
        assert values['METHOD']!=(0,0) and ids[name][0]==crc and ids[name][1]>0 and present=='true' or (
            values['METHOD']==(0,0) and name not in ids and all(v==(0,0) for v in values.values()))
    new_no_code=sorted(name for name,(crc,present,raw) in measures.items() if 'METHOD:0:0' in raw)
    assert new_no_code==sorted(previous['noCodeInterfacesRetained']+[R['PACKAGE'].replace('.','/')+'GateCli$UsableSpace'])
    assert all(row['className']==R['PACKAGE'].replace('.','/')+'GateCli' for row in deficits)
    return dict(command=command,evidence=ref(detail),actualExit=result.returncode,noCode=new_no_code,tool=ref(source),lineDeficits=line_deficits,
      rawTotals={kind:{role:totals[kind,role] for role in ('missed','covered')}
                 for kind in ('LINE','METHOD','CLASS','BRANCH','INSTRUCTION')},missedMethods=deficits)


def main():
    slot=E/'PG39830-p020-definition-green144-v3'
    red=E/'PG39822-p020-definition-red-v1'
    first=E/'PG39826-p020-definition-green144-v1'
    failed_compile=E/'PG39828-p020-definition-green144-v2'
    static=E/'PG39832-p020-definition-static-v1'
    history=next(E.glob('PG37324*/manifest.json'))
    original=read(history)
    unit=read(slot/'manifest.json')
    analysis=read(static/'manifest.json')
    current=Path(unit['classesDir'])
    stage_exits={k:v['actualExit'] for k,v in unit['stages'].items()}
    assert all(x==0 for x in stage_exits.values()) and len(stage_exits)==6
    assert unit['source']==analysis['source'] and analysis['allPhysicalUnchanged']
    assert len(unit['mainPhysical'])==17 and R['physical'](current)==unit['mainPhysical']
    assert read(failed_compile/'manifest.json')['stages'].keys()=={'main'}
    assert read(failed_compile/'manifest.json')['stages']['main']['actualExit']==1
    invalid={key:outcome for key,outcome in all_cases(first).items() if outcome!='PASS'}
    assert invalid=={(R['PACKAGE']+'GateCliTest','preflightValidatesFilesPermissionsStorageNetworkAndPorts()'):'error'}
    old_expected={(x['className'],x['name']) for x in original['cases']}
    new={(TAG,n+'()') for n in R['METHODS']}
    assert len(old_expected)==142 and old_expected.isdisjoint(new)
    assert all_cases(red)==dict.fromkeys(new,'failure')
    assert all_cases(slot)==dict.fromkeys(old_expected|new,'PASS')
    assert all(v==0 for k,v in analysis['stageExits'].items() if k!='pmd') and analysis['stageExits']['pmd']==4
    assert all(analysis['reports']['spotbugs'][k]==0 for k in ('findings','errors','missingClasses'))
    assert analysis['reports']['spotbugs']['exactPhysical'] and analysis['reports']['spotbugs']['physical']==17
    assert analysis['reports']['checkstyle']['findings']==0
    reviews=validate_pmd(static/'pmd.xml',analysis)
    names={c for c in unit['testPhysical'] if 'NativeNk' in c or 'CurrentCharacterizationTest' in c}
    assert not names
    log=Path(unit['initLog']['path'])
    assert ref(log)==unit['initLog']
    init=log.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",init)
    build=read(slot/'begin.json')
    candidates=read(next(E.glob('PG37318*/manifest.json')))['sourceHashes']
    declared={p for p in unit['inputHashes'] if p.startswith('program/characterization/')}
    unchanged=set(declared)-set(map(str,R['PHASE_CHANGES']['qualified']))
    assert all(unit['inputHashes'][p]==candidates[p] for p in unchanged)
    assert {str(p) for p in R['PHASE_CHANGES']['qualified']}==declared-unchanged
    assert all(ref(Path(build['snapshot'])/p)['sha256']==key for p,key in unit['inputHashes'].items())
    capture=E/'PG39834-p020-definition-independent-v1'
    if capture.exists():
        assert not list(capture.iterdir())
    else:
        capture.mkdir()
    raw=unfiltered(unit,slot,current,capture,original)
    save(capture/'pmd-per-site.json',reviews)
    previous_src=original['toolSource']
    diffs=R['git']('diff','--name-only',previous_src,unit['source'],'--',str(R['B'])).decode().splitlines()
    assert set(diffs)==set(map(str,R['PHASE_CHANGES']['qualified']))
    assert not R['git']('diff','--name-only','843de94',unit['source'],'--','program/characterization/baseline/current')
    archives=[]
    for p in [log,*sorted(slot.glob('*.log'))]:
        dst=capture/(p.name+'.gz')
        with dst.open('xb') as f:f.write(gzip.compress(p.read_bytes(),mtime=0))
        archives.append(dict(original=ref(p),archive=ref(dst)))
    m=dict(actualExit=0,source=unit['source'],groupStart=build['groupStart'],run=unit['run'],
        tests=144,oldDefinitions=142,newDefinitions=2,failed=0,errors=0,skipped=0,notRun=0,
        raw=raw,static=ref(static/'manifest.json'),toolCoverageFull=all(n['missed']==0 for n in raw['rawTotals'].values()),
        pmdRaw=26,pmdNotApplicable=26,pmdUnclassified=0,qualitySuppressionChanges=0,
        testedChangeFiles=diffs,firstFinishedFailure=ref(first/'manifest.json'),actualRootOrBackendActions=0,
        originalDefectRed=ref(red/'manifest.json'),independentMissingUrlBuildFailure=ref(failed_compile/'manifest.json'),
        sourceBaselineUnchanged=True,actualCHR=False,whole451Accepted=False,newAcceptance=0,
        productTests=0,archives=archives,unit=ref(slot/'manifest.json'),terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(capture/'manifest.json',m)
    print(ref(capture/'manifest.json'),raw['rawTotals'],raw['missedMethods'])


if __name__=='__main__':
    main()
