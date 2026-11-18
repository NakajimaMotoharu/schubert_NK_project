"""Bind the S02 field and fallback to the exact independent comparator evidence."""
from collections import Counter
from pathlib import Path
import gzip
import re
import runpy

HERE=Path(__file__).resolve()
S=runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
C,P,R,E=(S[n] for n in ('C','P','R','E'))
read,save,ref=(S[n] for n in ('read','save','ref'))
BASE=E/'PG39990-p020-search-empty170-v1'
OLD=E/'PG39994-p020-search-empty-independent-v1'
UNIT=E/'PG40014-p020-game-onchange176-v1'
STATIC=E/'PG40016-p020-game-onchange-static-v1'
OUT=E/'PG40018-p020-game-onchange-independent-v1'
TEST_IDS={
    'PT-CHR-DEF043':'acceptsAnAbsentInlineAttributeWithTheDisabledScriptSubmitButton',
    'PT-CHR-DEF044':'rejectsAMissingGameChangeFieldInsteadOfAnObservedAbsentAttribute',
    'PT-CHR-DEF045':'refusesASelfReportedNewInlineChangeHandler',
    'PT-CHR-DEF046':'refusesTheGameChangeClaimAtAnotherField',
    'PT-CHR-DEF047':'rejectsTheAbsentFallbackButtonEvenIfBothArtifactsAgree',
    'PT-CHR-DEF048':'requiresAnExplicitGameChangeClaim',
}


def main():
    old,unit,analysis=(read(x/'manifest.json') for x in (OLD,UNIT,STATIC))
    assert unit['source']==analysis['source']==read(UNIT/'begin.json')['source']
    assert len(unit['stages'])==6 and all(x['actualExit']==0 for x in unit['stages'].values())
    assert not unit['actualBackendActions'] and analysis['allPhysicalUnchanged']
    before=P['all_cases'](BASE)
    cases=P['all_cases'](UNIT)
    new={(C['NAME'],method+'()') for method in TEST_IDS.values()}
    assert len(before)==170 and not new & before.keys()
    assert cases==before | dict.fromkeys(new,'PASS') and set(cases.values())=={'PASS'}
    assert len(cases)==176 and len({suite for suite,_ in cases})==20
    assert not R['git']('diff','--name-only','843de94',unit['source'],'--',str(R['B']/'baseline/current'))
    baseline=R['B']/'baseline/current/artifacts/CHR-S02.json'
    original=read(baseline)
    assert original['gameOnchange']=='this.form.submit()' and original['javascriptDisabledSubmitButton'] is True
    design=R['git']('show','origin/main:'+S['UI']).decode()
    assert any('DIF-013' in line and 'Inline onchange' in line and '無効時button' in line for line in design.splitlines())
    scope=Path(unit['classesDir'])
    assert R['physical'](scope)==unit['mainPhysical'] and len(unit['mainPhysical'])==17
    init=Path(unit['initLog']['path'])
    assert ref(init)==unit['initLog']
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",init.read_bytes())
    session=(UNIT/'execinfo.log').read_text()
    assert session.count('Session "')==1 and unit['session'] in session
    pmd=S['decisions'](old,analysis,STATIC)
    assert len(pmd)==6 and all(x['disposition']=='NOT_APPLICABLE' for x in pmd)
    OUT.mkdir()
    engine=read(next(E.glob('PG37324*/manifest.json')))
    raw=P['unfiltered'](unit,UNIT,scope,OUT,engine)
    assert raw['missedMethods']==old['raw']['missedMethods']
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
    gz.write_bytes(gzip.compress(init.read_bytes(),mtime=0))
    report=dict(actualExit=0,source=unit['source'],unit=ref(UNIT/'manifest.json'),static=ref(STATIC/'manifest.json'),
        tests=176,suites=20,originalTests=170,newDefinitions=6,firstSuccess=176,failed=0,errors=0,skipped=0,notRun=0,
        oracle=dict(caseId='CHR-S02',pointer='/gameOnchange',current='this.form.submit()',nk=None,
                    disabledScriptFallbackBoth=True,baseline=ref(baseline),design=S['UI']),
        testIds=TEST_IDS,comparatorCounters=dict(per),raw=raw,originalBaselineUnchanged=True,oldCoverageTransferred=False,
        pmdReviews=ref(review),pmdRaw=6,pmdApplicable=0,pmdUnclassified=0,actualNkChr=False,classInit=ref(gz),
        remainingRuntimePreflight='BUG-3311',horizontalOpen='YKT-2699',productTests=0,newAcceptance=0,formalUpdated=False,
        whole451Accepted=False,terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(OUT/'manifest.json',report)
    print(ref(OUT/'manifest.json'),dict(per))


if __name__=='__main__':
    main()
