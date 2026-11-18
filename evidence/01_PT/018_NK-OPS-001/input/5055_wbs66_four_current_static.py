"""F02/F03: examine only the admitted four-module Maven Main output, without product execution."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import pgpt_spotbugs_contract as spotbugs

ROOT = Path.cwd()
EVIDENCE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
WORK = ROOT.parent / 'pgpt-runs/PG379/pg38760-wbs66-four-own-main-current-v1'
TOOLCHAIN = ROOT.parent / 'toolchain'
BASE = EVIDENCE / 'PG38760-wbs66-four-own-main-current-v1/compile'
OLD_OUTPUT = EVIDENCE / 'PG38206-bootstrap-batch-spotbugs-v1/attempt-02'
OUT = EVIDENCE / 'PG38762-wbs66-four-current-static-v1'
ANALYSIS = WORK / 'independent-static'
JAVA = TOOLCHAIN / 'jdk-25.0.4/bin/java'
NS = spotbugs.NS
ET.register_namespace('', NS.removesuffix('}').removeprefix('{'))


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def save(path, value):
    with path.open('x', encoding='utf-8') as file:
        json.dump(value, file, indent=2)
        file.write('\n')


def classes(directory):
    return {str(path.relative_to(directory)): sha(path) for path in directory.rglob('*.class')}


def stable_jar(directory, destination):
    with ZipFile(destination, 'x') as jar:
        for name in sorted(classes(directory)):
            jar.write(directory / name, name)
    with ZipFile(destination) as jar:
        assert {name: hashlib.sha256(jar.read(name)).hexdigest() for name in jar.namelist()} == classes(directory)


def analysis_pom(module, source, jars):
    old = OLD_OUTPUT / f'{module}-analysis-v2.pom.xml'
    tree = ET.parse(old)
    original = spotbugs.canonical_plugin((WORK / f'src/schubert-nk-{module}/pom.xml').read_bytes())
    installed = next(node for node in tree.findall('.//' + NS + 'plugin')
                     if node.findtext(NS + 'artifactId') == 'spotbugs-maven-plugin')
    assert all(installed.find(NS + 'configuration/' + NS + key).text == value
               for key, value in spotbugs.SETTINGS.items())
    assert original.findtext(NS + 'version') == installed.findtext(NS + 'version')
    build = tree.find(NS + 'build')
    build.find(NS + 'directory').text = str(ANALYSIS / f'{module}-target')
    build.find(NS + 'outputDirectory').text = str(source)
    for field in tree.findall('.//' + NS + 'systemPath'):
        path = Path(field.text)
        if path.name in jars and not path.is_relative_to(TOOLCHAIN):
            field.text = str(jars[path.name])
        elif not path.is_relative_to(TOOLCHAIN):
            raise ValueError(f'unknown SDK operand {path.name}')
        assert Path(field.text).is_file()
    path = OUT / f'{module}-analysis.pom.xml'
    tree.write(path, encoding='utf-8', xml_declaration=True)
    return path


def run(label, args, environment):
    with (OUT / f'{label}.stdout').open('xb') as stdout, (OUT / f'{label}.stderr').open('xb') as stderr:
        try:
            code = subprocess.run(args, cwd=WORK, env=environment, stdout=stdout, stderr=stderr,
                                  timeout=180).returncode
        except subprocess.TimeoutExpired:
            code = 124
    result = {'actualExit': code, 'terminalAtUTC': utc(), 'stdout': ref(OUT / f'{label}.stdout'),
              'stderr': ref(OUT / f'{label}.stderr')}
    save(OUT / f'{label}-exit.json', result)
    return label, result


def main():
    compiled = json.loads((BASE / 'manifest.json').read_text())
    assert compiled['actualExit'] == 0 and compiled['inputHashesReverified']
    assert json.loads((BASE / 'maven-process-exit.safe.json').read_text())['actualExit'] == 0
    original = json.loads((EVIDENCE / 'PG38256-wbs66-four-current-compile-v1/compile/manifest.json').read_text())
    four = compiled['physicalClassHashes']
    assert len(four) == 4 and four['protocol'] == original['physicalClassHashes']['protocol']
    compiled_dirs = {module: WORK / f'src/schubert-nk-{module}/target/classes' for module in four}
    assert all(classes(compiled_dirs[module]) == expected for module, expected in four.items())
    assert all(sha(WORK / path) == digest for path, digest in compiled['sourceInputs'].items())
    OUT.mkdir()
    ANALYSIS.mkdir()
    jars = {}
    for module in ('storage', 'bootstrap'):
        name = f'current-{module}.jar'
        jars[name] = ANALYSIS / name
        stable_jar(compiled_dirs[module], jars[name])
    inputs = sorted(WORK / path for path in compiled['sourceInputs'] if path.endswith('.java'))
    assert len(inputs) == 482
    listing = OUT / 'sources.txt'
    listing.write_text(''.join(str(path) + '\n' for path in inputs))
    cs = OUT / 'checkstyle.xml'
    check = ROOT / 'tools/quality/static/checkstyle.xml'
    formatter = TOOLCHAIN / 'google-java-format-1.36.1-all-deps.jar'
    cmd = {
        'checkstyle': [str(JAVA), '-jar', str(TOOLCHAIN / 'static-gates-20261015/checkstyle-14.3.0-all.jar'),
                       '-c', str(check), '-f', 'xml', '-o', str(cs), '@' + str(listing)],
        'format-delta': [str(JAVA), '-jar', str(formatter), '--skip-reflowing-long-strings', '--dry-run',
                         '--set-exit-if-changed', *[str(WORK / path) for path in compiled['changedSources']]],
    }
    xml_locations = {}
    for module in ('storage', 'bootstrap', 'batch'):
        if module == 'storage':
            pom = WORK / 'src/schubert-nk-storage/pom.xml'
            spotbugs.canonical_plugin(pom.read_bytes())
            xml_locations[module] = compiled_dirs[module].parent / 'spotbugsXml.xml'
        else:
            pom = analysis_pom(module, compiled_dirs[module], jars)
            xml_locations[module] = ANALYSIS / f'{module}-target/spotbugsXml.xml'
        cmd[module] = spotbugs.checked_command(
            [*compiled['command'][:5], '-f', str(pom), '-Dmaven.test.skip=true', *spotbugs.FLAGS,
             'com.github.spotbugs:spotbugs-maven-plugin:' + spotbugs.VERSION + ':check']
        )
    save(OUT / 'begin.json', {'source': compiled['sourceCore'], 'commands': cmd,
                              'compile': ref(BASE / 'manifest.json'), 'startedAtUTC': utc(),
                              'newSdkOrProductExecutions': 0, 'checkstyleRule': ref(check),
                              'localAnalysisJars': {name: sha(path) for name, path in jars.items()}})
    env = {'JAVA_HOME': str(JAVA.parents[1]), 'PATH': f'{JAVA.parent}:/usr/bin:/bin',
           'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8'}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(run, label, args, env) for label, args in cmd.items()]
        endings = dict(future.result() for future in futures)
    ck = ET.parse(cs).getroot() if cs.is_file() else None
    files = set() if ck is None else {Path(x.get('name')) for x in ck.findall('file')}
    checkstyle = {'files': len(files), 'expectedInputSet': files == set(inputs),
                  'findings': None if ck is None else len(ck.findall('.//error')), 'raw': ref(cs) if cs.is_file() else None}
    physical = {}
    for module, path in xml_locations.items():
        if not path.is_file():
            physical[module] = {'reportMissing': True}
            continue
        public = OUT / f'{module}-spotbugs.xml'
        public.write_bytes(path.read_bytes())
        root = ET.parse(public).getroot()
        actual = {x.get('class').replace('.', '/') + '.class' for x in root.findall('.//ClassStats')}
        physical[module] = {'physical': len(actual), 'exactPhysical': actual == set(four[module]),
                            'findings': len(root.findall('BugInstance')), 'errors': len(root.findall('.//Error')),
                            'missingClasses': len(root.findall('.//MissingClass')), 'raw': ref(public)}
    result = {'actualExit': 0 if all(x['actualExit'] == 0 for x in endings.values()) else 1,
              'source': compiled['sourceCore'], 'terminalAtUTC': utc(), 'checks': endings,
              'physical': physical, 'checkstyle': checkstyle, 'compile': ref(BASE / 'manifest.json'),
              'allInputAndPhysicalBytesStillExact': all(sha(WORK / rel) == h for rel, h in compiled['sourceInputs'].items())
              and all(classes(compiled_dirs[m]) == four[m] for m in four),
              'protocolPhysicalEqualToEarlier': True, 'pmdProductWideExecuted': False,
              'whole451Accepted': False, 'apiOrWebClassActions': 0, 'productTestsExecuted': 0}
    save(OUT / 'manifest.json', result)
    print(json.dumps({k: result[k] for k in ('actualExit', 'physical', 'checkstyle')}))
    return result['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
