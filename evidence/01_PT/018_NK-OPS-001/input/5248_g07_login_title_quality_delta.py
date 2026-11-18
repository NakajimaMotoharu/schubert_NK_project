"""Verify scanner coordinates and the original offline comparator probe for the new interval."""
from pathlib import Path
import json
import re
import runpy
import sys
from xml.etree import ElementTree as ET

HERE=Path(__file__).resolve()
P=runpy.run_path(str(HERE.with_name('5216_g07_scope_build_delta.py')))
E=HERE.parent.parent/'evidence'
CONFIG = {
    '532': {
        'history': ('PG39880-g07-service-state-lock-public-delta-v1',
                    'PG39840-g07-cleanup-static-and-characterization-delta-v1'),
        'units': {'PG39904-p020-approved-login-title148-v1': ('unit', 148)},
        'post': 'PG39910-p020-login-title-independent-v1',
    },
    '536': {
        'history': ('PG39914-g07-approved-login-title-and-quality-delta-v1',
                    'PG39880-g07-service-state-lock-public-delta-v1',
                    'PG39840-g07-cleanup-static-and-characterization-delta-v1'),
        'units': {'PG39922-p020-approved-all-brand153-v1': ('firstUnit', 153),
                  'PG39923-p020-approved-all-brand153-v2': ('unit', 153)},
        'post': 'PG39928-p020-approved-all-brand-independent-v1',
    },
    '542': {
        'history': ('PG39932-g07-four-brand-public-delta-v1',
                    'PG39914-g07-approved-login-title-and-quality-delta-v1',
                    'PG39880-g07-service-state-lock-public-delta-v1'),
        'units': {'PG39944-p020-cache-and-session161-v1': ('unit', 161),
                  'PG39964-p020-invalid-range165-v1': ('firstUnit', 165),
                  'PG39965-p020-invalid-range165-v2': ('unit', 165)},
        'posts': {'PG39944-p020-cache-and-session161-v1': 'PG39954-p020-cache-and-session-independent-v1',
                  'PG39964-p020-invalid-range165-v1': 'PG39970-p020-invalid-range-independent-v1',
                  'PG39965-p020-invalid-range165-v2': 'PG39970-p020-invalid-range-independent-v1'},
    },
    '551': {
        'history': ('PG39974-g07-cache-session-range-public-delta-v1',
                    'PG39932-g07-four-brand-public-delta-v1',
                    'PG39914-g07-approved-login-title-and-quality-delta-v1',
                    'PG39880-g07-service-state-lock-public-delta-v1',
                    'PG39730-g07-weblog-session-and-comparator-public-delta-v1'),
        'units': {'PG39990-p020-search-empty170-v1': ('unit', 170)},
        'post': 'PG39994-p020-search-empty-independent-v1',
    },
    '559': {
        'history': ('PG39998-g07-jars-batch-empty-public-delta-v1',
                    'PG39974-g07-cache-session-range-public-delta-v1',
                    'PG39932-g07-four-brand-public-delta-v1',
                    'PG39730-g07-weblog-session-and-comparator-public-delta-v1'),
        'units': {'PG40014-p020-game-onchange176-v1': ('unit', 176)},
        'post': 'PG40018-p020-game-onchange-independent-v1',
        'detachedValue': 'PG40008-p01810-broker-evidence-value-v2',
    },
    '568': {
        'history': ('PG40028-g07-value-onchange-signed-delta-v1',
                    'PG39998-g07-jars-batch-empty-public-delta-v1',
                    'PG39974-g07-cache-session-range-public-delta-v1',
                    'PG39730-g07-weblog-session-and-comparator-public-delta-v1'),
        'units': {'PG40034-p020-l01-required-actions-v1': ('firstUnit', 182),
                  'PG40035-p020-l01-required-actions-v2': ('unit', 182)},
        'post': 'PG40038-p020-l01-required-actions-independent-v1',
        'firstPmdCount': 13,
    },
    '580': {
        'history': ('PG40046-g07-l01-handoff-public-delta-v1',
                    'PG40028-g07-value-onchange-signed-delta-v1',
                    'PG39998-g07-jars-batch-empty-public-delta-v1',
                    'PG39730-g07-weblog-session-and-comparator-public-delta-v1'),
        'units': {'PG40056-p020-error-disclosure187-v1': ('firstUnit', 187),
                  'PG40057-p020-error-disclosure187-v2': ('unit', 187)},
        'post': 'PG40060-p020-error-disclosure-independent-v1',
        'firstPmdCount': 7,
    },
    '588': {
        'history': ('PG40072-g07-e01-f02-trace-public-delta-v1',
                    'PG40046-g07-l01-handoff-public-delta-v1',
                    'PG40028-g07-value-onchange-signed-delta-v1',
                    'PG39730-g07-weblog-session-and-comparator-public-delta-v1'),
        'units': {'PG40075-p020-o01-restart192-v2': ('unit', 192)},
        'post': 'PG40078-p020-o01-restart-independent-v1',
        'journalValue': 'PG40080-p01810-detached-journal-values-v1',
    },
    '596': {
        'history': ('PG40084-g07-o01-journal-public-delta-v1',
                    'PG40072-g07-e01-f02-trace-public-delta-v1',
                    'PG40046-g07-l01-handoff-public-delta-v1',
                    'PG40028-g07-value-onchange-signed-delta-v1'),
        'units': {'PG40088-p020-s08-voice198-v1': ('firstUnit', 198),
                  'PG40089-p020-s08-voice198-v2': ('unit', 198)},
        'post': 'PG40092-p020-s08-voice-independent-v1',
        'firstPmdCount': 8,
        'firstSpotBugsExit': 1,
    },
    '609': {
        'history': ('PG40096-g07-s08-c02-public-delta-v1',
                    'PG40084-g07-o01-journal-public-delta-v1',
                    'PG40072-g07-e01-f02-trace-public-delta-v1',
                    'PG40046-g07-l01-handoff-public-delta-v1'),
        'units': {'PG40105-p020-u01-menu204-v2': ('firstUnit', 204),
                  'PG40107-p020-u01-menu204-v3': ('unit', 204)},
        'post': 'PG40108-p020-u01-menu-independent-v1',
        'rejected': 'PG40104-p020-u01-menu204-v1',
        'firstPmdCount': 8,
    },
}


def historical_repository_digest(B, line, start, end):
    digest_line = re.fullmatch(rb' {14}"methodTokenSha256": "([0-9a-f]{64})",', line)
    if digest_line is None or (start, end) != (17, 102):
        return None
    project = 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    old = B.git('show', f"{V['fromCommit']}:{project}").splitlines()
    if old.count(line) != 4:
        return None
    original = E/'provisional/PG13640-repository-resource-trace-v1/manifest.json'
    independent = E/'provisional/PG13642-repository-resource-trace-post-v1/manifest.json'
    proof = B.load(independent)
    archived = B.load(original)
    assert proof['actualExit'] == archived['actualExit'] == 0
    assert proof['traceManifestSha256'] == B.ref(original)['sha256']
    assert proof['source'] == archived['source']
    rows = [row for row in archived['currentMainRepositoryStaticContexts']['rows']
            if row['ownership']['methodTokenSha256'] == digest_line[1].decode()]
    if len(rows) != 2 or any(row['ownership']['method'] != 'read' for row in rows):
        return None
    path, = {row['path'] for row in rows}
    assert Path(path).name in {'AsyncJobCountRepository.java', 'OutboxObservationRepository.java'}
    assert {B.sha(B.git('show', f"{proof['source']}:{path}"))} == {r['sourceSha256'] for r in rows}
    return dict(kind='Exact preserved Java method-token digest', proof=B.ref(independent),
                path=path, historicalSource=proof['source'], currentQualificationTransferred=False)


GROUP=sys.argv[2] if len(sys.argv)==3 else '532'
settings=CONFIG[GROUP]
START=next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob(GROUP+'_G07*'))
V=json.loads(START.read_bytes())['values']
OUT=E/V['run']/'scan'
WORK=Path(V['volatileStaging'])
RETAIN=Path.cwd().parent/'pgpt-runs/PG379'/V['run'].lower()
HISTORY=settings['history']



def set_worker(worker):
    worker.OUT,worker.START,worker.TEMP,worker.RETAIN=OUT,START,WORK,RETAIN


def detached_value_probe(B, row, meta, unit_folder):
    post=unit_folder/'independent.json'
    witness=B.load(post)
    report=B.load(unit_folder/'manifest.json')
    original=Path(witness['manifest']['path'])
    assert original.resolve()==unit_folder/'manifest.json'
    assert B.ref(original)['sha256']==witness['manifest']['sha256']==B.ref(unit_folder/'manifest.json')['sha256']
    assert witness['actualExit']==0 and witness['firstDynamicSuccess']==witness['firstDynamicTotal']==3
    assert witness['realBroker']==witness['actualNative']==0
    path=Path(row['path'])
    assert B.ref(WORK/meta['relativeProjection'])['sha256']==B.ref(path)['sha256']==meta['blobSha256']
    terminal=report['stages']['execinfo']
    assert terminal==B.load(unit_folder/'execinfo-exit.json') and terminal['actualExit']==0
    decoded=Path(terminal['log']['path'])
    assert decoded.resolve()==unit_folder/'execinfo.log' and B.ref(decoded)==terminal['log']
    assert terminal['command'][-2:]==['execinfo',str(path.resolve())]
    root=ET.parse(unit_folder/'xml/TEST-junit-jupiter.xml').getroot()
    assert len(list(root.iter('testcase')))==3
    assert not any(n.tag in ('failure','error','skipped') for n in root.iter())
    output=decoded.read_text()
    assert re.findall(r'^Session "([^"]+)":',output,re.M)==[report['session']]
    decoded_rows=re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',output,re.M)
    assert any(crc==witness['recordCrc64'] and name==report['target'] and int(hit)>0 for crc,hit,_,name in decoded_rows)
    assert not any(n.startswith(('org/apache/activemq/','org/postgresql/','com/microsoft/playwright/'))
                   for _,_,_,n in decoded_rows)
    return dict(row,actualExit=0,originalUnitExit=0,ordinaryProbeDataOnly=True,decodedOrigin=terminal['log'],
                qualifiedOriginal=B.ref(post),session=report['session'],decodedRows=len(decoded_rows),
                toolExecutionRepeated=False,priorStaticFailureRemains=False)


def journal_value_probe(B, row, meta, unit_folder):
    post=unit_folder/'independent.json'
    witness=B.load(post)
    report=B.load(unit_folder/'manifest.json')
    assert Path(witness['manifest']['path']).resolve() == (unit_folder/'manifest.json').resolve()
    assert witness['manifest']['sha256'] == B.ref(unit_folder/'manifest.json')['sha256']
    assert witness['actualExit']==report['actualExit']==0 and witness['tests']==report['tests']==2
    assert witness['absentOuterParserInitialization'] and witness['runtimeOperationCount']==0
    path=Path(row['path'])
    assert B.ref(WORK/meta['relativeProjection'])['sha256']==B.ref(path)['sha256']==meta['blobSha256']
    assert Path(report['exec']['path']).resolve() == path.resolve()
    assert B.ref(path)['sha256'] == report['exec']['sha256']
    terminal=report['stageResults']['execinfo']
    assert terminal==B.load(unit_folder/'execinfo-exit.json') and terminal['actualExit']==0
    decoded=Path(terminal['log']['path'])
    assert decoded.resolve() == (unit_folder/'execinfo.log').resolve()
    assert B.ref(decoded)['sha256'] == terminal['log']['sha256']
    assert terminal['command'][-2:]==['execinfo',str(path.resolve())]
    output=decoded.read_text()
    assert re.findall(r'^Session "([^"]+)":',output,re.M)==[report['session']]
    decoded_rows=re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',output,re.M)
    subjects={name:crc for crc,hit,_,name in decoded_rows if int(hit)>0 and name in witness['crc64']}
    assert subjects==witness['crc64'] and len(subjects)==2
    assert not any(n.startswith(('org/apache/activemq/','org/postgresql/','com/microsoft/playwright/'))
                   for _,_,_,n in decoded_rows)
    xml=ET.parse(unit_folder/'xml/TEST-junit-jupiter.xml').getroot()
    assert {r.get('name') for r in xml.iter('testcase')}=={name+'()' for name in witness['testIds'].values()}
    assert not any(n.tag in ('failure','error','skipped') for n in xml.iter())
    return dict(row,actualExit=0,originalUnitExit=0,ordinaryProbeDataOnly=True,decodedOrigin=terminal['log'],
                qualifiedOriginal=B.ref(post),session=report['session'],decodedRows=len(decoded_rows),
                toolExecutionRepeated=False,priorStaticFailureRemains=False)


def rejected_comparator_probe(B, row, meta, folder, post):
    qualified = B.load(post)
    unit = B.load(folder / 'manifest.json')
    original = unit['stages']['unit']
    assert original['actualExit'] == 1 and unit['source'] != qualified['source']
    assert B.ref((folder / 'manifest.json').relative_to(Path.cwd())) == qualified['firstRejectedUnit']
    assert B.ref(folder / 'jacoco.exec') == qualified['firstRejectedExec']
    assert meta['blobSha256'] == B.ref(WORK / meta['relativeProjection'])['sha256'] == qualified['firstRejectedExec']['sha256']
    xml = folder / 'xml/TEST-junit-jupiter.xml'
    assert B.ref(xml.relative_to(Path.cwd())) == qualified['firstRejectedXml']
    tests = ET.parse(xml).getroot().findall('.//testcase')
    counts = {tag: sum(case.find(tag) is not None for case in tests) for tag in ('failure', 'error', 'skipped')}
    assert len(tests) == unit['expected'] == 204
    assert counts == {'failure': 51, 'error': 1, 'skipped': 0}
    assert qualified['initialFES'] == dict(passed=152, failures=51, errors=1, skipped=0, notRun=0)
    terminal = qualified['failedReadOnly']
    decoded = Path(qualified['failedProbeFile']['path'])
    assert terminal['actualExit'] == 0 and terminal['command'][-2:] == ['execinfo', str(folder / 'jacoco.exec')]
    assert B.ref(decoded) == qualified['failedProbeFile'] and terminal['log']['sha256'] == qualified['failedProbeFile']['sha256']
    report = decoded.read_text()
    assert re.findall(r'^Session "([^"]+)":', report, re.M) == [unit['session']]
    rows = re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$', report, re.M)
    assert any(name == 'dev/codex/schubert/characterization/ArtifactComparator' and int(hits) for _, hits, _, name in rows)
    assert not any(name.startswith(('dev/codex/schubert/nk/', 'org/postgresql/', 'com/microsoft/playwright/'))
                   for _, _, _, name in rows)
    return dict(row, actualExit=0, originalUnitExit=1, failedRunNotSuccess=True, ordinaryProbeDataOnly=True,
                decodedOrigin=B.ref(decoded), qualifiedOriginal=B.ref(post), session=unit['session'],
                decodedRows=len(rows), toolExecutionRepeated=False)


def classify():
    p=P['load']('g07_login_qualification','5182_g07_jdbc_metrics_cached_classification.py')
    B=p.B
    set_worker(p.t.WRAPPER)
    p.OUT=p.t.OUT=B.OUT=OUT
    p.WORK=p.t.WORK=B.WORK=WORK
    p.t.PREPARE_RUNS=()
    p.t.ORDINARY_BUILD_RUNS=()
    before_ref=p.proven_content

    def old_rows():
        known=set()
        for run in HISTORY:
            manifest=E/run/'scan/manifest.json'
            prior=B.load(manifest)
            assert prior['qualifiedRangeOnly'] and prior['confirmedSecrets']==prior['unresolvedCandidates']==0
            for label in ('classified-findings.json','pinned-sdk-origin.json','additional-build-origins.json'):
                origin=prior['exactPrivateProofFiles'].get(label)
                if origin:
                    f=Path(origin['path'])
                    assert f.is_relative_to(RETAIN.parent) and B.ref(f)==origin
                    for r in B.load(f):
                        if r['ground']:
                            known.add((r['rule'],r['lineSha256'],r['startColumn'],r['endColumn']))
        return known,B.ref(E/HISTORY[0]/'scan/manifest.json')

    def all_binary(original, by_key, unused_scan):
        verified=[]
        for row in original:
            path=Path(row['path'])
            name=path.parent.name
            if row.get('actualExit')!=0 and name==settings.get('detachedValue') and path.name=='jacoco.exec':
                unit_folder=E/name
                assert path.resolve()==unit_folder/'jacoco.exec'
                verified.append(detached_value_probe(B,row,by_key[row['path'],row['blob']],unit_folder))
                continue
            if row.get('actualExit')!=0 and name==settings.get('journalValue') and path.name=='jacoco.exec':
                unit_folder=E/name
                assert path.resolve()==unit_folder/'jacoco.exec'
                verified.append(journal_value_probe(B,row,by_key[row['path'],row['blob']],unit_folder))
                continue
            if row.get('actualExit') != 0 and name == settings.get('rejected') and path.name == 'jacoco.exec':
                folder = E / name
                assert path.resolve() == folder / 'jacoco.exec'
                verified.append(rejected_comparator_probe(B, row, by_key[row['path'], row['blob']],
                                                          folder, E / settings['post'] / 'manifest.json'))
                continue
            if row.get('actualExit')==0 or name not in settings['units'] or path.name!='jacoco.exec':
                continue
            unit_folder=E/name
            assert path.resolve()==unit_folder/'jacoco.exec'
            ticket,expected=settings['units'][name]
            meta=by_key[row['path'],row['blob']]
            unit=B.load(unit_folder/'manifest.json')
            start=B.load(unit_folder/'begin.json')
            post=E/(settings.get('post') or settings['posts'][name])/'manifest.json'
            finished=B.load(post)
            assert start['source']==unit['source']
            assert Path(finished[ticket]['path']).resolve()==unit_folder/'manifest.json'
            assert finished[ticket]['sha256']==B.ref(unit_folder/'manifest.json')['sha256']
            assert finished['tests']==unit['expected']==expected
            if ticket=='unit':
                assert unit['source']==finished['source']
            else:
                assert unit['source']!=finished['source']
                typed_failure=finished.get('firstStaticNonzero')
                static_failure=typed_failure or finished['firstStaticFailure']
                prior_static=Path(static_failure['path'])
                assert B.ref(prior_static)==static_failure
                static_result=B.load(prior_static)
                if typed_failure:
                    assert static_result['stageExits']['spotbugs']==1
                else:
                    assert static_result['stageExits']['pmd']==4
                    assert static_result['reports']['pmd']['findings']==settings.get('firstPmdCount',8)
                    if 'firstSpotBugsExit' in settings:
                        assert static_result['stageExits']['spotbugs']==settings['firstSpotBugsExit']
            terminal=unit['stages']['execinfo']
            assert terminal==B.load(unit_folder/'execinfo-exit.json') and terminal['actualExit']==0
            decoded=Path(terminal['log']['path'])
            assert decoded==unit_folder.relative_to(Path.cwd())/'execinfo.log' or decoded==unit_folder/'execinfo.log'
            assert B.ref(decoded)==terminal['log']
            assert terminal['command'][-2:]==['execinfo',str((unit_folder/'jacoco.exec').resolve())]
            assert meta['blobSha256']==B.ref(WORK/meta['relativeProjection'])['sha256']==B.ref(path)['sha256']
            root=ET.parse(unit_folder/'xml/TEST-junit-jupiter.xml').getroot()
            assert len(list(root.iter('testcase')))==expected
            assert not any(n.tag in ('failure','error','skipped') for n in root.iter())
            text=decoded.read_text()
            assert re.findall(r'^Session "([^"]+)":',text,re.M)==[unit['session']]
            rows=re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',text,re.M)
            assert any(n=='dev/codex/schubert/characterization/ArtifactComparator' and int(hit)>0 for _,hit,_,n in rows)
            assert not any(n.startswith(('dev/codex/schubert/nk/','org/postgresql/','com/microsoft/playwright/')) for _,_,_,n in rows)
            verified.append(dict(row,actualExit=0,originalUnitExit=0,ordinaryProbeDataOnly=True,
                                 decodedOrigin=terminal['log'],qualifiedOriginal=B.ref(post),
                                 session=unit['session'],decodedRows=len(rows),toolExecutionRepeated=False,
                                 priorStaticFailureRemains=ticket!='unit'))
        return verified

    p.exact_previous=old_rows
    p.t.extra_binary=all_binary
    def current_content(line, start, end, digests, reachable):
        normal=before_ref(line,start,end,digests,reachable)
        if not normal and GROUP=='580':
            return historical_repository_digest(B,line,start,end)
        if not normal and GROUP=='609':
            known_line='b5d6756add19f5ffa0bc023ee60a7734418de2c532fbefafe5cc10b147045b59'
            if B.sha(line)!=known_line or (start,end)!=(1455,1499):
                return None
            progress='documents/400_PGPT/450_品質/460_基盤残件・再開優先順.md'
            old=B.git('show',f"{V['fromCommit']}:{progress}").splitlines()
            assert old.count(line)==1
            assert b'G07remaining3315+22actualSecretCountnull, freshquota10percent' in line
            return dict(kind='Exact preserved planning counts and unknown polarity',
                        path=progress,originalCommit=V['fromCommit'],line=old.index(line)+1,lineSha256=known_line)
        if normal or GROUP!='559':
            return normal
        known_line='2407d662eeca6d2478a97780e1a71fdb2194e38e34255f22a41671e0c88ad520'
        if B.sha(line)!=known_line or (start,end)!=(1155,1196):
            return None
        a,z=start-1,end
        assert line[:a].endswith(b'from current Java/public evidence; no private logs, actual secrets/')
        assert line[z:].startswith(b'actions. Identify missing ordinary redaction contract')
        assert re.fullmatch(rb'keys, Root/[A-Za-z]{6}/VM/DB/permit/[A-Za-z]{10} ',line[a:z])
        progress='documents/400_PGPT/450_品質/456_領域別進捗・利用枠・中断再開管理.md'
        old=B.git('show',f"{V['fromCommit']}:{progress}").splitlines()
        assert old.count(line)==1
        return dict(kind='Exact preserved work-scope prose',path=progress,
                    originalCommit=V['fromCommit'],line=old.index(line)+1,lineSha256=known_line)

    p.proven_content=current_content
    p.main()


def retain():
    p=P['load']('g07_login_retain','5184_g07_jdbc_metrics_retain_compact.py')
    set_worker(p.w)
    value=p.p.load(OUT/'qualified-cached-initial.json')
    assert value['unresolvedCandidates']==value['unqualifiedBinary']==0
    original=p.p.load(RETAIN/'initial-classification'/'qualified-cached-initial.json') if GROUP in ('551','559','580','609') else None
    if original:
        assert original['unresolvedCandidates']==(8 if GROUP=='580' else 1) and original['unqualifiedBinary']==0
    p.p.write(OUT/'qualified-final-private-detail.json',dict(
        value,verifier=p.p.ref(HERE),scannerExecutionCount=1,initialClassificationExit=int(GROUP in ('532','559','588','609')),
        initialIssue='Exact archived path was relative instead of absolute' if GROUP in ('532','559','588','609') else None,
        initialSetupExit=int(GROUP=='551'),
        initialSetupIssue='Public run directory parent was absent before scanner start' if GROUP=='551' else None,
        firstUnclassified=original['unresolvedCandidates'] if original else None,
        firstClassification=tuple(p.p.ref(f) for f in sorted((RETAIN/'initial-classification').iterdir())) if original else ()))
    p.DETAILS=('scan-terminal.json','qualified-cached-initial.json','qualified-final-private-detail.json',
               'classified-findings.json','remaining-origins.json','binary-qualification.json')
    p.main()


if __name__=='__main__':
    {'classify':classify,'retain':retain}[sys.argv[1]]()
