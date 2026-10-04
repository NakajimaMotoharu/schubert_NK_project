"""Source-frozen six-module PG/PT capture. Not formal, native, or coverage-100 acceptance."""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
runroot = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
assert len(sys.argv) == 4
source, identifier, logfile = sys.argv[1:]
assert re.fullmatch(r'[0-9a-f]{40}', source)
assert re.fullmatch(r'PG[0-9]{3}-[a-z0-9-]+', identifier)
assert re.fullmatch(r'pg[0-9]{3}-[a-z0-9-]+\.log', logfile)
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == source
subprocess.run(['git', 'diff', '--exit-code', source, '--', 'src', 'tools', 'pom.xml'], cwd=root, check=True)
assert not subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'src', 'tools'], cwd=root, text=True).strip()
logpath = runroot / logfile
log = logpath.read_text()
assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log and 'BUILD FAILURE' not in log
totals = re.findall(r'\[INFO\] Results:\s*\[INFO\]\s*\[INFO\] Tests run: ([0-9]+), Failures: 0, Errors: 0, Skipped: 0', log)
assert len(totals) == 6
out = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional' / identifier
assert not out.exists()
modules, coverage = {}, {}
for name, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), map(int, totals), strict=True):
    target = root / f'src/schubert-nk-{name}/target'
    count = 0
    reports = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
    assert reports and expected > 0
    for report in reports:
        suite = ET.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert len(suite.findall('testcase')) == int(suite.get('tests'))
        safe = ET.Element('testsuite', {k: suite.get(k) for k in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out', 'system-err') for child in case)
            ET.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
        path = out / 'junit' / name / report.name
        path.parent.mkdir(parents=True, exist_ok=True)
        ET.indent(safe)
        ET.ElementTree(safe).write(path, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected, (name, count, expected)
    modules[name] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in ET.parse(target / 'site/jacoco/jacoco.xml').getroot().findall('counter')}
    bugs = ET.parse(target / 'spotbugsXml.xml').getroot()
    assert not bugs.findall('BugInstance') and int(bugs.find('Errors').get('errors')) == 0
manifest = {
    'id': identifier, 'formal': False, 'sourceCommit': source, 'branch': 'dev-foundation',
    'environment': 'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'six modules: clean test spotbugs:check jacoco:report jar:jar dependency-plugin3.9.0:copy-dependencies/list runtime -o',
    'exitCode': 0, 'modules': modules, 'tests': sum(m['tests'] for m in modules.values()), 'coverage': coverage,
    'logSha256': hashlib.sha256(logpath.read_bytes()).hexdigest(),
    'testIds': ['CEXEC001..004', 'CINSPECT001..004', 'COWNERFILE001..002', 'CTERM001..005', 'CCYCLE001..004', 'BCATALOG001'],
    'bugs': ['BUG-362', 'BUG-363', 'BUG-364', 'BUG-365', 'BUG-366'],
    'ssc': ['SSC-119', 'SSC-120', 'SSC-121'], 'ykt': ['YKT-284', 'YKT-285', 'YKT-286', 'YKT-287'],
    'limitations': ['native Cleanup/Inspector/Transfer not accepted', 'native refusal/explicit resume pending', 'failed Backup six SKIP/Broker/Expiry/issuer/API/Web/CHR pending', '100% coverage and formal PT-WEB-20260925-24 unchanged'],
    'redaction': 'JUnit properties/stdout/stderr/provider diagnostics omitted; no credential/session/token/password/key/dump',
    'finishedAt': next(line.split('Finished at: ', 1)[1] for line in log.splitlines() if 'Finished at: ' in line),
}
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
if int(identifier[2:5]) >= 391:
    manifest['bugs'].append('BUG-367')
    manifest['ssc'].append('SSC-122')
    manifest['ykt'].append('YKT-288')
    manifest['testIds'].append('COWNER005')
if int(identifier[2:5]) >= 392:
    manifest['bugs'].append('BUG-368')
    manifest['ssc'].append('SSC-123')
    manifest['ykt'].append('YKT-289')
    manifest['testIds'].append('CCYCLE005')
if int(identifier[2:5]) >= 393:
    manifest['ssc'].append('SSC-124')
    manifest['testIds'].extend(['CFREQ001..006', 'CFDB001..004', 'CFLOW001..004'])
    manifest['limitations'] = ['failed Backup/Cleanup native acceptance pending', 'Broker/Expiry/issuer/API/Web/CHR pending', '100% coverage and formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 394:
    manifest['ssc'].append('SSC-125')
    manifest['bugs'].extend(['BUG-369', 'BUG-370'])
    manifest['ykt'].extend(['YKT-290', 'YKT-291'])
    manifest['testIds'].extend(['BROKERLIVE001..004', 'BROKERSTART001..004', 'BROKERQUERY001..003', 'EXPARENT001..005'])
    manifest['limitations'] = ['same-source native Broker/Expiry acceptance pending', 'failed Backup/Cleanup native and real hard-timeout pending', 'issuer/API/Web/CHR pending', '100% coverage and formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 395:
    manifest['ssc'].append('SSC-126')
    manifest['bugs'].append('BUG-372')
    manifest['ykt'].append('YKT-292')
    manifest['testIds'].extend(['ISSCFG001..002', 'ISSSTEP002..003', 'ISSGATE002'])
    manifest['testIds'].extend(['ISSROOT001..003'])
    manifest['bugs'].append('BUG-373')
    manifest['ykt'].append('YKT-293')
    manifest['limitations'] = ['same-source native preserved terminal/reference/config handoff pending', 'six roots and five concrete gate collection/publication caller incomplete', 'failed Backup/Cleanup native and real hard-timeout pending', 'issuer/API/Web/CHR pending', '100% coverage and formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 396:
    manifest['ssc'].append('SSC-127')
    manifest['bugs'].append('BUG-375')
    manifest['ykt'].append('YKT-295')
    manifest['testIds'].append('ISSBROKERSTOP001')
    manifest['limitations'] = ['same-source native prior SIGTERM143/journal/fresh Broker/Expiry/six roots pending', 'five actual gates and normal issuer publication caller incomplete', 'failed Cleanup/hard-timeout/native negative closure pending', 'issuer/API/Web/CHR and coverage100/formal run24 unchanged']
if int(identifier[2:5]) >= 397:
    manifest['ssc'].append('SSC-128')
    manifest['bugs'].append('BUG-376')
    manifest['ykt'].append('YKT-296')
    manifest['testIds'].extend(['ISSGATE003', 'MMAIN010'])
    manifest['limitations'] = ['same-source native Expiry reread and six-root collection pending', 'five actual gates and normal issuer publication caller incomplete', 'known guard failure/native negatives/hard-timeout coverage pending', 'issuer/API/Web/CHR and coverage100/formal run24 unchanged']
if int(identifier[2:5]) >= 399:
    manifest['ssc'].extend(['SSC-129', 'SSC-130'])
    manifest['bugs'].extend(['BUG-379', 'BUG-380', 'BUG-381', 'BUG-382', 'BUG-383'])
    manifest['ykt'].extend(['YKT-299', 'YKT-300', 'YKT-301', 'YKT-302', 'YKT-303'])
    manifest['testIds'].extend(['ISSPG001..003', 'ISSREL001..002', 'ISSBROKER001..004', 'MQUNKNOWN001..004', 'MDB020'])
    manifest['limitations'] = ['same-source native DB/release/Broker full observations and gate frames pending', 'STOP_SET/retention/ten steps/full proof/publication/A handoff/API/Web/CHR incomplete', 'native unknown/negative/hard-timeout and coverage100 pending', 'formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 400:
    manifest['bugs'].extend(['BUG-384', 'BUG-385'])
    manifest['ykt'].extend(['YKT-304', 'YKT-305'])
    manifest['testIds'].append('ISSBROKER005')
    manifest['command'] += ' outputFile=target/runtime-dependencies.txt appendOutput=false'
if int(identifier[2:5]) >= 401:
    manifest['ssc'].extend(['SSC-131', 'SSC-132'])
    manifest['bugs'].append('BUG-386')
    manifest['ykt'].append('YKT-306')
    manifest['testIds'].append('ISSSTOP001..007')
    manifest['limitations'] = ['same-source actual STOP_SET and journal-content reread pending', 'retention/ten steps/full proof/publication/A handoff/API/Web/CHR incomplete', 'native negatives/hard-timeout and coverage100 pending', 'formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 402:
    manifest['ssc'].append('SSC-133')
    manifest['bugs'].append('BUG-387')
    manifest['ykt'].append('YKT-307')
    manifest['testIds'].append('ISSRET001..008')
    manifest['limitations'] = ['same-source actual BACKUP_RETENTION and five-frame return pending', 'ten steps/full proof/publication/A handoff/API/Web/CHR incomplete', 'native fresh retention/negatives/hard-timeout and coverage100 pending', 'formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 403:
    manifest['ssc'].extend(['SSC-134', 'SSC-135'])
    manifest['bugs'].append('BUG-388')
    manifest['ykt'].append('YKT-308')
    manifest['testIds'].extend(['ISSCOMP001..010', 'ISSSTEP004..007'])
    manifest['limitations'] = ['same-source native ten actual steps/five gate frames and stopped GC proof pending', 'regular issuer/full proofs/revoke/A handoff/API/Web/CHR incomplete', 'fresh retention/failed Backup/native negatives/hard-timeout and coverage100 pending', 'formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 404:
    manifest['ssc'].append('SSC-136')
    manifest['bugs'].extend(['BUG-389', 'BUG-390', 'BUG-391'])
    manifest['ykt'].extend(['YKT-309', 'YKT-310', 'YKT-311'])
    manifest['testIds'].append('ISSPUB001..008')
    manifest['limitations'] = ['same-source actual regular issuer/three proofs/after-A commit pending', 'Root full admission/same-parent launch/same-PID exec/API/Web/CHR incomplete', 'fresh retention/failed Backup/native negatives/hard-timeout and coverage100 pending', 'formal PT-WEB-20260925-24 unchanged']
if int(identifier[2:5]) >= 405:
    manifest['bugs'].append('BUG-393')
    manifest['ykt'].append('YKT-313')
    manifest['testIds'].append('ISSPUB009')
if int(identifier[2:5]) >= 406:
    manifest['ssc'].extend(f'SSC-{n:03d}' for n in range(137, 143))
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(395, 403))
    manifest['ykt'].extend(f'YKT-{n:03d}' for n in range(315, 323))
    manifest['testIds'].extend(['ROOTLAUNCH001..006', 'ROOTELF001..006', 'ROOTPROOF001..004',
                               'ROOTTICKET001..004', 'ROOTUNIT001', 'ROOTOWNERFD001..002'])
    manifest['limitations'] = [
        'same-source native Root actual gates/launch/held ELF/same-PID privilege transition pending',
        'API/Web ordinary ready, completed Morning receipt, CHR-A01/L01 pending',
        'FAILED cleanup classification BUG392, UNKNOWN/hard-timeout/native negative closure pending',
        '100% coverage and formal PT-WEB-20260925-24 unchanged',
    ]
if int(identifier[2:5]) >= 407:
    manifest['ssc'].extend(['SSC-143', 'SSC-144'])
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(403, 409))
    manifest['ykt'].extend(f'YKT-{n:03d}' for n in range(323, 327))
    manifest['testIds'].extend(['ROOTSELECTOR001', 'ROOTREC001..005'])
    manifest['limitations'] = [
        'same-source native strict failed-generation recovery and Root selector admission pending',
        'API/Web ordinary ready, completed Morning receipt, CHR-A01/L01 pending',
        'FAILED cleanup classification BUG392, UNKNOWN/hard-timeout/native negative closure pending',
        '100% coverage and formal PT-WEB-20260925-24 unchanged',
    ]
if int(identifier[2:5]) >= 408:
    manifest['ssc'].append('SSC-145')
    manifest['bugs'].extend(['BUG-409', 'BUG-410'])
    manifest['ykt'].append('YKT-327')
    manifest['testIds'].extend(['ROOTREC006', 'ROOTREC007'])
if int(identifier[2:5]) >= 412:
    manifest['ssc'].extend(['SSC-149', 'SSC-150'])
    manifest['bugs'].extend(['BUG-416', 'BUG-417', 'BUG-418', 'BUG-419'])
    manifest['ykt'].append('YKT-331')
    manifest['testIds'].extend(['PT-JMS-DISPATCH-026-A..F', 'PT-OPS-API-KEY-001..006',
        'PT-OPS-API-PREP-001..004', 'PT-AUT-LOGOUT-ASSEMBLY-001..003',
        'PT-MED-ASSEMBLY-001..003', 'PT-ADM-ASSEMBLY-001..003', 'PT-OPS-API-CFG-007'])
    manifest['limitations'] = ['Ordinary API24/31 real registration only; Question7/async/outbox/Web lifecycle incomplete',
        'Host retained-FD component and real PostgreSQL factory tests do not prove native Root/full ready',
        'Current VM still signed PG408/source32c6a7b1e; PG410 old-source exit50 is not mixed into this source coverage',
        'API/Web ordinary ready, completed Morning receipt, CHR-A01/L01 pending',
        '100% coverage and formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 413:
    manifest['bugs'].extend(['BUG-420', 'BUG-424'])
    manifest['ykt'].append('YKT-335')
    manifest['testIds'].extend(['ROOTCFG002', 'ISSUERCFG002'])
    manifest['command'] = 'six modules: clean test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar dependency-plugin3.9.0:copy-dependencies/list runtime -o; verified Node24.19.0 PATH'
if int(identifier[2:5]) >= 415:
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(421, 431) if n != 424)
    manifest['ssc'].extend(['SSC-151', 'SSC-152', 'SSC-153'])
    manifest['ykt'].extend(['YKT-332', 'YKT-333', 'YKT-334', 'YKT-336', 'YKT-337', 'YKT-338'])
    manifest['testIds'].extend(['PT-JMS-QSB-A-API', 'PT-JMS-QSB-A-WEB-SEND',
        'PT-JMS-QSB-A-WEB-REPLY', 'PT-JMS-EVENT-DELIVERY', 'PT-QST-STATE-001..003'])
    manifest['ddl'] = {'versionedMigrations': 24, 'appendOnly': 'V024 notification RECEIVED state',
        'v003Sha256': '85f05cda30be1dd7856fb1eee3b25f42c6513641ab5d30b92410210f5460aa5e',
        'legacyMismatch': 'V024 transaction fails without guessed job state', 'nativeMigration': 'not deployed'}
    manifest['command'] += '; outputFile=target/runtime-dependencies.txt appendOutput=false'
if int(identifier[2:5]) >= 417:
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(431, 437))
    manifest['ssc'].append('SSC-155')
    manifest['ykt'].extend(['YKT-339', 'YKT-340'])
    manifest['testIds'].extend(['PT-QST-DLQ-MODEL', 'PT-QST-DLQ-DB', 'PT-QST-DLQ-JMS'])
    manifest['ddl'].update({'versionedMigrations': 25,
        'appendOnly': 'V024 notification state; V025 immutable Question DLQ profile',
        'legacyDlq': 'migration refuses missing original metadata; no inferred repair'})
if int(identifier[2:5]) >= 419:
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(437, 447))
    manifest['ykt'].extend(['YKT-341', 'YKT-342', 'YKT-343'])
    manifest['testIds'].extend(['ASUB001..007', 'OUTBOX001..004'])
    manifest['limitations'].append('Question acceptance/owned Outbox exercised with real PostgreSQL18 and embedded Artemis; Worker/read/cancel/delete and third consumer not assembled')
if int(identifier[2:5]) >= 420:
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(447, 457) if n != 453)
    manifest['ssc'].append('SSC-156')
    manifest['ykt'].extend(['YKT-344', 'YKT-345', 'YKT-346'])
    manifest['testIds'].extend(['AWORK001..013'])
    manifest['limitations'].append('Real host PG18/Artemis Worker completion and fourth-rollback two physical DLQ copies exercised; hard process/connection-loss/native lifecycle and read/cancel/delete/31-handler registration remain pending')
    manifest['toolOnlyBug'] = 'BUG-453: Work usage allowlist/de-dup, not Production PT numerator'
if int(identifier[2:5]) >= 421:
    manifest['ssc'].extend(['SSC-157', 'SSC-158'])
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(457, 508))
    manifest['ykt'].extend(f'YKT-{n:03d}' for n in range(347, 367))
    manifest['testIds'].extend(['QRY001..048', 'NTF001..016', 'PT-JMS-CORE001..008',
        'PT-OPS-API-READY001..008', 'PT-OPS-RELEASE009', 'PT-OPS-STARTADMIT009', 'OUTBOX005'])
    manifest['limitations'] = [
        'All31 request processors and three factory profiles/six consumers wired in admitted API Main; native readiness not accepted',
        'Real host PostgreSQL18/Artemis query/mutation/acceptance/Worker/replay exercised; current-role and immutable Inbox guards retained',
        'Management and lifetime component HTTP/TERM do not substitute for native Root admission, actual Morning completion or CHR',
        'VM remains signed PG408/source32c6a7b1e; old182 rows/Backup/INVALID/intents retained, new migration and signed deployment pending',
        'New lifecycle/fatal contract remaining host/native coverage explicitly pending; no exclusion or synthetic Main invocation',
        '100% coverage/full scope/formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 424:
    manifest['ssc'].append('SSC-161')
    manifest['testIds'].extend(['READY004-CLOSED', 'MAIN003', 'NATIVEPHASE-001'])
    manifest['limitations'] = [
        'Full31 API assembly and true Root-to-same-PID exec observed; actual readiness and whole Morning remain unaccepted',
        'VM signed PG424/sourcefa30 diagnostic actual ordinary API reached TRANSFER then normal exit50; no UP',
        'Old failed captured generations physically retired only after full private preservation, not historical close/phase success',
        'Web actual assembly, ordinary native coverage, CHR, full coverage/formal scope remain pending',
        'Formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 425:
    manifest['ssc'].append('SSC-162')
    manifest['bugs'].append('BUG-519')
    manifest['ykt'].append('YKT-373')
    manifest['testIds'].extend(['A06-MOUNT001', 'A06-MOUNT002'])
    manifest['toolOnlyBugs'] = ['BUG-520: stale M2 when API-only selected command',
        'BUG-521: operator compile/runtime classpath; not Production PT numerator']
    manifest['trigger'] = 'Same S3 native Transfer held-mount contract: SSC162/BUG519, readonly/unknown negatives and full six regression before signed candidate'
if int(identifier[2:5]) >= 428:
    manifest['ssc'].append('SSC-164')
    manifest['bugs'].extend(['BUG-523', 'BUG-524', 'BUG-525', 'BUG-526'])
    manifest['ykt'].append('YKT-375')
    manifest['testIds'].extend(['READY428001..012', 'ROOTCTX-ORDINARY-GENERATION-DEADLINE'])
    manifest['trigger'] = 'SSC164 same captured Root-to-ordinary readiness and API-to-Web owned sequence: source-frozen full six regression before signed native candidate'
    manifest['limitations'] = [
        'Selected 60PT preceded this full run; neither is actual parent/API/Web native acceptance',
        'Prior PG427 API200/owned TERM uses sourcea3c86daf, not this source; no cross-source coverage/result reuse',
        'API-to-Web parent connection is implemented; Web business assembly, Caddy, held original DONE and intent retirement remain pending',
        'New VM boot requires fresh observations; old PID/Invocation and terminal receipts are historical only',
        'Native ordinary coverage, CHR-A01/L01 and full scope coverage100 remain pending',
        'Formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 429:
    manifest['ssc'].extend(['SSC-165', 'SSC-166'])
    manifest['bugs'].extend(['BUG-527', 'BUG-531', 'BUG-532', 'BUG-533', 'BUG-534', 'BUG-535'])
    manifest['ykt'].extend(['YKT-376', 'YKT-377', 'YKT-378', 'YKT-379'])
    manifest['testIds'].extend(['ISSCOLD001..007', 'MAINTENANCE-TMPFILES-FIXED-NAMESPACE'])
    manifest['trigger'] = 'SSC165/166 same cold-boot owner/STOP_SET/fresh Broker intent contract: full six frozen-source regression before signed ordinary parent candidate'
    manifest['limitations'] = [
        'PG428/source352 full2891 is historical and not reused for this changed source',
        'Actual same-source NoPrior/fresh Broker and issuer/API/Web parent observation pending',
        'Web full business assembly, Caddy, held original DONE and normal intent retirement remain pending',
        'Native ordinary coverage, CHR-A01/L01 and full scope coverage100 remain pending',
        'Formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 430:
    manifest['ssc'].append('SSC-167')
    manifest['bugs'].append('BUG-536')
    manifest['ykt'].append('YKT-380')
    manifest['testIds'].extend(['FULLBOM010', 'ISSCOLD008'])
    manifest['trigger'] = 'SSC167 fixed signed boot-config payload path and same cold-owner oracle boundary closure: full shared six regression before new signed native candidate'
    manifest['limitations'].insert(0, 'PG429/sourcec3 full2898 is preserved; PG429 signed signature passed but full BOM refused tmpfiles layout; current/approval/permits were unchanged')
if int(identifier[2:5]) >= 431:
    manifest['ssc'].append('SSC-168')
    manifest['bugs'].extend(['BUG-539', 'BUG-540', 'BUG-541', 'BUG-542'])
    manifest['ykt'].extend(['YKT-383', 'YKT-384', 'YKT-385', 'YKT-386'])
    manifest['testIds'].extend(['ROOTPAIR001..010'])
    manifest['trigger'] = 'SSC168 fixed same-owner two-child failure recovery/quarantine contract: frozen six-module full regression before typed PG430 native retirement and next Web assembly'
    manifest['limitations'] = ['PG430/source91 parent API200/Root-ordinary Web50 is historical, not reused as new-source acceptance',
        'PG430 old-generation typed pair native retirement must be independently preserved/verified',
        'Web full business assembly/Caddy/original DONE/normal retirement/real CHR-A01/L01 remain pending',
        'Native positive coverage and full-scope 100% formal acceptance remain pending',
        'Formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 432:
    manifest['bugs'].append('BUG-543')
    manifest['ykt'].append('YKT-387')
    manifest['trigger'] = 'BUG543 fixed same-M/A candidate host-read-only preparation before Pair native retirement: new frozen source six regression; source329 results retained but not reused'
    manifest['limitations'].insert(0, 'PG431/source329 signed candidate placement only; missing host-RO preflight detected before native recovery, no intent/current change')
if int(identifier[2:5]) >= 433:
    manifest['bugs'].extend(['BUG-545', 'BUG-546'])
    manifest['ykt'].extend(['YKT-389', 'YKT-390'])
    manifest['testIds'].append('PT-WEB-S3WIRE001..008')
    manifest['trigger'] = 'PG-D342 shared protected wire interaction and eighteen fixed Web request capabilities: frozen six-module full security regression after independent byte/vector PT'
    manifest['limitations'] = [
        'PG432/source d90 full2909 and dirty selected72 are preserved, not reused as this source full acceptance',
        'PG432 native Pair operator is UNKNOWN with M/A held after obsolete empty-Transfer fixture refusal; QA047 pending; no native success or historical close inferred',
        'Five fixed Web wire facades do not prove full HTTP business assembly or ordinary native readiness',
        'Caddy/original DONE/normal retirement/real CHR-A01/L01/native coverage/full-scope 100% remain pending',
        'Formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged']
if int(identifier[2:5]) >= 434:
    manifest['bugs'].extend(['BUG-547', 'BUG-548', 'BUG-549', 'BUG-550', 'BUG-551', 'BUG-552'])
    manifest['ykt'].extend(['YKT-391', 'YKT-392', 'YKT-393', 'YKT-394', 'YKT-395', 'YKT-396'])
    manifest['testIds'].extend(['PT-MED-HTTP001..010', 'PT-WEB-DBFIX001..003'])
    manifest['trigger'] = 'PG-D343 fixed five media GET/HEAD/controller/descriptor binding and local audit contract plus test-only DB setup ownership: fresh source-frozen six-module security regression'
    media_names = {'MediaController', 'MediaController$ServletResponse', 'MediaController$ServletResponse$1',
        'WebMediaAudit', 'WebMediaAudit$Failure', 'MediaMvcConfiguration', 'MediaResponseDecoder',
        'MediaResponseDecoder$Binding', 'MediaResponseDecoder$Result'}
    media = {}
    for cls in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class'):
        short = cls.get('name').split('/')[-1]
        if short in media_names:
            media[short] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))}
                for c in cls.findall('counter')}
    assert set(media) == media_names
    assert all(c['missed'] == 0 for counters in media.values() for c in counters.values())
    manifest['mediaScopeCoverage'] = media
    manifest['limitations'] = [
        'PG433 source8bead full2917 and PG434 dirty selected74/77 are preserved, not reused as this source full acceptance',
        'PG432 native Pair operator remains UNKNOWN/M-A held; QA047 pending, no stop/deploy/start repeated',
        'Receipt reference fourth technical table proposed in QA048/UIC007/SSC169; no unapproved schema/oracle change',
        'Owned native FileSource/full Web business assembly/Caddy/original DONE/normal retirement/real CHR-A01/L01 remain pending',
        'Full-scope/native coverage100 and formal PT-WEB-20260925-24/1964PT/53scope/48.3% remain unchanged']
if int(identifier[2:5]) >= 435:
    manifest['bugs'].extend(['BUG-553', 'BUG-554', 'BUG-555'])
    manifest['ykt'].extend(['YKT-397', 'YKT-398', 'YKT-399'])
    manifest['testIds'].append('PT-USER-HTTP001..010')
    manifest['trigger'] = 'PG-D344 ADMIN SCR015 fixed HTTP/HEAD query/form/PAGED48/C-byte ordered rows/template, common MVC view allowlist and immutable snapshot: source-frozen six-module regression'
    names = {'UserSearchForm', 'UserListViewModel', 'UserListViewModel$Row', 'UserAdminController', 'UserMvcConfiguration'}
    user_coverage = {c.get('name').split('/')[-1]: {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').split('/')[-1] in names}
    assert set(user_coverage) == names
    assert all(k['missed'] == 0 for value in user_coverage.values() for k in value.values())
    manifest['userListScopeCoverage'] = user_coverage
    manifest['limitations'].extend([
        'PG434 source7caaa full2930 and PG435 dirty selected108 are preserved, not reused as this source full acceptance',
        'SCR015 User list HTTP is connected; detail/create/mutation screens and full ordinary Web business ready remain pending'])
if int(identifier[2:5]) >= 436:
    manifest['bugs'].extend(['BUG-557', 'BUG-558', 'BUG-559'])
    manifest['ykt'].extend(['YKT-401', 'YKT-402', 'YKT-403'])
    manifest['testIds'].extend(['PT-USER-CREATE001..008', 'PT-USER-DETAIL001..008'])
    manifest['trigger'] = 'PG-D345/346 User creation input and ADMIN SCR017 reference, common MVC template allowlist, immutable safe projection: source-frozen six-module regression'
    names = {'UserCreateForm', 'UserDetailViewModel', 'UserAdminController'}
    detail_coverage = {c.get('name').split('/')[-1]: {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').split('/')[-1] in names}
    assert set(detail_coverage) == names
    assert all(k['missed'] == 0 for value in detail_coverage.values() for k in value.values())
    manifest['userCreateDetailScopeCoverage'] = detail_coverage
    manifest['limitations'] = [
        'PG435 sourcefe4ea full2940 and PG436 selected83/91 are preserved, not mixed into this fresh source full regression',
        'User list/detail GET/HEAD and creation input connected; create GET/POST and User mutation forms/controllers remain incomplete',
        'QA047 fixed native owner remains UNKNOWN/M-A held; no repeated stop/deploy/start',
        'QA048 receipt reference and QA049 completed-token retention are unapproved; no proposed schema/session JSON/oracle mutation',
        'Full ordinary Web business ready/Caddy/original DONE/normal intent retirement/real CHR-A01/L01/native100 remain pending',
        'Full formal scope/100percent and PT-WEB-20260925-24/1964PT/53scope/48.3% remain unchanged']
if int(identifier[2:5]) >= 437:
    manifest['bugs'].extend(['BUG-560', 'BUG-561'])
    manifest['ykt'].extend(['YKT-404', 'YKT-405'])
    manifest['testIds'].extend(['PT-NTF-HTTP001..010', 'PT-WEB-050..053', 'PT-WEB-CSRF054'])
    manifest['trigger'] = 'PG-D347/348 Notification owner-only HTTP/query/DOM and CSRF rotation postconditions, common MVC/CSS/security: source-frozen six-module regression'
    names = {'NotificationSearchForm', 'NotificationListViewModel', 'NotificationController', 'NotificationMvcConfiguration', 'EncryptedSessionCsrfTokenRepository'}
    notification_coverage = {c.get('name').split('/')[-1]: {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').split('/')[-1] in names}
    assert set(notification_coverage) == names
    assert all(k['missed'] == 0 for value in notification_coverage.values() for k in value.values())
    manifest['notificationSecurityScopeCoverage'] = notification_coverage
    manifest['limitations'].extend([
        'PG436 source22b95 full2956 and PG437 selected WIP results are not reused as this fresh source full acceptance',
        'SCR020 Notification GET/HEAD is connected; SCR021 detail/cancel and full business/native Web assembly remain incomplete'])
if int(identifier[2:5]) >= 438:
    manifest['bugs'].extend(['BUG-562', 'BUG-563', 'BUG-564', 'BUG-565', 'BUG-567'])
    manifest['ykt'].extend(['YKT-406', 'YKT-407', 'YKT-408', 'YKT-409', 'YKT-410'])
    manifest['testIds'].extend(['PT-NTF-DETAIL001..008', 'deletedNotificationNeverContainsAnswer', 'PT-OPS-EVIDENCE-GIT001', 'PT-DB-INBOX-161..168'])
    manifest['trigger'] = 'PG-D349 SCR021 reference and deleted-answer typed semantic rejection, common protocol/MVC/CSS and evidence tooling corrections: source-frozen six-module regression'
    web = ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml')
    detail = next(c for c in web.findall('.//class') if c.get('name').endswith('/NotificationDetailViewModel'))
    manifest['notificationDetailCoverage'] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in detail.findall('counter')}
    assert all(c['missed'] == 0 for c in manifest['notificationDetailCoverage'].values())
    protocol = ET.parse(root / 'src/schubert-nk-protocol/target/site/jacoco/jacoco.xml')
    assert all(int(c.get('missed')) == 0 for c in protocol.getroot().findall('counter'))
    manifest['limitations'].append('SCR021 reference is connected, cancellation/token/Question forms and full native ordinary Web remain incomplete')
if int(identifier[2:5]) >= 439:
    manifest['bugs'].extend(['BUG-568', 'BUG-569'])
    manifest['ykt'].append('YKT-411')
    manifest['testIds'].extend(['PT-QRY-HTTP001..012'])
    manifest['trigger'] = 'PG-D350 SCR022/023 reference: closed role-aware QSS/QSD HTTP forms, owner and response checks, immutable projection, MVC/templates/CSS: source-frozen six-module regression'
    names = {'QuestionSearchForm', 'QuestionListViewModel', 'QuestionDetailViewModel', 'QuestionController', 'QuestionMvcConfiguration'}
    query_coverage = {c.get('name').split('/')[-1]: {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').split('/')[-1] in names}
    assert set(query_coverage) == names
    assert all(k['missed'] == 0 for value in query_coverage.values() for k in value.values())
    manifest['questionReadScopeCoverage'] = query_coverage
    manifest['limitations'].append('SCR022/023 references connected only; delete and completed-token approval QA049, acceptance receipt QA048, native owner recovery QA047/full ordinary Web ready remain pending')
if int(identifier[2:5]) >= 440:
    manifest['bugs'].append('BUG-570')
    manifest['ykt'].append('YKT-412')
    manifest['testIds'].extend(['PT-QST-FORM001..008', 'PT-QST-JS001-A..H'])
    manifest['trigger'] = 'PG-D351/352 SCR018 closed Question input and independent byte-counter JS: source-frozen six-module regression'
    form_classes = [c for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').endswith('/QuestionSubmitForm')]
    assert len(form_classes) == 1
    form_coverage = {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in form_classes[0].findall('counter')}
    assert all(k['missed'] == 0 for k in form_coverage.values())
    manifest['questionSubmitFormCoverage'] = form_coverage
    jsdir = root / 'src/schubert-nk-web/target/pt-question-script'
    tap = (jsdir / 'node.tap').read_text()
    assert all(line in tap.splitlines() for line in ['# tests 8', '# pass 8', '# fail 0', '# cancelled 0', '# skipped 0', '# todo 0'])
    assert re.search(r'question-input-validation\.js\s*\|\s*100\.00\s*\|\s*100\.00\s*\|\s*100\.00', tap)
    proof = json.loads((jsdir / 'PT-QST-JS001-node.json').read_text())
    assert proof['scriptSha256'] == hashlib.sha256((root / 'src/schubert-nk-web/src/main/resources/static/js/question-input-validation.js').read_bytes()).hexdigest()
    assert proof['subcases'] == 8 and proof['productionFiles'] == 1
    assert proof['testExit'] == proof['syntaxExit'] == proof['failed'] == proof['skipped'] == proof['todo'] == 0
    (out / 'logs').mkdir()
    (out / 'logs/byte-counter.txt').write_text(tap)
    (out / 'logs/byte-counter.json').write_text(json.dumps(proof, indent=2) + '\n')
    manifest['javascript'] = proof
    manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
    manifest['limitations'].append('Question input/byte counter only; token issuance/POST/receipt/template/live Browser/native acceptance remain incomplete')
if int(identifier[2:5]) >= 441:
    manifest['bugs'].extend(['BUG-571', 'BUG-572'])
    manifest['ykt'].append('YKT-413')
    manifest['testIds'].append('PT-USER-CHANGE001..016')
    manifest['trigger'] = 'PG-D353 SCR017 four closed User mutation inputs, password lifetime and independent wire oracles: source-frozen six-module regression'
    names = {'UserMutationInput', 'UserStatusForm', 'UserRoleForm', 'PasswordResetForm', 'UserUnlockForm'}
    mutation_coverage = {c.get('name').split('/')[-1]: {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').split('/')[-1] in names}
    assert set(mutation_coverage) == names
    assert all(k['missed'] == 0 for value in mutation_coverage.values() for k in value.values())
    manifest['userMutationInputCoverage'] = mutation_coverage
    manifest['limitations'].append('User mutation forms only; API self/last-admin/version/revocation remain authoritative; QA047/048/049/050, POST/token/Logout/native full Web ready remain pending')
# PG442 REQUEST proof: this block is also reused by the checked selected-run profile.
if int(identifier[2:5]) >= 442:
    names = {'WebRequestTrace', 'WebRequestTrace$Scope', 'WebRequestLogProducer',
             'HttpRequestLoggingValve', 'WebRequestRouteInterceptor', 'RequestLogMvcConfiguration'}
    request_coverage = {c.get('name').split('/')[-1]: {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class') if c.get('name').split('/')[-1] in names}
    assert set(request_coverage) == names
    assert all(k['missed'] == 0 for value in request_coverage.values() for k in value.values())
    manifest['requestTerminalScopeCoverage'] = request_coverage
    proofdir = root / 'src/schubert-nk-web/target/request-log-proof'
    proofnames = {'REQ010-wire.expected.bin', 'REQ010-wire.actual.bin', 'REQ010-json.expected.json',
                  'REQ010-json.actual.json', 'REQ010-input.json'}
    assert {p.name for p in proofdir.iterdir()} == proofnames
    fixture = json.loads((proofdir / 'REQ010-input.json').read_text())
    assert fixture == {'testId': 'PT-REQ-LOG010', 'clock': '2026-10-03T01:00:00.123987Z',
        'requestUuid': '00000000-0000-0000-0000-000000000001',
        'eventUuid': '00000000-0000-0001-0000-000000000001', 'route': '/login', 'method': 'GET',
        'status': 200, 'elapsedNs': 12999999, 'responseBytes': 3, 'verifiedIp': '203.0.113.7', 'actor': None}
    expected_json = {'timestamp': '2026-10-03T01:00:00.123Z', 'service': 'WEB', 'appVersion': 'pt-1',
        'configVersion': 'cfg-1', 'level': 'INFO', 'category': 'REQUEST', 'action': 'HTTP_REQUEST_COMPLETED',
        'outcome': 'SUCCESS', 'messageId': fixture['eventUuid'], 'correlationId': fixture['eventUuid'],
        'requestId': fixture['requestUuid'], 'message': 'HTTP request completed', 'httpMethod': 'GET',
        'path': '/login', 'status': 200, 'elapsedMs': 12, 'remoteAddress': '203.0.113.7',
        'details': {'responseBytes': 3, 'projectionStatus': 'PENDING'}}
    for kind in ('expected', 'actual'):
        assert json.loads((proofdir / f'REQ010-json.{kind}.json').read_text()) == expected_json
    # Independent UI235 offset/length vector; no Production codec is called here.
    vector = bytearray(b' ' * 2336)
    fields = {0: 'SCHBNK01001WLGEVT01001EI', 24: fixture['eventUuid'], 60: fixture['eventUuid'],
        96: '20261003100000123', 177: '0256002080000000000000000002336',
        256: '20261003100000123', 273: 'REQUEST', 289: 'INFO', 297: 'HTTP_REQUEST_COMPLETED',
        361: 'HTTP request completed', 873: fixture['requestUuid'], 909: 'GET', 917: '/login',
        1173: '200', 1176: '12', 1185: '203.0.113.7',
        1299: '{"responseBytes":3,"projectionStatus":"PENDING"}'}
    for offset, value in fields.items():
        encoded = value.encode('ascii')
        vector[offset:offset + len(encoded)] = encoded
    for kind in ('expected', 'actual'):
        assert (proofdir / f'REQ010-wire.{kind}.bin').read_bytes() == vector
    destination = out / 'request-proof'
    destination.mkdir()
    for name in sorted(proofnames):
        (destination / name).write_bytes((proofdir / name).read_bytes())
    manifest['testIds'].extend(['PT-REQ-LOG001..016'])
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(573, 594))
    manifest['ykt'].extend(f'YKT-{n:03d}' for n in range(414, 419))
    manifest['ssc'].extend(['SSC-172', 'SSC-173'])
    manifest['trigger'] = 'PG-D354/355 REQUEST native terminal, safe identity/actor, encrypted outbox and existing retry/Artemis/API UK: same-source six-module regression'
    manifest['requestProof'] = {'testId': 'PT-REQ-LOG010', 'wireBytes': 2336,
        'oracle': 'UI235 independent byte offsets; literal JSON; independent JCE decrypt; DDL/SQL postconditions',
        'fixture': 'public synthetic only; no key/ciphertext/session/token/runtime user'}
    manifest['limitations'] = [
        'REQUEST native Tomcat component and actual existing replay/Artemis/API path only; full ordinary Production Web assembly is not accepted',
        'QA047/048/049 design approval now recorded; fixed owner recovery, receipt persistence and completed-token implementation/PT remain pending',
        'QA050 Logout expiry/retention remains unapproved; its proposed DDL/API oracle is not implemented',
        'same-source full production Morning/API/Web/Caddy/original DONE/normal intent retirement/native CHR-A01/L01/coverage100 remain pending',
        'root clean verify/full formal scopes and PT-WEB-20260925-24/1964PT/53scope/48.3% remain unchanged']
    manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
# End PG442 REQUEST proof.
if int(identifier[2:5]) >= 446:
    names = {'SessionOperationToken', 'SessionAttributeCodec', 'SessionOperationTokenLifecycle',
             'OperationTokenConflictException', 'SpringWebSession'}
    token_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.get('name').rsplit('/', 1)[-1] in names}
    assert set(token_coverage) == names
    assert all(k['missed'] == 0 for value in token_coverage.values() for k in value.values())
    manifest['operationTokenCoverage'] = token_coverage
    manifest['testIds'].extend(['TOKV201..208'])
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(600, 606))
    manifest['ykt'].extend(['YKT-424', 'YKT-425'])
    manifest['qa'] = ['QA-047', 'QA-048', 'QA-049', 'QA-050']
    manifest['trigger'] = 'PG-D356/QA049 session JSON v2 legacy strict read, current-row token lifecycle and Spring delta: fresh source-frozen full-six regression'
    manifest['limitations'] = [
        'QA047..050 are approved; no repeated approval request or stale QA050-unapproved classification',
        'Host token data/short transaction/retirement/delta tests only; genuine business POST reply verification and receipt/Logout/Web assembly remain pending',
        'current PG444 cold boot native acceptance applies only to fcc source; future diagnostics and new token source not native accepted',
        'source-identical ordinary Morning/API/Web/Caddy/original DONE/intent retirement/native CHR-A01/L01 and native coverage100/formal recognition remain pending',
        'interrupted PG442 exit143 and other-source PG441/PG443 success not reused as this full-run result',
    ]
if int(identifier[2:5]) >= 447:
    names = {'ReceiptReference', 'ReceiptReferenceRepository', 'ReceiptReferenceException'}
    receipt_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.get('name').rsplit('/', 1)[-1] in names}
    assert set(receipt_coverage) == names
    assert all(k['missed'] == 0 for value in receipt_coverage.values() for k in value.values())
    manifest['receiptReferenceCoverage'] = receipt_coverage
    manifest['ddl'].update({'versionedMigrations': 26,
        'appendOnly': 'V001..025 unchanged; V026 QA048 technical three-value locator and SSC175 atomic shared cleanup',
        'receiptOracle': '075 RCPT001..005: literal SQL, independent role/catalog, physical orphan, bounded/locked/backup/run/rollback and fault matrix'})
    manifest['testIds'].extend(['RCPT001..005', 'RCPT006A..H'])
    manifest['bugs'].extend('BUG-' + str(n) for n in range(608, 618))
    manifest['bugs'].extend(['BUG-619', 'BUG-620'])
    manifest['ykt'].extend('YKT-' + str(n) for n in range(428, 437))
    manifest['ykt'].append('YKT-438')
    manifest['testIds'].append('REQ004 receipt safe registered pattern, actual27methods/25unique and CSS-JS2, raw locator/query rejection')
    manifest['ssc'].append('SSC-175')
    names = {'QuestionController', 'QuestionSubmitViewModel', 'QuestionAcceptedViewModel',
             'QuestionAcceptanceMvcConfiguration', 'QuestionSubmitForm', 'QuestionDetailViewModel'}
    http_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.get('name').rsplit('/', 1)[-1] in names}
    assert set(http_coverage) == names
    assert all(k['missed'] == 0 for value in http_coverage.values() for k in value.values())
    manifest['receiptHttpCoverage'] = http_coverage
    manifest['receiptHttpOracle'] = '075 RCPT006A..H: independent QSB4400/320, QSD268/8608; immutable current SQL, real security HTTP302/CSRF403/API0 and DOM200-codepoint escape; same-token unknown/lost-response replay, owner/tuple/100 concurrent and per-request DB release'
    manifest['trigger'] = 'PG-D357/QA048049/SSC175 receipt ownership group: V026 immutable locator/atomic shared cleanup, inventory propagation and retained-token POST/fresh IF030 receipt HTTP: fresh full-six regression'
    manifest['limitations'] = [
        'Host receipt SQL/JDBC and real embedded secured HTTP only; full native ordinary Web assembly is not accepted',
        'QA050 nullable pending revocation/retry/API expired fence and remaining business POST wiring not yet implemented',
        'V026 native signed migration and new schema Backup/restore not yet executed; old successful bundles remain immutable',
        'ordinary Morning/API/full Web/Caddy/DONE/intent/native CHR-A01/L01 and native coverage100/formal acceptance pending',
        'formal PT-WEB-20260925-24/source858713c0/1964PT/53scope/48.3% unchanged; failed/partial/other-source results not reused',
    ]
if int(identifier[2:5]) >= 448:
    names = {'AuthSessionRevocationService', 'LogoutInboxService', 'AuthenticationContextVerifier'}
    fence_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-api/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.get('name').rsplit('/', 1)[-1] in names}
    assert set(fence_coverage) == names
    assert all(k['missed'] == 0 for value in fence_coverage.values() for k in value.values())
    manifest['logoutFenceCoverage'] = fence_coverage
    manifest['bugs'].append('BUG-618')
    manifest['ykt'].append('YKT-437')
    manifest['ssc'].append('SSC-171')
    manifest['testIds'].append('RERUN001-A..E')
    manifest['trigger'] = 'PG-D358/QA050/SSC171: lock-current Logout Clock, atomic EXPIRED fence/audit/Inbox ERROR, immutable replay and TOUCH/delayed-verifier competition: security ownership full-six regression'
    manifest['limitations'] = [
        'API expired fence host regression only; QA050 nullable pending row/15-minute retry/revoke key retention/local destruction and full Web assembly remain pending',
        'V026 native signed migration/Backup, ordinary Morning/API/full Web/Caddy/DONE/intent/native CHR-A01/L01 and native coverage100/formal acceptance pending',
        'formal PT-WEB-20260925-24/source858713c0/1964PT/53scope/48.3% unchanged; failed/partial/other-source results not reused',
    ]
if int(identifier[2:5]) >= 449:
    names = {'AuthenticationInfrastructureException', 'AuthSessionRevocationService', 'AuthSessionService',
             'AuthenticationContextVerifier', 'AdminCommandAuthenticator', 'LogoutInboxService'}
    auth_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-api/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.get('name').rsplit('/', 1)[-1] in names}
    assert set(auth_coverage) == names
    assert all(k['missed'] == 0 for value in auth_coverage.values() for k in value.values())
    manifest['authFatalCoverage'] = auth_coverage
    revoke_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.get('name').startswith('dev/codex/schubert/nk/web/revocation/') and c.findall('counter')}
    assert len(revoke_coverage) == (15 if int(identifier[2:5]) >= 450 else 11)
    assert all(k['missed'] == 0 for value in revoke_coverage.values() for k in value.values())
    manifest['revokeCoverage'] = revoke_coverage
    manifest['ddl'].update({'versionedMigrations': 27,
        'appendOnly': 'V001..026 unchanged; V027 only removes pending expires_at NOT NULL; no expiry deletion proof'})
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in range(622, 628))
    manifest['ykt'].extend(f'YKT-{n:03d}' for n in range(440, 445))
    manifest['testIds'].extend(['RERUN001-F', 'RERUN002', 'RERUN003A..G', 'RERUN004A..I', 'RERUN005A..H'])
    manifest['trigger'] = 'PG-D359..361/QA050 ownership group: fatal preservation, V027 and inventory, dedicated encrypted revoke, SQL lease/backoff/retention and genuine Logout facade/API participants; fresh six-module regression'
    manifest['limitations'] = [
        'Host genuine facade/API/isolated PostgreSQL and independent JMS fixture only; actual Artemis/native Web not accepted',
        'Local Logout atomic destruction/enqueue, retry worker shutdown, old key retention and full native assembly pending',
        'V027 signed native migration/Backup/ordinary Morning/API/Web/Caddy/DONE/intent/CHR-A01/L01/native coverage100 pending',
        'Formal PT-WEB-20260925-24/source858713c0/1964PT/53scope/48.3% unchanged; no interrupted/other-source result reuse',
    ]
if int(identifier[2:5]) >= 450:
    names = {'JdbcWebSessionStore', 'SessionStoreException', 'EncryptedWebSessionRepository',
             'LocalLogoutHandler', 'LogoutController', 'LogoutMvcConfiguration',
             'WebLogApplicationRuntime', 'WebHttpServer', 'WebNativeCodecs', 'WebNativeCodecs$1',
             'WebLogReplayWorker', 'WebLogReplayWorker$Snapshot'}
    owned_coverage = {c.get('name').rsplit('/', 1)[-1]:
        {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))}
         for k in c.findall('counter')}
        for c in ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').findall('.//class')
        if c.findall('counter') and
        (c.get('name').startswith('dev/codex/schubert/nk/web/revocation/') or
         c.get('name').rsplit('/', 1)[-1] in names or
         c.get('name').rsplit('/', 1)[-1].startswith(('WebSecurityAudit', 'WebRequestTrace')))}
    assert len(owned_coverage) == 32
    assert all(k['missed'] == 0 for value in owned_coverage.values() for k in value.values())
    manifest['logoutOwnedCoverage'] = owned_coverage
    manifest['bugs'].extend(f'BUG-{n:03d}' for n in (628, 630, 631, 632, 633, 634))
    manifest['ykt'].extend(f'YKT-{n:03d}' for n in (445, 447, 448, 449))
    manifest['testIds'].extend(['RERUN006A..H', 'RERUN007A..H', 'RERUN008A..E', 'NKEY005',
                              'REQUEST actual valve', 'Log repeated UNKNOWN join/hidden fatal',
                              'Runtime confirmed phases/HTTP stop-destroy phases'])
    manifest['trigger'] = 'PG-D362..364/QA050: atomic local destruction and durable retained retry, real Logout HTTP/security/closed audit, actual workers join/confirmed stop phases/current third key; fresh six-module ownership regression'
    manifest['limitations'] = [
        'Host genuine facade/API/isolated PostgreSQL and independent JMS fixture only; actual Artemis/native Web not accepted',
        'BUG629/YKT446 remain open for legacy startPath/closeAfterFailure and native outer callback UNKNOWN retention; no final stop receipt from requested stop',
        'Mandatory business routes and full native resource graph/management/owner A release remain pending',
        'V027 signed native migration/Backup/ordinary Morning/API/Web/Caddy/DONE/intent/CHR-A01/L01/native coverage100 pending',
        'Formal PT-WEB-20260925-24/source858713c0/1964PT/53scope/48.3% unchanged; no interrupted/other-source result reuse',
    ]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'source': source, 'tests': manifest['tests'], 'coverage': coverage, 'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest()}))
