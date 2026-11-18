"""Independently verify the exact comparator test set, current classfiles and recorded oracles."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import re
import runpy

HERE=Path(__file__).resolve()
P=runpy.run_path(str(HERE.with_name('5229_p020_definition_144_independent.py')))
R=P['R']
E=P['E']
read,save,ref=(P[n] for n in ('read','save','ref'))
UNIT=E/'PG39904-p020-approved-login-title148-v1'
STATIC=E/'PG39908-p020-approved-login-title-static-v1'
OLD_UNIT=E/'PG39830-p020-definition-green144-v3'
BASE=E/'PG39834-p020-definition-independent-v1'
OUT=E/'PG39910-p020-login-title-independent-v1'
PKG='dev/codex/schubert/characterization/'
NAME='dev.codex.schubert.characterization.ArtifactComparatorTest'
TEST_IDS={
 'PT-CHR-DEF017':'requiresLoginTitleObservationEvenWhenAnotherCaseUsesBrandDifference',
 'PT-CHR-DEF018':'rejectsLoginTitleObservationAtAnotherPointer',
 'PT-CHR-DEF019':'rejectsCurrentLoginTitleOutsideTheApprovedPair',
 'PT-CHR-DEF020':'rejectsNkLoginTitleOutsideTheApprovedPair',
}


def check_rules(analysis):
    reports=analysis['reports']
    for section in reports.values():
        assert ref(Path(section['raw']['path']))==section['raw']
    assert reports['checkstyle']['hasAllInputRows'] and reports['checkstyle']['findings']==0
    spotbugs=reports['spotbugs']
    assert spotbugs['exactPhysical'] and spotbugs['physical']==17
    assert all(spotbugs[k]==0 for k in ('findings','errors','missingClasses'))
    assert analysis['stageExits']==dict(spotbugs=0,format=0,checkstyle=0,pmd=4)
    old_reviews=read(BASE/'pmd-per-site.json')
    known={(Path(item['source']['path']).name,item['anchor'],item['rule'],item['message']):item['reason']
           for item in old_reviews if Path(item['source']['path']).name in ('ArtifactComparator.java','ArtifactComparatorTest.java')}
    assert len(known)==6
    root=ET.parse(STATIC/'pmd.xml').getroot()
    n=root.tag.partition('}')[0]+'}'
    findings=[]
    for parent in root.findall(n+'file'):
        source=Path(parent.get('name'))
        docs=source.read_text().splitlines()
        for site in parent.findall(n+'violation'):
            line=int(site.get('beginline'))
            key=(source.name,docs[line-1].strip(),site.get('rule'),(site.text or '').strip())
            reason=known.get(key)
            assert reason and key[2]=='UseConcurrentHashMap'
            findings.append(dict(owner=source.name,line=line,anchor=key[1],rule=key[2],message=key[3],
                                 source=ref(source),disposition='NOT_APPLICABLE',reason=reason))
    assert len(findings)==reports['pmd']['findings']==6
    return findings


def main():
    unit=read(UNIT/'manifest.json')
    begin=read(UNIT/'begin.json')
    analysis=read(STATIC/'manifest.json')
    old=read(OLD_UNIT/'manifest.json')
    assert unit['source']==begin['source']==analysis['source']
    assert unit['source']==R['git']('rev-parse','HEAD').decode().strip()
    assert unit['actualBackendActions']==0 and analysis['allPhysicalUnchanged']
    assert len(unit['stages'])==6 and all(row['actualExit']==0 for row in unit['stages'].values())
    assert len(unit['mainPhysical'])==len(old['mainPhysical'])==17
    assert unit['mainPhysical'].keys()==old['mainPhysical'].keys()
    assert {p for p,sha in unit['mainPhysical'].items() if old['mainPhysical'][p]!=sha}=={
      PKG+'ArtifactComparator.class',PKG+'ArtifactComparator$ComparisonResult.class'}
    actual=P['all_cases'](UNIT)
    expected=P['all_cases'](OLD_UNIT)
    assert len(expected)==144 and set(expected.values())=={'PASS'}
    new={(NAME,method+'()') for method in TEST_IDS.values()}
    assert not new & expected.keys() and actual==dict(expected,**{}) | dict.fromkeys(new,'PASS')
    assert len(actual)==148 and len({group for group,_ in actual})==20
    assert b'[       148 tests started         ]' in (UNIT/'unit.log').read_bytes()
    assert b'[         0 tests aborted         ]' in (UNIT/'unit.log').read_bytes()
    scope=Path(unit['classesDir'])
    assert R['physical'](scope)==unit['mainPhysical']
    originals=(UNIT/'execinfo.log').read_text()
    assert originals.count('Session "')==1 and unit['session'] in originals
    init=Path(unit['initLog']['path'])
    assert ref(init)==unit['initLog']
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",init.read_bytes())
    assert not R['git']('diff','--name-only','843de94',unit['source'],'--',str(R['B']/'baseline/current'))
    ss, = R['git']('-c','core.quotePath=false','ls-files','documents/300_SS/350_運用・品質/355_*').decode().splitlines()
    c=R['git']('show','origin/main:'+ss).decode()
    baseline=read(R['B']/'baseline/current/artifacts/CHR-A01.json')
    original_title='schubert - ログイン'
    expected_title='schubert NK - ログイン'
    assert baseline['title']==original_title and expected_title in c
    assert 'QA-045/UIC-005/SSC-074' in c and 'JSON Pointer' in c
    lines=check_rules(analysis)
    OUT.mkdir()
    base=read(next(E.glob('PG37324*/manifest.json')))
    raw=P['unfiltered'](unit,UNIT,scope,OUT,base)
    assert raw['missedMethods']==read(BASE/'manifest.json')['raw']['missedMethods']
    assert {r['className'] for r in raw['missedMethods']}=={PKG+'GateCli'}
    per=Counter()
    for record in (OUT/'raw.tsv').read_text().splitlines():
        fields=record.split('\t')
        if fields[0]!='CLASS' or not fields[1].startswith(PKG+'ArtifactComparator'):
            continue
        assert fields[3]=='true'
        for name,miss,hit in (item.split(':') for item in fields[6:]):
            assert int(miss)==0
            per[name]+=int(hit)
    assert per['CLASS']==2 and per['BRANCH']>0
    saved=OUT/'pmd-per-site.json'
    save(saved,lines)
    gz=OUT/'class-init.log.gz'
    gz.write_bytes(gzip.compress(init.read_bytes(),mtime=0))
    manifest=dict(actualExit=0,source=unit['source'],run=unit['run'],unit=ref(UNIT/'manifest.json'),
        static=ref(STATIC/'manifest.json'),originalTests=144,newDefinitions=4,tests=148,suites=20,
        firstSuccess=148,failed=0,errors=0,skipped=0,notRun=0,
        approvedOracle=dict(current=original_title,nk=expected_title,dif='DIF-001',caseId='CHR-A01',
                            jsonPointer='/title',canonicalOriginMainSS=ss),
        testIds=TEST_IDS,raw=raw,fullCounterForTwoComparatorPhysical=dict(per),
        pmdRaw=6,pmdNotApplicable=6,pmdApplicable=0,pmdUnclassified=0,pmdReviews=ref(saved),
        originalBaselineUnchanged=True,oldCoverageTransferred=False,
        priorOpenNormalPreflightDeficitRemains='BUG-3311',
        resolvedBug='BUG-3314',horizontalOpen='YKT-2699',
        keyOrExternalOrNativeActions=0,actualNkChr=False,newAcceptance=0,productTests=0,
        whole451Accepted=False,formalUpdated=False,classInit=ref(gz),
        terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(OUT/'manifest.json',manifest)
    print(ref(OUT/'manifest.json'),dict(per),raw['rawTotals'])


if __name__=='__main__':
    main()
