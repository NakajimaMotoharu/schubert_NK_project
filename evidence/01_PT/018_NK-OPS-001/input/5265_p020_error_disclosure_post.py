"""Verify the E01 comparison's non-disclosure assumptions and exact unit result."""
from collections import Counter
from pathlib import Path
import gzip
import re
import runpy

HERE=Path(__file__).resolve()
S=runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
C,P,R,E=(S[n] for n in ('C','P','R','E'))
read,save,ref=(S[n] for n in ('read','save','ref'))
PREVIOUS=E/'PG40035-p020-l01-required-actions-v2'
PREVIOUS_POST=E/'PG40038-p020-l01-required-actions-independent-v1'
STATIC_HISTORY=E/'PG40018-p020-game-onchange-independent-v1'
FIRST=E/'PG40056-p020-error-disclosure187-v1'
FIRST_STATIC=E/'PG40058-p020-error-disclosure-static-v1'
UNIT=E/'PG40057-p020-error-disclosure187-v2'
STATIC=E/'PG40059-p020-error-disclosure-static-v2'
OUT=E/'PG40060-p020-error-disclosure-independent-v1'
FLAGS=['secretLeak','absolutePathLeak','exceptionClassLeak']
TEST_IDS={
    'PT-CHR-DEF055':'acceptsTheCommonErrorPresentationWithThreeExplicitFalseLeakFlags',
    'PT-CHR-DEF056':'rejectsEveryPositiveLeakOnEachSide',
    'PT-CHR-DEF057':'rejectsAnIdenticalPositiveLeakEvenWithoutAChangedField',
    'PT-CHR-DEF058':'rejectsMissingNullAndTextualLeakFlags',
    'PT-CHR-DEF059':'rejectsAnErrorStyleClaimThatTriesToCoverAChangedLeakFlag',
}


def main():
    prior,unit,analysis=(read(d/'manifest.json') for d in (PREVIOUS_POST,UNIT,STATIC))
    initial,first_static=(read(d/'manifest.json') for d in (FIRST,FIRST_STATIC))
    assert initial['source']!=unit['source'] and first_static['source']==initial['source']
    assert (first_static['reports']['pmd']['findings'],first_static['stageExits']['pmd'])==(7,4)
    assert all(row['actualExit']==0 for row in initial['stages'].values())
    assert unit['mainPhysical']==initial['mainPhysical'] and analysis['priorExactMainTyped']['actualArchivedExit']==0
    assert unit['source']==analysis['source']==read(UNIT/'begin.json')['source']
    assert len(unit['stages'])==6 and all(row['actualExit']==0 for row in unit['stages'].values())
    assert unit['actualBackendActions']==0 and analysis['allPhysicalUnchanged']
    assert not R['git']('diff','--name-only','843de94',unit['source'],'--',str(R['B']/'baseline/current'))
    baseline=R['B']/'baseline/current/artifacts/CHR-E01.json'
    legacy=read(baseline)
    assert all(legacy[field] is False for field in FLAGS)
    ui=R['git']('show','origin/main:'+S['UI']).decode()
    assert any('CHR-E01' in line and '秘密/path/exception非表示' in line for line in ui.splitlines())
    before=P['all_cases'](PREVIOUS)
    cases=P['all_cases'](UNIT)
    new={(C['NAME'],method+'()') for method in TEST_IDS.values()}
    assert len(before)==182 and not new & before.keys()
    assert cases==P['all_cases'](FIRST)==before | dict.fromkeys(new,'PASS')
    assert set(cases.values())=={'PASS'}
    assert len(cases)==187 and len({group for group,_ in cases})==20
    scope=Path(unit['classesDir'])
    assert R['physical'](scope)==unit['mainPhysical'] and len(unit['mainPhysical'])==17
    init=Path(unit['initLog']['path'])
    assert ref(init)==unit['initLog']
    raw_init=init.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",raw_init)
    session=(UNIT/'execinfo.log').read_text()
    assert session.count('Session "')==1 and unit['session'] in session
    pmd=S['decisions'](read(STATIC_HISTORY/'manifest.json'),analysis,STATIC)
    assert len(pmd)==6 and all(x['disposition']=='NOT_APPLICABLE' for x in pmd)
    OUT.mkdir()
    raw=P['unfiltered'](unit,UNIT,scope,OUT,read(next(E.glob('PG37324*/manifest.json'))))
    assert raw['missedMethods']==prior['raw']['missedMethods']
    per=Counter()
    for line in (OUT/'raw.tsv').read_text().splitlines():
        row=line.split('\t')
        if row[0]=='CLASS' and row[1].startswith(S['PKG']+'ArtifactComparator'):
            assert row[3]=='true'
            for key,miss,hit in (part.split(':') for part in row[6:]):
                assert int(miss)==0
                per[key]+=int(hit)
    assert per['CLASS']==2 and per['BRANCH']>0
    review=OUT/'pmd-per-site.json'
    save(review,pmd)
    gz=OUT/'class-init.log.gz'
    gz.write_bytes(gzip.compress(raw_init,mtime=0))
    report=dict(actualExit=0,source=unit['source'],unit=ref(UNIT/'manifest.json'),static=ref(STATIC/'manifest.json'),
        firstUnit=ref(FIRST/'manifest.json'),firstStaticFailure=ref(FIRST_STATIC/'manifest.json'),
        independentOracle=dict(caseId='CHR-E01',closedFlags=dict.fromkeys(FLAGS,False),baseline=ref(baseline),design=S['UI']),
        tests=187,suites=20,originalTests=182,newDefinitions=5,firstSuccess=187,failed=0,errors=0,skipped=0,notRun=0,
        testIds=TEST_IDS,comparatorCounters=dict(per),raw=raw,pmdReviews=ref(review),pmdRaw=6,pmdApplicable=0,pmdUnclassified=0,
        actualNkChr=False,actualBackendActions=0,originalBaselineUnchanged=True,oldCoverageTransferred=False,classInit=ref(gz),
        productTests=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(OUT/'manifest.json',report)
    print(ref(OUT/'manifest.json'),dict(per))


if __name__=='__main__':
    main()
