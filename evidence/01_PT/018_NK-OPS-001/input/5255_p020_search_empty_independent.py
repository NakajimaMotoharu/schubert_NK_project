"""Independently verify the S04 comparator oracle, exact test roster and raw results."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
C = runpy.run_path(str(HERE.with_name('5247_p020_login_title_independent.py')))
P, R, E = C['P'], C['R'], C['E']
read, save, ref = (C[k] for k in ('read','save','ref'))
BASE = E/'PG39965-p020-invalid-range165-v2'
OLD = E/'PG39970-p020-invalid-range-independent-v1'
UNIT = E/'PG39990-p020-search-empty170-v1'
STATIC = E/'PG39992-p020-search-empty-static-v1'
OUT = E/'PG39994-p020-search-empty-independent-v1'
UI = 'documents/200_UI/260_引継ぎ・監査/264_現行互換性Characterization Test仕様.md'
PKG = 'dev/codex/schubert/characterization/'
TEST_IDS = {
    'PT-CHR-DEF038':'acceptsTheExactEmptySearchMessageAtItsVisibleField',
    'PT-CHR-DEF039':'requiresAnExplicitEmptySearchObservation',
    'PT-CHR-DEF040':'rejectsASelfReportedDifferentNkEmptySearchLabel',
    'PT-CHR-DEF041':'rejectsAnEmptySearchClaimOnAnUnrelatedField',
    'PT-CHR-DEF042':'doesNotTreatAnL01ClaimAsTheRequiredS04Observation',
}


def decisions(old, analysis):
    reports = analysis['reports']
    assert reports['checkstyle']['findings'] == 0 and reports['checkstyle']['hasAllInputRows']
    sb = reports['spotbugs']
    assert sb['physical'] == 17 and sb['exactPhysical'] and all(sb[k]==0 for k in ('findings','errors','missingClasses'))
    assert analysis['stageExits'] == dict(spotbugs=0,format=0,checkstyle=0,pmd=4)
    for report in reports.values():
        assert ref(Path(report['raw']['path'])) == report['raw']
    historic = read(Path(old['pmdReviews']['path']))
    known={(p['owner'],p['rule'],p['anchor'],p['message']):p['reason'] for p in historic}
    root = ET.parse(STATIC/'pmd.xml')
    observed=[]
    for group in root.findall('{*}file'):
        path=Path(group.get('name'))
        lines=path.read_text().splitlines()
        for v in group.findall('{*}violation'):
            line=int(v.get('beginline'))
            key=(path.name,v.get('rule'),lines[line-1].strip(),(v.text or '').strip())
            observed.append(dict(owner=key[0],rule=key[1],anchor=key[2],message=key[3],line=line,
                                 disposition='NOT_APPLICABLE' if key in known else 'UNCLASSIFIED',
                                 reason=known.get(key),file=ref(path)))
    assert len(observed) == reports['pmd']['findings']
    return observed


def main():
    unit=read(UNIT/'manifest.json')
    begin=read(UNIT/'begin.json')
    old=read(OLD/'manifest.json')
    analysis=read(STATIC/'manifest.json')
    assert unit['source']==begin['source']==analysis['source']
    assert all(stage['actualExit']==0 for stage in unit['stages'].values()) and len(unit['stages'])==6
    assert unit['actualBackendActions']==0 and analysis['allPhysicalUnchanged']
    before=P['all_cases'](BASE)
    actual=P['all_cases'](UNIT)
    new={(C['NAME'],method+'()') for method in TEST_IDS.values()}
    assert len(before)==165 and not new & before.keys()
    assert actual==before | dict.fromkeys(new,'PASS') and set(actual.values())=={'PASS'}
    assert len(actual)==170 and len({suite for suite,_ in actual})==20
    scope=Path(unit['classesDir'])
    assert R['physical'](scope)==unit['mainPhysical'] and len(unit['mainPhysical'])==17
    initial=Path(unit['initLog']['path'])
    assert ref(initial)==unit['initLog']
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",initial.read_bytes())
    session=(UNIT/'execinfo.log').read_text()
    assert session.count('Session "')==1 and unit['session'] in session
    assert not R['git']('diff','--name-only','843de94',unit['source'],'--',str(R['B']/'baseline/current'))
    immutable=Path(R['B']/'baseline/current/artifacts/CHR-S04.json')
    s04 = read(immutable)
    ui = R['git']('show','origin/main:'+UI)
    exact = '該当するデータはありません'
    assert s04['emptyVisibleText']=='' and s04['resultCount']==s04['paginationCount']==0
    assert any(b'DIF-008' in row and exact.encode() in row for row in ui.splitlines())
    l01 = read(R['B']/'baseline/current/artifacts/CHR-L01.json')
    assert 'emptyVisibleText' not in l01 and l01['displayedRows']==2
    reviewed=decisions(old,analysis)
    assert {row['disposition'] for row in reviewed} == {'NOT_APPLICABLE'} and len(reviewed)==6
    OUT.mkdir()
    engine=read(next(E.glob('PG37324*/manifest.json')))
    raw=P['unfiltered'](unit,UNIT,scope,OUT,engine)
    assert raw['missedMethods'] == old['raw']['missedMethods']
    per=Counter()
    for line in (OUT/'raw.tsv').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]!='CLASS' or not fields[1].startswith(PKG+'ArtifactComparator'):
            continue
        assert fields[3]=='true'
        for name,miss,hit in (part.split(':') for part in fields[6:]):
            assert int(miss)==0
            per[name]+=int(hit)
    assert per['CLASS']==2 and per['BRANCH']>0
    pmd = OUT/'pmd-per-site.json'
    save(pmd,reviewed)
    init = OUT/'class-init.log.gz'
    init.write_bytes(gzip.compress(initial.read_bytes(),mtime=0))
    result=dict(actualExit=0, source=unit['source'], unit=ref(UNIT/'manifest.json'), static=ref(STATIC/'manifest.json'),
         run=unit['run'], firstSuccess=170, tests=170, suites=20, originalTests=165, newDefinitions=5,
         failed=0, errors=0, skipped=0, notRun=0, testIds=TEST_IDS,
         independentOracle=dict(current='',nk=exact,caseId='CHR-S04',pointer='/emptyVisibleText',
                                currentRef=ref(immutable),design=UI,logProjectionPending=True),
         raw=raw, comparatorCounters=dict(per), pmdRaw=6,pmdApplicable=0,pmdUnclassified=0,pmdReviews=ref(pmd),
         originalBaselineUnchanged=True, oldCoverageTransferred=False, actualNkChr=False,
         classInit=ref(init), productTests=0, remainingRuntimePreflight='BUG-3311', horizontalOpen='YKT-2699',
         whole451Accepted=False, formalUpdated=False, newAcceptance=0, terminalAtUTC=R['utc'](), verifier=ref(HERE))
    save(OUT/'manifest.json',result)
    print(ref(OUT/'manifest.json'),dict(per),raw['rawTotals'])


if __name__=='__main__':
    main()
