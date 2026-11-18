"""Trace the four recently changed Main types into their independent published PT runs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = Path('documents/400_PGPT/470_PMO')
START = D / '601_WBS66短期実行_20261117/496_G08四実装の公開trace開始.json'
REGISTRY = D / '485_WBS網羅性・受入対応.json'
SS = Path('documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md')
LOCAL = Path('documents/400_PGPT/440_判断/441_実装判断記録.md')
LEDGER = Path('documents/900_OTHER/910_台帳/915_障害表.md')
YKT = LEDGER.with_name('916_横展開管理台帳.md')
DETAIL = [
    ('PG39606', 'OutboxObservationRepository', 'OutboxObservationRepositoryTest', 'SSC-470',
     'BUG-3292', 'YKT-2597',
     [('OUTBOXDB011', 'outboxDb011SameReadAndCloseThrowablePreservesJdkSelfSuppressionAndReverseClose')]),
    ('PG39656', 'JdbcOutboxRepository', 'JdbcOutboxPortTest', 'SSC-471', 'BUG-3296', 'YKT-2597', [
     ('PT-OUT-JDBC010', 'requiredStatementNullStopsAllFourOperationsBeforeBinding'),
     ('PT-OUT-JDBC011', 'requiredRowsNullClosesTheAlreadyAcquiredStatementExactlyOnce'),
     ('PT-OUT-JDBC012', 'jdbcPrimarySuppressionAndJdkSelfFailureCloseRowsBeforeStatement')]),
    ('PG39690', 'WebLogOutboxRepository', 'WebLogOutboxPortTest', 'SSC-472', 'BUG-3300', 'YKT-2597', [
     ('WLG-PORT-021', 'port021AllFourMissingStatementsAreRejectedBeforeBind'),
     ('WLG-PORT-022', 'port022MissingRowsCloseOnlyTheAcquiredStatementOnce'),
     ('WLG-PORT-023', 'port023AliasedRowsFailureKeepsPrimaryCauseAndStatementSuppression')]),
    ('PG39762', 'ProcessResourceScope', 'ProcessResourceScopeValueContractTest', 'PG-D-1185',
     'BUG-3305', 'YKT-2664', [
     ('PT-OPS-SCOPEVALUE001', 'scopeValue001RejectsAnyInstanceOfTheStaticNamespace'),
     ('PT-OPS-SCOPEVALUE002', 'scopeValue002RejectsMissingInputsWithoutAcquiringOrReleasingThem'),
     ('PT-OPS-SCOPEVALUE003', 'scopeValue003OwnsEachAcquisitionThroughItsOwnRelease'),
     ('PT-OPS-SCOPEVALUE004', 'scopeValue004BodyAndReleaseFollowTheIndependentLiteralPriorityTable')]),
]


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def checked(item):
    p=Path(item['path'])
    assert ref(p)==item
    return p


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def lineage(post, profile, target, test, core, current_core):
    selected = [Path(name) for name in profile['mainSources'] if name.endswith('/'+target+'.java')]
    [main] = selected
    [test_path] = [Path(row['path']) for row in profile['testSources'] if row['path'].endswith('/'+test+'.java')]
    fixed = post['source']
    for path in (main, test_path):
        bytes=path.read_bytes()
        assert sha(bytes)==post['inputHashes'][str(path)]
        assert git('show', f'{fixed}:{path}')==git('show', f'{current_core}:{path}')==bytes
    assert git('show', f'{core}:{main}')==main.read_bytes()
    class_name = str(main).split('/src/main/java/', 1)[1][:-5]
    assert post['classIds'][class_name]
    return main,test_path,class_name


def proof_xml(post, post_path, suite):
    xml = post_path.with_name('original-TEST-junit-jupiter.xml')
    assert ref(xml)['sha256'] == post['files'][xml.name]
    tree = ET.parse(xml).getroot()
    assert all(int(tree.get(key,'0'))==0 for key in ('errors','failures','skipped'))
    rows = tree.findall('testcase')
    assert len(rows)==post['tests']
    assert not any(c.tag in {'error','failure','skipped'} for row in rows for c in row)
    return ref(xml), {row.get('name') for row in rows
                      if row.get('classname','').endswith('.'+suite)}


def scenario(details, current_core, owner):
    pg, target, suite, approval, bug, ykt, ids=details
    [evidence] = list(E.glob(pg+'*/manifest.json'))
    m=read(evidence)
    post_path=checked(m['proofs']['post'])
    post=read(post_path)
    conf=read(checked(post['config']))
    assert m['actualExit']==post['actualExit']==0 and m['source']==post['source']
    assert m['productionCoreMain']==post['productionCoreMain']
    assert m['tests']==post['tests'] and m['newTestDefinitions']==len(ids)
    assert not post['oldExecCombined'] and not post['manualCoverageExclusions']
    main,test,class_name=lineage(post,conf,target,suite,m['productionCoreMain'],current_core)
    assert owner[str(main)]['class']==class_name
    (xml,methods)=proof_xml(post,post_path,suite)
    specs=[checked(x) for x in conf['oracleSpecs']]
    test_src=test.read_text()
    specs_text='\n'.join(p.read_text() for p in specs)
    for ident, method in ids:
        assert method+'()' in methods and f'void {method}(' in test_src
        if ident.startswith('PT-OPS-SCOPEVALUE'):
            assert 'PT-OPS-SCOPEVALUE001' in specs_text and 'PT-OPS-SCOPEVALUE004' in specs_text
        else:
            assert ident in specs_text
    if 'canonicalDesign' in m:
        design=m['canonicalDesign']
        assert git('merge-base','--is-ancestor',design,'origin/main')==b''
        assert approval.encode() in git('show',f'{design}:{SS}')
        design_ref=dict(path=str(SS), commit=design, locator=approval)
    else:
        assert approval in LOCAL.read_text() and approval in git('show',f"{m['productionCoreMain']}:{LOCAL}").decode()
        design_ref=dict(path=str(LOCAL),commit=m['productionCoreMain'],locator=approval)
    assert bug in LEDGER.read_text() and ykt in YKT.read_text()
    exec_file=post_path.with_name('jacoco.exec')
    assert ref(exec_file)['sha256']==post['files'][exec_file.name]
    return dict(production=ref(main),currentCoreSameByte=True,owner=owner[str(main)]['owner'],
                costOwner=owner[str(main)]['costOwner'], test=ref(test),
                independentSpecs=[ref(p) for p in specs], approvedSpec=design_ref,
                tests=[dict(id=k,method=v) for k,v in ids], wholeOriginalTests=post['tests'],
                unitSource=post['source'], originalCore=post['productionCoreMain'],
                originalSession=post['run'], caseEvidence=xml, originalScope=ref(evidence),
                originalPost=ref(post_path), execEvidence=ref(exec_file), sameClassCrc=post['classIds'][class_name],
                issue=[dict(id=bug,path=str(LEDGER)), dict(id=ykt,path=str(YKT))])


def main():
    start=read(START)
    core=start['values']['productionCoreMain']
    head=start['values']['source']
    assert git('rev-parse','HEAD').decode().strip()==head and not git('diff','--name-only',core,head,'--','src')
    owner={p['path']:p for p in read(REGISTRY)['artifacts']}
    rows=[scenario(props,core,owner) for props in DETAIL]
    seen=[t['id'] for row in rows for t in row['tests']]
    assert len(seen)==len(set(seen))==11
    assert len({r['originalSession'] for r in rows})==4
    p=E/start['values']['run']/'manifest.json'
    with p.open('x') as f:
        json.dump(dict(actualExit=0, startEvent=start['eventId'], source=head, currentCore=core,
                       ownerRegistry=ref(REGISTRY), mappedCases=11, trace=rows,
                       productTests=0, measuredCoverageAdded=0, execUnion=False,
                       wholeG08Accepted=False, newAcceptance=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       verifier=ref(Path(__file__))), f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(ref(p))


if __name__=='__main__':
    main()
