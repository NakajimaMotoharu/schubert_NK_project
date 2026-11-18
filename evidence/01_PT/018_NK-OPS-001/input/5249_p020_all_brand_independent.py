"""Verify all approved brand paths and the current full offline comparator module."""
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
UNIT=E/'PG39923-p020-approved-all-brand153-v2'
STATIC=E/'PG39927-p020-approved-all-brand-static-v2'
FIRST=E/'PG39922-p020-approved-all-brand153-v1'
FIRST_STATIC=E/'PG39926-p020-approved-all-brand-static-v1'
PREVIOUS=E/'PG39904-p020-approved-login-title148-v1'
OUT=E/'PG39928-p020-approved-all-brand-independent-v1'
TEST_IDS={
 'PT-CHR-DEF021':'requiresSearchTitleEvidenceEvenWithoutAnyUnregisteredDrift',
 'PT-CHR-DEF022':'requiresMenuBrandEvidenceFromTheMenuCase',
 'PT-CHR-DEF023':'requiresBothCommonStyleTitlesWhenTheSecondOneChanged',
 'PT-CHR-DEF024':'refusesCommonStyleTitleOutsideApprovedBrandPositions',
 'PT-CHR-DEF025':'leavesNonBrandTitleChangeUnregistered',
}


def verify_style():
    analysis=read(STATIC/'manifest.json')
    first=read(FIRST_STATIC/'manifest.json')
    assert analysis['stageExits']==dict(spotbugs=0,format=0,checkstyle=0,pmd=4)
    assert first['stageExits']==dict(spotbugs=1,format=0,checkstyle=0,pmd=4)
    assert all(ref(Path(report['raw']['path']))==report['raw'] for report in analysis['reports'].values())
    old_findings=ET.parse(FIRST_STATIC/'spotbugs.xml')
    assert [r.get('type') for r in old_findings.iter('BugInstance')]==['NS_DANGEROUS_NON_SHORT_CIRCUIT']
    spotbugs=analysis['reports']['spotbugs']
    assert spotbugs['exactPhysical'] and spotbugs['physical']==17
    assert all(spotbugs[k]==0 for k in ('findings','errors','missingClasses'))
    checks=analysis['reports']['checkstyle']
    assert checks['hasAllInputRows'] and checks['findings']==checks['processingErrors']==0
    existing=read((E/'PG39910-p020-login-title-independent-v1/pmd-per-site.json'))
    known={(item['owner'],item['anchor'],item['rule'],item['message']):item['reason'] for item in existing}
    assert len(known)==6
    root=ET.parse(STATIC/'pmd.xml').getroot()
    namespace=root.tag.partition('}')[0]+'}'
    assert not root.findall(namespace+'error')
    reviewed=[]
    for file in root.findall(namespace+'file'):
        path=Path(file.get('name'))
        source=path.read_text().splitlines()
        for finding in file.findall(namespace+'violation'):
            line=int(finding.get('beginline'))
            use=(path.name,source[line-1].strip(),finding.get('rule'),(finding.text or '').strip())
            assert use in known and use[2]=='UseConcurrentHashMap'
            reviewed.append(dict(owner=path.name,line=line,anchor=use[1],rule=use[2],message=use[3],
                                 disposition='NOT_APPLICABLE',reason=known[use],source=ref(path)))
    assert len(reviewed)==analysis['reports']['pmd']['findings']==6
    return reviewed


def baseline_oracle(unit):
    base=R['B']/'baseline/current'
    assert not R['git']('diff','--name-only','843de94',unit['source'],'--',str(base))
    u01=read(base/'artifacts/CHR-U01.json')
    u02=read(base/'artifacts/CHR-U02.json')
    assert u01['brand']=='schubert'
    assert u02['titles']==['schubert','schubert - 検索','Scenario Games','Animation','Music','Logs']
    assert sum(1 for path in unit['inputHashes'] if path.startswith(str(base)+'/'))==27
    ui, = R['git']('-c','core.quotePath=false','ls-files','documents/200_UI/260_引継ぎ・監査/264_*').decode().splitlines()
    content=R['git']('show','origin/main:'+ui).decode()
    assert '| DIF-001 | Brand `schubert` | `schubert NK` |' in content and '| CHR-A01/U01/U02 |' in content
    return dict(originals=[ref(base/'artifacts/CHR-U01.json'),ref(base/'artifacts/CHR-U02.json')],
        design=dict(path=ui,sha256=R['hashlib'].sha256(content.encode()).hexdigest()),
        approved={'CHR-U01:/brand':['schubert','schubert NK'],
                  'CHR-U02:/titles/0':['schubert','schubert NK'],
                  'CHR-U02:/titles/1':['schubert - 検索','schubert NK - 検索']},
        retainedOtherTitles=u02['titles'][2:])


def main():
    unit=read(UNIT/'manifest.json')
    first=read(FIRST/'manifest.json')
    begin=read(UNIT/'begin.json')
    chosen=read(STATIC/'manifest.json')
    assert unit['source']==begin['source']==chosen['source']
    assert unit['source']==R['git']('rev-parse','HEAD').decode().strip()
    assert first['source']!=unit['source'] and unit['session']!=first['session']
    assert unit['actualBackendActions']==first['actualBackendActions']==0 and chosen['allPhysicalUnchanged']
    assert len(unit['stages'])==6 and all(row['actualExit']==0 for row in unit['stages'].values())
    assert len(first['stages'])==6 and all(row['actualExit']==0 for row in first['stages'].values())
    previous=P['P']['all_cases'](PREVIOUS)
    first_xml=P['P']['all_cases'](FIRST)
    current=P['P']['all_cases'](UNIT)
    new={(P['NAME'],method+'()') for method in TEST_IDS.values()}
    assert len(previous)==148 and not new & previous.keys()
    assert len(current)==153 and len({group for group,_ in current})==20
    assert current==first_xml==previous|dict.fromkeys(new,'PASS')
    assert all(row=='PASS' for row in current.values())
    classes=Path(unit['classesDir'])
    assert R['physical'](classes)==unit['mainPhysical'] and len(unit['mainPhysical'])==17
    old=read(PREVIOUS/'manifest.json')
    changed={p for p,h in unit['mainPhysical'].items() if old['mainPhysical'][p]!=h}
    assert changed=={P['PKG']+'ArtifactComparator.class',P['PKG']+'ArtifactComparator$ComparisonResult.class'}
    no_ops=Path(unit['initLog']['path'])
    assert ref(no_ops)==unit['initLog']
    data=no_ops.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",data)
    oracle=baseline_oracle(unit)
    reviewed=verify_style()
    OUT.mkdir()
    original=read(next(E.glob('PG37324*/manifest.json')))
    raw=P['P']['unfiltered'](unit,UNIT,classes,OUT,original)
    assert raw['missedMethods']==read(E/'PG39910-p020-login-title-independent-v1/manifest.json')['raw']['missedMethods']
    per=Counter()
    for row in (OUT/'raw.tsv').read_text().splitlines():
        fields=row.split('\t')
        if fields[0]=='CLASS' and fields[1].startswith(P['PKG']+'ArtifactComparator'):
            assert fields[3]=='true'
            for kind,miss,hit in (x.split(':') for x in fields[6:]):
                assert int(miss)==0
                per[kind]+=int(hit)
    assert per['CLASS']==2 and per['BRANCH']>0
    archive=OUT/'class-init.log.gz'
    archive.write_bytes(gzip.compress(data,mtime=0))
    sites=OUT/'pmd-per-site.json'
    save(sites,reviewed)
    manifest=dict(actualExit=0,source=unit['source'],run=unit['run'],unit=ref(UNIT/'manifest.json'),
        firstUnit=ref(FIRST/'manifest.json'),firstStaticNonzero=ref(FIRST_STATIC/'manifest.json'),
        static=ref(STATIC/'manifest.json'),originalTests=148,newDefinitions=5,tests=153,suites=20,
        firstUnitSuccess=153,currentUnitSuccess=153,failed=0,errors=0,skipped=0,notRun=0,
        independentOracle=oracle,testIds=TEST_IDS,raw=raw,comparatorCounters=dict(per),
        pmdRaw=len(reviewed),pmdApplicable=0,pmdUnclassified=0,pmdReviews=ref(sites),
        originalBaselineUnchanged=True,oldCoverageTransferred=False,
        remainingRuntimePreflight='BUG-3311',closedLocal=['BUG-3315','BUG-3316'],horizontalOpen='YKT-2699',
        noRealBrowserOrBackendExecution=True,actualNkChr=False,newAcceptance=0,productTests=0,
        whole451Accepted=False,formalUpdated=False,classInit=ref(archive),terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(OUT/'manifest.json',manifest)
    print(ref(OUT/'manifest.json'),dict(per),raw['rawTotals'])


if __name__=='__main__':
    main()
