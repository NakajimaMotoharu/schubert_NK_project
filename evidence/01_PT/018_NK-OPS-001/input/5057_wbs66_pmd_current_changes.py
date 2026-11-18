"""F03/451 full PMD policy on current, explicitly changed, approved Main files."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path.cwd()
E = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
OUT = E / 'PG38768-f03-twelve-current-main-pmd-v1'
BUILD = E / 'PG38760-wbs66-four-own-main-current-v1/compile/manifest.json'
TOOLCHAIN = ROOT.parent / 'toolchain'
JDK = TOOLCHAIN / 'jdk-25.0.4'
SETTINGS = ROOT / 'tools/quality/static/pmd.xml'
STAGE = TOOLCHAIN / 'static-gates-20261015'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def saved(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def write(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    begin = json.loads(BUILD.read_text())
    changed = begin['changedSources']
    work = Path(begin['cwd'])
    assert begin['actualExit'] == 0 and len(changed) == 12 and begin['inputHashesReverified']
    assert set(OUT.iterdir()) == {OUT / 'quota-start.json'}
    assert all('/src/main/java/' in p and 'Root' not in Path(p).name for p in changed)
    assert all(sha(ROOT / p) == sha(work / p) == begin['sourceInputs'][p] for p in changed)
    old = subprocess.check_output(['git', 'show', '1634e3884a7b645f50b3552642ed4a1844736ab5:tools/quality/static/pmd.xml'])
    assert hashlib.sha256(old).hexdigest() == sha(SETTINGS)
    listing = OUT / 'sources.txt'
    listing.write_text(''.join(str(work / p) + '\n' for p in changed))
    tool = [STAGE / 'record-fix-v1/pmd-record-1298.jar', *sorted((STAGE / 'pmd-bin-7.28.0/lib').glob('*.jar'))]
    aux = [JDK / 'lib/jrt-fs.jar', *[work / f'src/schubert-nk-{m}/target/classes'
                                    for m in ('protocol', 'storage', 'bootstrap', 'batch')]]
    static = E / 'PG38762-wbs66-four-current-static-v1'
    allowed_jars = []
    for file in sorted(static.glob('*-analysis.pom.xml')):
        for node in ET.parse(file).findall('.//{*}systemPath'):
            p = Path(node.text)
            if p.is_relative_to(TOOLCHAIN) and p not in allowed_jars:
                assert p.suffix == '.jar' and p.is_file()
                allowed_jars.append(p)
    java = JDK / 'bin/java'
    xml = OUT / 'pmd.xml'
    args = [str(java), '-cp', ':'.join(map(str, tool)), 'net.sourceforge.pmd.cli.PmdCli', 'check',
            '--file-list', str(listing), '--rulesets', str(SETTINGS), '--use-version', 'java-25',
            '--aux-classpath', ':'.join(str(p) for p in [*aux, *allowed_jars]), '--no-cache',
            '--format', 'xml', '--report-file', str(xml)]
    write(OUT / 'begin.json', {'source': begin['sourceCore'], 'build': saved(BUILD),
                               'startedAtUTC': now(), 'policy': saved(SETTINGS), 'command': args,
                               'sourceHashes': {p: sha(work / p) for p in changed},
                               'toolHashes': {str(p): sha(p) for p in tool},
                               'auxAdditionalJars': {str(p): sha(p) for p in allowed_jars},
                               'productTestsExecuted': 0, 'scope': 'Exact 12 changed approved Main'})
    env = {'JAVA_HOME': str(JDK), 'PATH': f'{JDK}/bin:/usr/bin:/bin', 'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8'}
    stdout = OUT / 'pmd.stdout'
    stderr = OUT / 'pmd.stderr'
    with stdout.open('xb') as output, stderr.open('xb') as errors:
        report = subprocess.run(args, cwd=work, env=env, stdout=output, stderr=errors, timeout=180)
    write(OUT / 'terminal.json', {'actualExit': report.returncode, 'terminalAtUTC': now(),
                                  'stdout': saved(stdout), 'stderr': saved(stderr)})
    tree = ET.parse(xml)
    raw = []
    failures = []
    for node in tree.getroot():
        name = node.tag.rsplit('}', 1)[-1]
        if name == 'file':
            path = str(Path(node.attrib['name']).relative_to(work))
            assert path in changed
            for issue in node:
                raw.append({'path': path, 'rule': issue.attrib['rule'],
                            'line': int(issue.attrib['beginline']),
                            'message': ' '.join(''.join(issue.itertext()).split())})
        elif name in ('error', 'configerror'):
            failures.append(node.attrib)
    assert report.returncode == (4 if raw else 0) and not failures
    write(OUT / 'raw.json', {'actualExit': report.returncode, 'source': begin['sourceCore'],
                             'terminalAtUTC': now(), 'pmdXml': saved(xml), 'inputs': len(changed),
                             'processingErrors': failures, 'rawFindings': raw})
    print(json.dumps({'actualExit': report.returncode, 'inputs': len(changed), 'findings': len(raw)}))


if __name__ == '__main__':
    main()
