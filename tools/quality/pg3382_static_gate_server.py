"""PG3382 read-only Production analysis; new-only output, actual whole3372 aux byte proof."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import xml.etree.ElementTree as ET
import zipfile

BASE = Path('/home/mini/schubert-nk-pgpt')
SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
JDK = BASE / 'tools/jdk-25.0.4/bin/java'
MODULES = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
TOOLS = {
    'pmd-dist-7.28.0-bin.zip': 'f974ba571f7bc01c73fffe11bade25fbc1f438698f9e9c00e416e8d65e9fbac2',
    'checkstyle-14.3.0-all.jar': '754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def command(argv, output, cwd):
    with output.open('xb') as log:
        result = subprocess.run(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    return {'argv': [str(x) for x in argv], 'exit': result.returncode, 'outputSha256': digest(output)}


def main(stage, archive_hash):
    os.umask(0o077)
    stage = stage.resolve()
    require(stage.parent == BASE / 'runs' and stage.name == 'PG3382-static-gate-v1', 'specific staging root')
    out = stage / 'result'
    out.mkdir(mode=0o700)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for name, expected in TOOLS.items():
        require(digest(stage / name) == expected, 'pinned tool bytes')
    archive = stage / 'source.tar'
    require(digest(archive) == archive_hash, 'fixed source archive')
    tree = out / 'source'
    tree.mkdir()
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            p = Path(member.name)
            require(not p.is_absolute() and '..' not in p.parts and (member.isdir() or member.isfile()), 'plain source-only members')
            require(p.parts[0] in ['src', 'tools'], 'source/config only')
        tar.extractall(tree, filter='data')
    full = BASE / 'runs/PG3372-six-v1'
    manifest = json.loads((full / 'manifest.safe.json').read_bytes())
    inputs = json.loads((full / 'begin.safe.json').read_bytes())['inputs']
    require(manifest['actualExit'] == manifest['mavenExit'] == 0 and manifest['tests'] == 3706
            and manifest['productionSource'] == SOURCE, 'actual qualified whole3706')
    files = sorted(tree.glob('src/*/src/main/java/**/*.java'))
    expected = {p: h for p, h in inputs.items() if '/src/main/java/' in p and p.endswith('.java') and p.startswith('src/')}
    actual = {str(p.relative_to(tree)): digest(p) for p in files}
    require(actual == expected and len(files) > 800, 'complete exact same whole Production source, no exclusions')
    jars = []; class_count = 0
    for module in MODULES:
        jar = full / module / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')
        with zipfile.ZipFile(jar) as z:
            classes = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
        require(classes == manifest['modules'][module]['mainClassHashes'], 'all actual module class bytes')
        class_count += len(classes); jars.append(jar)
    require(class_count == 1643, 'complete Main byte inventory')
    for module in MODULES:
        reports = sorted((full / module / 'surefire-reports').glob('TEST-*.xml'))
        require(reports, 'original actual XML')
        props = {x.get('name'): x.get('value') for x in ET.parse(reports[0]).getroot().findall('./properties/property')}
        cp = props.get('surefire.test.class.path', props.get('java.class.path', ''))
        require(cp, 'actual classpath property')
        for item in cp.split(':'):
            p = Path(item)
            if p.suffix == '.jar' and p not in jars:
                require(p.is_absolute() and p.is_file() and p.resolve().is_relative_to(BASE), 'authenticated exact dependency Jar')
                jars.append(p)
    pmd_tree = out / 'pmd'
    pmd_tree.mkdir()
    with zipfile.ZipFile(stage / 'pmd-dist-7.28.0-bin.zip') as z:
        for name in z.namelist():
            p = Path(name); require(not p.is_absolute() and '..' not in p.parts, 'safe official distribution path')
        z.extractall(pmd_tree)
    pmd_cp = ':'.join(str(p) for p in sorted(pmd_tree.glob('pmd-bin-7.28.0/lib/*.jar')))
    require(pmd_cp, 'PMD distribution libraries')
    config = tree / 'tools/quality/static'
    filelist = out / 'all-java.txt'
    filelist.write_text(''.join(str(p) + '\n' for p in files))
    aux = out / 'aux-classpath.txt'
    aux.write_text('\n'.join(str(p) for p in jars) + '\n')
    # All priorities; violations/error exits preserved, no --no-fail flags.
    pmd = command([str(JDK), '-cp', pmd_cp, 'net.sourceforge.pmd.cli.PmdCli', 'check', '--file-list', str(filelist),
                   '--rulesets', str(config / 'pmd.xml'), '--use-version', 'java-25', '--minimum-priority', '5',
                   '--aux-classpath', 'file:' + str(aux), '--no-cache', '--format', 'xml', '--report-file', str(out / 'pmd.xml')],
                  out / 'pmd.private.log', out)
    checkstyle = command([str(JDK), '-jar', str(stage / 'checkstyle-14.3.0-all.jar'), '-c', str(config / 'checkstyle.xml'),
                         '-f', 'xml', '-o', str(out / 'checkstyle.xml'), '@' + str(filelist)], out / 'checkstyle.private.log', out)
    pmd_xml = ET.parse(out / 'pmd.xml').getroot()
    violations = pmd_xml.findall('.//{*}violation'); errors = pmd_xml.findall('.//{*}error')
    check_xml = ET.parse(out / 'checkstyle.xml').getroot()
    cs_errors = check_xml.findall('.//error')
    value = {'run': 'PG3382-static-gate-v1', 'productionSource': SOURCE, 'startUTC': started,
             'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sourceArchiveSha256': archive_hash,
             'sourceFiles': len(files), 'sourceSha256': actual, 'auxMainClasses': class_count,
             'auxJarSha256': {str(p): digest(p) for p in jars}, 'fullManifestSha256': digest(full / 'manifest.safe.json'),
             'pinnedToolSha256': TOOLS, 'ruleSha256': {p.name: digest(p) for p in config.glob('*.xml')},
             'pmd': {**pmd, 'violations': len(violations), 'processingErrors': len(errors),
                     'ruleCounts': dict(Counter(x.get('rule') for x in violations))},
             'checkstyle': {**checkstyle, 'violations': len(cs_errors),
                            'ruleCounts': dict(Counter(x.get('source') for x in cs_errors))},
             'reportsSha256': {n: digest(out / n) for n in ['pmd.xml', 'checkstyle.xml']},
             'F03Accepted': False, 'formalUpdated': False, 'newPtCredit': 0, 'productionMutated': False}
    value['sourceUnchangedAfter'] = all(digest(tree / p) == h for p, h in actual.items())
    require(value['sourceUnchangedAfter'], 'read-only source postcondition')
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, indent=2)
    print(json.dumps({k: value[k] for k in ['run', 'sourceFiles', 'auxMainClasses', 'pmd', 'checkstyle', 'reportsSha256', 'sourceUnchangedAfter']}))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', type=Path); parser.add_argument('archive_sha256')
    args = parser.parse_args()
    raise SystemExit(main(args.stage, args.archive_sha256))
