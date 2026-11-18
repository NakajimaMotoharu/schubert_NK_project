"""Independently bind each QA054 operation and the final L01 tool result to its exact source."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import re
import runpy

HERE=Path(__file__).resolve()
S=runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
C,P,R,E=(S[k] for k in ('C','P','R','E'))
ref,read,save=(S[k] for k in ('ref','read','save'))
BASE=E/'PG40014-p020-game-onchange176-v1'
BASE_POST=E/'PG40018-p020-game-onchange-independent-v1'
FIRST=E/'PG40034-p020-l01-required-actions-v1'
FIRST_STATIC=E/'PG40036-p020-l01-required-actions-static-v1'
UNIT=E/'PG40035-p020-l01-required-actions-v2'
STATIC=E/'PG40037-p020-l01-required-actions-static-v2'
OUT=E/'PG40038-p020-l01-required-actions-independent-v1'
PKG='dev/codex/schubert/characterization/'
TEST_IDS={
    'PT-CHR-DEF049': ('ArtifactComparatorTest','rejectsLoginOnlyEvidenceAtTheFullL01Gate'),
    'PT-CHR-DEF050': ('CorrelatedMenuActionContractTest','completeL01RequiresBothInitialOperationsAndTheirCompanionRequests'),
    'PT-CHR-DEF051': ('CorrelatedMenuActionContractTest','completeL01DoesNotAcceptBothSidesOmittingTheMenuAction'),
    'PT-CHR-DEF052': ('CorrelatedMenuActionContractTest','completeL01DoesNotAcceptBothSidesOmittingTheLogSearchAction'),
    'PT-CHR-DEF053': ('CorrelatedMenuActionContractTest','completeL01ChecksCompanionRequestCountRouteMethodAndStatus'),
    'PT-CHR-DEF054': ('CorrelatedMenuActionContractTest','completeL01MenuActionAndRequestNeedOneHttpRequestIdentity'),
}


def pmd_disposition(analysis):
    reports=analysis['reports']
    assert all(ref(Path(item['raw']['path']))==item['raw'] for item in reports.values())
    assert reports['checkstyle']['hasAllInputRows'] and reports['checkstyle']['findings']==0
    sb=reports['spotbugs']
    assert sb['physical']==17 and sb['exactPhysical'] and all(sb[k]==0 for k in ('findings','errors','missingClasses'))
    assert analysis['stageExits']==dict(spotbugs=0,format=0,checkstyle=0,pmd=4)
    assert analysis['priorExactMainTyped']['actualArchivedExit']==0
    historic=read(E/'PG39834-p020-definition-independent-v1'/'pmd-per-site.json')
    known={(Path(row['source']['path']).name,row['anchor'],row['rule'],row['message']):row['reason']
           for row in historic if row['rule']=='UseConcurrentHashMap'}
    validator_maps={
        'Map<String, JsonNode> events = new HashMap<>();':
            'Each call builds its expectation index locally and uses it only in its synchronous validation.',
        'Map<String, JsonNode> addedEvents = new HashMap<>();':
            'Each compareSide call builds and consumes its after-row index without sharing it.',
        'Map<String, JsonNode> rows = new HashMap<>();':
            'Each old/new row index remains within the current invocation, even when validations are concurrent.',
    }
    root=ET.parse(STATIC/'pmd.xml')
    results=[]
    for file in root.findall('{*}file'):
        source=Path(file.get('name'))
        lines=source.read_text().splitlines()
        for site in file.findall('{*}violation'):
            i=int(site.get('beginline'))
            rule=site.get('rule')
            msg=(site.text or '').strip()
            key=(source.name,lines[i-1].strip(),rule,msg)
            reason=known.get(key)
            if source.name=='CorrelatedLogEvidenceValidator.java':
                reason=validator_maps.get(key[1])
            assert reason and rule=='UseConcurrentHashMap'
            results.append(dict(source=ref(source),line=i,anchor=key[1],rule=rule,message=msg,
                                reason=reason,disposition='NOT_APPLICABLE'))
    assert len(results)==reports['pmd']['findings']==9
    return results


def main():
    latest=read(UNIT/'manifest.json')
    build=read(UNIT/'begin.json')
    first=read(FIRST/'manifest.json')
    initial=read(FIRST_STATIC/'manifest.json')
    static=read(STATIC/'manifest.json')
    assert latest['source']==build['source']==static['source']
    assert first['source']!=latest['source'] and first['source']==initial['source']
    assert latest['mainPhysical']==first['mainPhysical'] and len(latest['mainPhysical'])==17
    test='program/characterization/tests/java/'+PKG+'CorrelatedMenuActionContractTest.java'
    assert {k for k,sha in latest['inputHashes'].items() if sha!=first['inputHashes'][k]}=={test}
    assert initial['reports']['pmd']['findings']==13 and initial['stageExits']['spotbugs']==0
    prior=ET.parse(FIRST_STATIC/'pmd.xml')
    assert sum(v.get('rule')=='AvoidDuplicateLiterals' for v in prior.findall('.//{*}violation'))==4
    assert all(row['actualExit']==0 for unit in (latest,first) for row in unit['stages'].values())
    before=P['all_cases'](BASE)
    new={('dev.codex.schubert.characterization.'+cls,method+'()') for cls,method in TEST_IDS.values()}
    assert len(before)==176 and not new & before.keys()
    cases=P['all_cases'](UNIT)
    assert cases==P['all_cases'](FIRST)==before | dict.fromkeys(new,'PASS')
    assert set(cases.values())=={'PASS'} and len(cases)==182 and len({x[0] for x in cases})==20
    assert not R['git']('diff','--name-only','843de94',latest['source'],'--',str(R['B']/'baseline/current'))
    design_file='documents/300_SS/350_運用・品質/355_Characterization Test実行準備・PG開始gate.md'
    design=R['git']('show','origin/main:'+design_file).decode()
    assert any('MENU_VIEWED 1' in line and 'API LOG_SEARCHED 1' in line and 'REQUEST 1' in line for line in design.splitlines())
    scope=Path(latest['classesDir'])
    assert R['physical'](scope)==latest['mainPhysical']
    init=Path(latest['initLog']['path'])
    assert ref(init)==latest['initLog']
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",init.read_bytes())
    session=(UNIT/'execinfo.log').read_text()
    assert session.count('Session "')==1 and latest['session'] in session
    pmd=pmd_disposition(static)
    OUT.mkdir()
    raw=P['unfiltered'](latest,UNIT,scope,OUT,read(next(E.glob('PG37324*/manifest.json'))))
    assert raw['missedMethods']==read(BASE_POST/'manifest.json')['raw']['missedMethods']
    counters=Counter()
    targets={'ArtifactComparator','ArtifactComparator$ComparisonResult','CorrelatedLogEvidenceValidator'}
    for line in (OUT/'raw.tsv').read_text().splitlines():
        row=line.split('\t')
        if row[0]=='CLASS' and row[1].removeprefix(PKG) in targets:
            assert row[3]=='true'
            for key,miss,hit in (part.split(':') for part in row[6:]):
                assert int(miss)==0
                counters[key]+=int(hit)
    assert counters['CLASS']==3 and counters['BRANCH']>0
    review=OUT/'pmd-per-site.json'
    save(review,pmd)
    gz=OUT/'class-init.log.gz'
    gz.write_bytes(gzip.compress(init.read_bytes(),mtime=0))
    report=dict(actualExit=0,source=latest['source'],unit=ref(UNIT/'manifest.json'),static=ref(STATIC/'manifest.json'),
        firstUnit=ref(FIRST/'manifest.json'),firstStaticFailure=ref(FIRST_STATIC/'manifest.json'),
        tests=182,suites=20,originalTests=176,newDefinitions=6,firstSuccess=182,failed=0,errors=0,skipped=0,notRun=0,
        oracle=dict(activeDesign=design_file,menu='GET / 200 with separate events and same HTTP request',
                    logSearch='GET /logs 200 and API LOG_SEARCHED with same logical operation'),
        testIds=TEST_IDS,affectedPhysicalCounters=dict(counters),raw=raw,pmdRaw=9,pmdApplicable=0,pmdUnclassified=0,
        pmdReviews=ref(review),actualL01=False,originalBaselineUnchanged=True,oldCoverageTransferred=False,
        independentPreparationGuardExit1='Three validator map sites needed separate current review',
        classInit=ref(gz),productTests=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,
        terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(OUT/'manifest.json',report)
    print(ref(OUT/'manifest.json'),dict(counters))


if __name__=='__main__':
    main()
