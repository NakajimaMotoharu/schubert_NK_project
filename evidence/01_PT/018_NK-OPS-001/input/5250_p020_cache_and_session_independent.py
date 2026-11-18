"""Independently bind approved cache and session comparison fields to the exact tool outcome."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import re
import runpy

HERE=Path(__file__).resolve()
P=runpy.run_path(str(HERE.with_name('5247_p020_login_title_independent.py')))
R=P['R']
E=P['E']
read,save,ref=(P[n] for n in ('read','save','ref'))
UNIT=E/'PG39944-p020-cache-and-session161-v1'
STATIC=E/'PG39948-p020-cache-and-session-static-v1'
PREVIOUS=E/'PG39923-p020-approved-all-brand153-v2'
PREVIOUS_POST=E/'PG39928-p020-approved-all-brand-independent-v1'
OUT=E/'PG39954-p020-cache-and-session-independent-v1'
TEST_IDS={
 'PT-CHR-DEF026':'requiresCacheObservationEvenWhenTheOldHeaderWasUnchanged',
 'PT-CHR-DEF027':'rejectsCacheControlOtherThanApprovedNoStore',
 'PT-CHR-DEF028':'rejectsCacheObservationForADifferentField',
 'PT-CHR-DEF029':'rejectsStringCountEvenWhenItsCharactersMatchTheApprovedNumber',
 'PT-CHR-DEF030':'requiresOldestInvalidationEvidenceAlongsideTheCorrectCount',
 'PT-CHR-DEF031':'leavesAnAdditionalSessionLossUnregistered',
 'PT-CHR-DEF032':'rejectsAnUnapprovedConfiguredMaximum',
 'PT-CHR-DEF033':'requiresTheOldestSessionsObservedRedirect',
}


def approved_inputs(source):
    base=R['B']/'baseline/current'
    assert not R['git']('diff','--name-only','843de94', source,'--',str(base))
    cache=base/'artifacts/CHR-O01.json'
    session=base/'artifacts/CHR-A02.json'
    a02=read(session)
    assert read(cache)['cacheControl']=='no-cache, no-store, max-age=0, must-revalidate'
    assert a02['configuredMaximumSessions']==2 and a02['observedActiveSessionCount']==3
    assert a02['oldestSessionInvalidated'] is False and a02['sessionActiveOldestToNewest']==[True,True,True]
    assert a02['sessionRedirectsOldestToNewest']==['/','/','/']
    references={}
    for number,pattern,needle in (
        ('UI222','documents/200_UI/220_画面・認証/222_*',b'Cache-Control: no-store'),
        ('UI226','documents/200_UI/220_画面・認証/226_*','最大2'.encode()),
        ('UI264','documents/200_UI/260_引継ぎ・監査/264_*',b'DIF-016'),
        ('SS314','documents/300_SS/310_アプリケーション/314_*',b'/login?session-expired'),
        ('SS355','documents/300_SS/350_運用・品質/355_*',b'JSON Pointer'),
    ):
        [path]=R['git']('-c','core.quotePath=false','ls-files',pattern).decode().splitlines()
        content=R['git']('show','origin/main:'+path)
        assert needle in content
        references[number]=dict(path=path,sha256=R['hashlib'].sha256(content).hexdigest())
    return dict(design=references,artifacts=[ref(cache),ref(session)],currentAndNk={
      'CHR-O01:/cacheControl':['no-cache, no-store, max-age=0, must-revalidate','no-store'],
      'CHR-A02:/observedActiveSessionCount':[3,2],
      'CHR-A02:/oldestSessionInvalidated':[False,True],
      'CHR-A02:/sessionActiveOldestToNewest/0':[True,False],
      'CHR-A02:/sessionRedirectsOldestToNewest/0':['/','/login?session-expired'],
      },configuredMaximumSessionsEach=2)


def static_reviews(analysis):
    assert analysis['stageExits']==dict(spotbugs=0,format=0,checkstyle=0,pmd=4)
    for result in analysis['reports'].values():
        assert ref(Path(result['raw']['path']))==result['raw']
    typed=analysis['reports']['spotbugs']
    assert typed['physical']==17 and typed['exactPhysical']
    assert all(typed[key]==0 for key in ('findings','missingClasses','errors'))
    style=analysis['reports']['checkstyle']
    assert style['hasAllInputRows'] and style['findings']==style['processingErrors']==0
    previous=read(PREVIOUS_POST/'pmd-per-site.json')
    prior={(x['owner'],x['anchor'],x['rule'],x['message']):x['reason'] for x in previous}
    root=ET.parse(STATIC/'pmd.xml').getroot()
    pre=root.tag.partition('}')[0]+'}'
    assert not root.findall(pre+'error')
    reasons=[]
    for file in root.findall(pre+'file'):
        path=Path(file.get('name'))
        lines=path.read_text().splitlines()
        for rule in file.findall(pre+'violation'):
            n=int(rule.get('beginline'))
            name=rule.get('rule')
            source_line=lines[n-1].strip()
            msg=(rule.text or '').strip()
            key=(path.name,source_line,name,msg)
            assert key in prior and name=='UseConcurrentHashMap'
            reasons.append(dict(owner=path.name,line=n,rule=name,anchor=source_line,message=msg,source=ref(path),
                                disposition='NOT_APPLICABLE',reason=prior[key]))
    assert len(reasons)==len(prior)==6
    return reasons


def main():
    unit=read(UNIT/'manifest.json')
    old=read(PREVIOUS/'manifest.json')
    analysis=read(STATIC/'manifest.json')
    assert unit['source']==analysis['source']==R['git']('rev-parse','HEAD').decode().strip()
    assert len(unit['stages'])==6 and all(s['actualExit']==0 for s in unit['stages'].values())
    assert unit['actualBackendActions']==0 and analysis['allPhysicalUnchanged']
    baseline=P['P']['all_cases'](PREVIOUS)
    actual=P['P']['all_cases'](UNIT)
    new={(P['NAME'],method+'()') for method in TEST_IDS.values()}
    assert len(baseline)==153 and not new & baseline.keys()
    assert len(actual)==161 and len({name for name,_ in actual})==20
    assert actual==baseline|dict.fromkeys(new,'PASS') and set(actual.values())=={'PASS'}
    assert b'[         0 tests aborted         ]' in (UNIT/'unit.log').read_bytes()
    assert {p for p,h in unit['mainPhysical'].items() if old['mainPhysical'][p]!=h}=={
       P['PKG']+'ArtifactComparator.class',P['PKG']+'ArtifactComparator$ComparisonResult.class'}
    classes=Path(unit['classesDir'])
    assert R['physical'](classes)==unit['mainPhysical'] and len(unit['mainPhysical'])==17
    witness=Path(unit['initLog']['path'])
    assert ref(witness)==unit['initLog']
    init=witness.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",init)
    oracle=approved_inputs(unit['source'])
    sites=static_reviews(analysis)
    OUT.mkdir()
    previous=read(next(E.glob('PG37324*/manifest.json')))
    raw=P['P']['unfiltered'](unit,UNIT,classes,OUT,previous)
    assert raw['missedMethods']==read(PREVIOUS_POST/'manifest.json')['raw']['missedMethods']
    counters=Counter()
    for line in (OUT/'raw.tsv').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS' and fields[1].startswith(P['PKG']+'ArtifactComparator'):
            for label,missed,covered in (token.split(':') for token in fields[6:]):
                assert int(missed)==0
                counters[label]+=int(covered)
    assert counters['CLASS']==2 and counters['BRANCH']>0
    archive=OUT/'class-init.log.gz'
    archive.write_bytes(gzip.compress(init,mtime=0))
    report=OUT/'pmd-per-site.json'
    save(report,sites)
    result=dict(actualExit=0,source=unit['source'],run=unit['run'],unit=ref(UNIT/'manifest.json'),
       static=ref(STATIC/'manifest.json'),originalTests=153,newDefinitions=8,tests=161,suites=20,
       firstSuccess=161,failed=0,errors=0,skipped=0,notRun=0,independentOracle=oracle,testIds=TEST_IDS,
       raw=raw,comparatorCounters=dict(counters),originalBaselineUnchanged=True,oldCoverageTransferred=False,
       pmdRaw=6,pmdApplicable=0,pmdUnclassified=0,pmdReviews=ref(report),
       remainingRuntimePreflight='BUG-3311',closedLocal=['BUG-3317'],horizontalOpen='YKT-2699',
       actualNkChr=False,actualAuthenticationOrBackendActions=0,newAcceptance=0,whole451Accepted=False,
       productTests=0,formalUpdated=False,classInit=ref(archive),terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(OUT/'manifest.json',result)
    print(ref(OUT/'manifest.json'),dict(counters),raw['rawTotals'])


if __name__=='__main__':
    main()
