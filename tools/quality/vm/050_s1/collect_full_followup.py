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
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'source': source, 'tests': manifest['tests'], 'coverage': coverage, 'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest()}))
