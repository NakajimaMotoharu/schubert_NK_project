"""Frozen actual PG453 targeted host evidence; never native/full/formal acceptance."""
import hashlib
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
tag = 'target-selected-v4'
assert sys.argv[1:] in ([], ['PG454'], ['PG454_NATIVE'])
native_group = sys.argv[1:] == ['PG454_NATIVE']
graph = bool(sys.argv[1:])
run = 'PG454' if graph else 'PG453'
if graph:
    tag = 'graph-selected-v8'
if native_group:
    tag = 'native-selected-v4'
prefix = work / (run.lower() + '-' + tag)
frozen = work / (prefix.name + '-frozen')
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional' / (run + '-' + tag)
source = '4d61cc280c863853931df975141f351c3db7b387'
names = {'NotificationBusinessMvcConfiguration', 'TargetOperationInput', 'CancelForm',
         'QuestionDeleteForm', 'NotificationController', 'QuestionController',
         'QuestionDetailViewModel', 'QuestionListViewModel'}
if graph:
    source = '2e529b880b89ca4f141d3ae870b674c4fb884804'
    names = {'ApiManagementServer', 'ArtemisReplyConsumers', 'WebApplication',
             'WebBusinessAssembly', 'WebHttpAdmission', 'WebHttpServer',
             'WebHttpAdmissionValve', 'WebHttpAdmissionValve$Lease', 'WebManagementServer'}
counts = (5, 7, 10, 33, 63, 8) if graph else (5, 7, 10, 99, 182, 43)
total, suites = (126, 18) if graph else (346, 33)
if native_group:
    source = '2aeb40aeba752e500b7a2d564ad62dd175ce5976'
    names |= {'WebBrokerContexts', 'ServiceProcessResources', 'WebProcessLifetime',
              'RevocationRetryWorker', 'WebLogReplayWorker', 'JmsRequestReplyClient',
              'MediaRangeService', 'WebNativeRuntime'}
    counts = (5, 7, 25, 33, 95, 8)
    total, suites = 173, 26
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == source
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log
assert log.count('BugInstance size is 0') == 6 and 'do not match with execution data' not in log
modules, coverage, cases = {}, {}, set()
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'),
                            counts, strict=True):
    target = frozen / module / 'target'
    reports = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
    count = 0
    for report in reports:
        suite = E.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert int(suite.get('tests')) == len(suite.findall('testcase'))
        safe = E.Element('testsuite', {k: suite.get(k) for k in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out', 'system-err') for child in case)
            E.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
            cases.add(case.get('classname'))
        path = out / 'junit' / module / report.name
        path.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(path, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected
    modules[module] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    static = E.parse(target / 'spotbugsXml.xml').getroot()
    assert not static.findall('BugInstance') and int(static.find('Errors').get('errors')) == 0
    for cls in E.parse(target / 'site/jacoco/jacoco.xml').findall('.//class'):
        name = cls.get('name').rsplit('/', 1)[-1]
        if name in names and cls.findall('counter'):
            coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))}
                              for c in cls.findall('counter')}
assert set(coverage) == names
incomplete = {'WebApplication', 'WebBusinessAssembly', 'WebNativeRuntime',
              'WebProcessLifetime', 'WebBrokerContexts'} if native_group else set()
assert all(c['missed'] == 0 for n,v in coverage.items() if n not in incomplete for c in v.values())
assert sum(m['tests'] for m in modules.values()) == total and len(cases) == suites
before = []
for version, code, tests, failures, limitations in (
    (1, 1, 121, 0, ['Web compile NullAway failed; Web/Batch PT and static/coverage not-run']),
    (2, 1, 301, 1, ['HTTP post not reached; Batch and Web static/coverage not-run']),
    (3, 0, 344, 0, ['Target Notification branch missed1/line missed2; target coverage gate not accepted']),
):
    if graph:
        break  # PG454 failed runs remain individually recorded in 086, never aggregated.
    prior = work / f'pg453-target-selected-v{version}'
    assert prior.with_suffix('.exit').read_text().strip() == str(code)
    before.append({'id': prior.name, 'accepted': False, 'exitCode': code, 'tests': tests,
                   'failures': failures, 'errors': 0, 'skipped': 0, 'limitations': limitations,
                   'logSha256': sha(prior.with_suffix('.log')),
                   'sourceFilesSha256': sha(prior.with_suffix('.source-files.sha256')),
                   'bytePreservation': str(work / (prior.name + '-frozen'))})
manifest = {
    'id': run + '-' + tag, 'sourceHead': source,
    'sourceDirty': 'PG-D368 Notification CANCEL/Question DELETE, same-core retained operation token, closed form/template/view and independent golden/SQL/HTTP/100 replay PT; BUG646 static-null and BUG647 independent order-oracle correction',
    'formal': False, 'fullRun': False, 'native': False, 'branch': 'dev-foundation',
    'startedAt': prefix.with_suffix('.started').read_text().strip(),
    'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg453_selected.sh target-selected-v4 ' + source + ' exact33Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'exitCode': 0, 'tests': total, 'suites': suites, 'modules': modules, 'testClasses': sorted(cases),
    'coverage': coverage, 'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0},
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')),
    'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'logSha256': sha(prefix.with_suffix('.log')),
    'sourceArchive': {'privatePath': str(prefix.with_suffix('.source.tar')), 'sha256': sha(prefix.with_suffix('.source.tar'))},
    'bytePreservation': str(frozen),
    'testIds': [f'PT-TARGET{n:03d}' for n in range(1, 9)]
               + [f'NTC-BIZ{n:03d}' for n in range(1, 9)]
               + [f'QDL-BIZ{n:03d}' for n in range(1, 10)],
    'qa': ['QA-049'], 'bugs': ['BUG-646', 'BUG-647'], 'ykt': ['YKT-458', 'YKT-459'],
    'expected': '083: manual304 whole requests and 48/32/24 byte vectors; RECEIVED-only NTC form; QDL detail-issued one token, same pending/completed UUID/first completed time, full10pending refuse; null/missing/unknown/owner/fault/fatal boundaries; real business API SQL version1 and100calls/99Inbox replays; real HTTP CSRF403/update0,302/replay one update, all50 owner links sorted ID50..1 from UI224 and zero list tokens, independently fixed100Unicode-codepoint summary and escaped body; SQL transaction ownership0 on actual sending thread and all resources0 after futures',
    'actual': '346PT33suite/FES0/static6zero; changed8 executable classes all line/method/class/branch missed0; actual isolated PostgreSQL/business API and same-core secured host HTTP passed',
    'before': before,
    'limitations': ['Selected host only, actual Artemis/native/full regression not accepted',
                    'Collector added after selected source capture; grouped fresh full includes it',
                    'Formal PT-WEB-20260925-24/source858713c0/1964PT/53scope unchanged'],
    'redaction': 'JUnit properties/stdout/stderr removed; no real credential/password/session/cookie/token/context/key/DB dump/provider raw output',
}
if graph:
    manifest.update({
        'sourceDirty': 'PG-D369 C1 same-core bridge/C2 full business assembly, actual HTTP terminal admission and management, requested/confirmed JMS closure; independent boundary/null/async/fatal/interrupt PT',
        'command': 'bash WorkPG379/pg454_selected.sh graph-selected-v8 ' + source + ' exact18Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
        'testIds': ['NATIVE-CORE001..003', 'NATIVE-GRAPH001..002', 'NATIVE-READY001..006', 'NATIVE-STOP001..004', 'reply/broker requested-confirmed retry', 'API management caller interrupt'],
        'qa': ['QA-047', 'QA-049', 'QA-050'],
        'bugs': [f'BUG-{n}' for n in range(648, 655)],
        'ykt': ['YKT-460', 'YKT-461', 'YKT-462'],
        'expected': '085: independently handwritten32 MVC paths; actual secured Login200/title/CSRF and protected302; borrowed17 ports with same core/Spring pair; initial503 then admission, real held AsyncContext prevents drain and terminal completion permits it; actual management five fixed info values/DOWN/UP/DOWN, one Ready release, bind before start refusal, actual uncooperative handler and interrupted cleanup UNKNOWN with retry; provider repeated close UNKNOWN/fatal identity; mandatory12 null constructors; no production-derived golden output',
        'actual': '126PT18suite/FES0/static6zero; nine listed executable classes every counter missed0; actual isolated PG/embedded Artemis/full MVC/HTTP/async/JDK management lifecycle verified',
        'before': {'resultDocument': 'evidence/01_PT/016_NK-WEB-002/086_NK-WEB-002_native組立・所有実行結果.md', 'acceptedByThisManifest': False},
        'limitations': ['Selected host only; full grouped regression/native/formal not accepted',
                        'WebBrokerContexts native create/credential-copy line4/method2 missed: not program100%',
                        'Legacy partial runtime/outer owner/worker budget/native graph remain open',
                        'Collector profile added after frozen run; fresh grouped full must include it',
                        'Formal PT-WEB-20260925-24/source858713c0/1964PT/53scope unchanged'],
    })
if native_group:
    manifest.update({
        'sourceDirty': 'PG-D369/370 C3/C4 native graph/owned HTTP/remaining worker budget/lifetime/validated configuration/native outer UNKNOWN retention; BUG655..660 fixes',
        'command': 'bash WorkPG379/pg454_selected.sh native-selected-v4 ' + source + ' exact26Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
        'testIds': ['NATIVE-CORE/GRAPH/READY/STOP/OWNER/BUDGET/CONFIG/LIFE/OUTER', 'existing API/SQL/JMS/media/native-entry refusal regression'],
        'bugs': [f'BUG-{n}' for n in range(648, 661)],
        'ykt': [f'YKT-{n}' for n in range(460, 467)],
        'expected': '085 C3/C4: capture before real Tomcat vendor start and retain fatal/UNKNOWN owner; actual repeated join with remaining0..30s budget; initial1/12/20 and media1/2/20 saturation/next send or file0/recovery; config100ms across eight real facade fields/default2s; same lifetime TERM admission refusal; child actual native-release UNKNOWN/interrupt/periodic observation attempts1/downstream0/alive with fixture SIGTERM143, not normal provider cleanup; real PG five credentials/normal retained-mode and legacy partial/compound scopes',
        'actual': '173PT26suite/FES0/static6zero; twelve listed classes every counter missed0. NativeRuntime/ordinary main/native admission not accepted; known missed counters preserved without exclusions',
        'limitations': ['Selected host components only; grouped fresh full and actual ordinary native/parent/Caddy/DONE/CHR not accepted',
                        'WebApplication old delegates L3/M2 and Assembly default constructor L1 remain for fresh full; Broker native L4/M2, Lifetime shutdown/retain and NativeRuntime graph require actual native proof',
                        'Collector profile added after byte/source capture; grouped full must include it',
                        'Legacy partial runtime remains under BUG629/YKT446/460 until native scope/non-applicability and independent recurrence proof',
                        'Formal PT-WEB-20260925-24/source858713c0/1964PT/53scope unchanged'],
    })
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': manifest['tests'], 'coverageClasses': len(coverage), 'manifestSha256': sha(out / 'manifest.json')}))
