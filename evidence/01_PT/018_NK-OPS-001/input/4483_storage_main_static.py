"""Full unchanged PMD/SpotBugs rules on the actual Storage Main compile; no tests."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET

r = Path.cwd(); tc = r.parent / 'toolchain'
b = r / 'evidence/01_PT/018_NK-OPS-001/evidence'
prepared = b / 'PG36820-storage-main-compile-v1/manifest.json'
m = json.loads(prepared.read_text()); assert m['actualExit'] == 0
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
work = Path(m['cwd']); classes = work / 'src/schubert-nk-storage/target/classes'
assert {str(p.relative_to(classes)): sha(p) for p in classes.rglob('*.class')} == m['physicalClassHashes']
assert all(sha(r / p) == h == sha(work / p) for p, h in m['inputHashes'].items())
out = b / 'PG36822-storage-main-full-static-v1'; assert not out.exists(); out.mkdir()
source_list = out / 'sources.txt'
main = sorted(p for p in m['inputHashes'] if p.endswith('.java')); assert len(main) == 25
source_list.write_text(''.join(str(r / p) + '\n' for p in main))
sg = tc / 'static-gates-20261015'
libs = [sg / 'record-fix-v1/pmd-record-1298.jar', *sorted((sg / 'pmd-bin-7.28.0/lib').glob('*.jar'))]
rules = r / 'tools/quality/static/pmd.xml'
assert rules.read_bytes() == subprocess.check_output(['git', 'show',
    '1634e3884a7b645f50b3552642ed4a1844736ab5:tools/quality/static/pmd.xml'])
ann = tc / 'm2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'
commands = {
 'pmd': [str(tc / 'jdk-25.0.4/bin/java'), '-cp', ':'.join(map(str, libs)),
  'net.sourceforge.pmd.cli.PmdCli', 'check', '--file-list', str(source_list),
  '--rulesets', str(rules), '--use-version', 'java-25', '--aux-classpath',
  ':'.join(map(str, [tc / 'jdk-25.0.4/lib/jrt-fs.jar', classes, ann])),
  '--no-cache', '--format', 'xml', '--report-file', str(out / 'pmd.xml')],
 'spotbugs': [str(tc / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
  '-o', '-B', '-ntp', '-Dmaven.repo.local=' + str(tc / 'm2/repository'),
  '-pl', 'src/schubert-nk-storage',
  'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']}
env = {'PATH': str(tc / 'jdk-25.0.4/bin') + ':/usr/bin:/bin',
 'JAVA_HOME': str(tc / 'jdk-25.0.4'), 'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8'}
def run(name):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
        try:
            result = subprocess.run(commands[name], cwd=work, env=env, stdout=stdout,
                                    stderr=stderr, timeout=180)
            exit_code = result.returncode; timed_out = False
        except subprocess.TimeoutExpired:
            exit_code = 124; timed_out = True
    return dict(command=commands[name], actualExit=exit_code, timedOut=timed_out,
      startAtUTC=start, terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      stdoutSha256=sha(out / (name + '.stdout.log')), stderrSha256=sha(out / (name + '.stderr.log')))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    stages = dict(zip(commands, executor.map(run, commands)))
sb_file = work / 'src/schubert-nk-storage/target/spotbugsXml.xml'
if sb_file.exists(): (out / 'spotbugs.xml').write_bytes(sb_file.read_bytes())
summary = {}; findings = []; errors = []
if (out / 'pmd.xml').exists():
    root = ET.parse(out / 'pmd.xml').getroot()
    for node in root.iter():
        tag = node.tag.rpartition('}')[2]
        if tag in ['error', 'configerror']: errors.append(dict(node.attrib))
        if tag == 'file':
            for item in node:
                if item.tag.rpartition('}')[2] == 'violation':
                    findings.append(dict(path=str(Path(node.get('name')).relative_to(r)),
                      **item.attrib, message=(item.text or '').strip()))
    summary['pmd'] = dict(rawFindings=len(findings), processingErrors=errors)
if (out / 'spotbugs.xml').exists():
    root = ET.parse(out / 'spotbugs.xml').getroot()
    summary['spotbugs'] = dict(bugs=len(root.findall('.//BugInstance')),
      missingClasses=[n.text for n in root.findall('.//MissingClass')],
      errors=[n.attrib for n in root.findall('.//Error')],
      classStats=sorted(n.get('class') for n in root.findall('.//ClassStats')))
assert all(sha(r / p) == h == sha(work / p) for p, h in m['inputHashes'].items())
assert {str(p.relative_to(classes)): sha(p) for p in classes.rglob('*.class')} == m['physicalClassHashes']
assert not list(work.rglob('surefire-reports'))
(out / 'raw-findings.json').open('x').write(json.dumps(findings, indent=2) + '\n')
result = dict(actualExit=0 if len(summary)==2 and not any(x['timedOut'] for x in stages.values()) else 1,
 sourceCore=m['sourceCore'], prepare=dict(path=str(prepared.relative_to(r)), sha256=sha(prepared)),
 stages=stages, summary=summary, fullRulesetSha256=sha(rules),
 toolHashes={str(p): sha(p) for p in [*libs, ann]}, inputHashes=m['inputHashes'],
 terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 productTestsExecuted=0, actualNativeDbVmServiceActions=0, heldClassfileActions=0,
 rawFindingCollectionIsNotQualityPass=True, formalUpdated=False, newAcceptance=0)
(out / 'manifest.json').open('x').write(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(actualExit=result['actualExit'], stages={k:v['actualExit'] for k,v in stages.items()},
 pmdFindings=len(findings), pmdErrors=len(errors), spotbugs=summary.get('spotbugs'))))
