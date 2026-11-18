"""More F03 evidence from a frozen, ordinary repository-only PMD input set."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
E = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
OUT = E / 'PG38792-f03-ordinary-batch-repository-pmd-v1'
PACKAGE = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/'
NAMES = ('BatchRepositoryException', 'BatchRun', 'BatchRunRepository', 'BatchStep', 'BatchStepAttempt',
         'BatchStepResult', 'CleanupChunk', 'CleanupCounts', 'CleanupKind', 'CleanupReason',
         'CleanupStepChunk', 'InspectionSummary', 'InspectionSummaryRepository', 'LogCleanupProgress',
         'RunReferences', 'SuccessRunLookup')
CORE = 'c58e98bd297adcff2351447e52b2449e1b558255'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': sha(p.read_bytes())}


def write(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    prior_path = E / 'PG38768-f03-twelve-current-main-pmd-v1/begin.json'
    source = E / 'PG38760-wbs66-four-own-main-current-v1/compile/manifest.json'
    prior = json.loads(prior_path.read_text())
    compiled = json.loads(source.read_text())
    work = Path(compiled['cwd'])
    paths = [PACKAGE + n + '.java' for n in NAMES]
    assert compiled['inputHashesReverified'] and compiled['actualExit'] == 0
    assert set(paths).isdisjoint(compiled['changedSources'])
    assert set(OUT.iterdir()) == {OUT / 'quota-start.json'}
    for path in paths:
        frozen = subprocess.check_output(['git', 'show', CORE + ':' + path])
        assert frozen == (work / path).read_bytes() == (ROOT / path).read_bytes()
        assert sha(frozen) == compiled['sourceInputs'][path]
    for path, digest in [*prior['auxAdditionalJars'].items(), *prior['toolHashes'].items()]:
        assert sha(Path(path).read_bytes()) == digest
    for module, expected in compiled['physicalClassHashes'].items():
        directory = work / f'src/schubert-nk-{module}/target/classes'
        assert {str(p.relative_to(directory)): sha(p.read_bytes()) for p in directory.rglob('*.class')} == expected
    assert ref(ROOT / prior['policy']['path']) == prior['policy']
    listing = OUT / 'sources.txt'
    listing.write_text(''.join(str(work / p) + '\n' for p in paths))
    xml = OUT / 'pmd.xml'
    cmd = list(prior['command'])
    cmd[cmd.index('--file-list') + 1] = str(listing)
    cmd[cmd.index('--report-file') + 1] = str(xml)
    write(OUT / 'begin.json', {'startedAtUTC': utc(), 'source': CORE, 'compile': ref(source),
                              'priorPMDOptions': ref(prior_path), 'command': cmd,
                              'paths': {p: compiled['sourceInputs'][p] for p in paths},
                              'sameFourCompileBytes': True})
    java = Path(cmd[0])
    env = {'JAVA_HOME': str(java.parents[1]), 'PATH': f'{java.parent}:/usr/bin:/bin',
           'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8'}
    stdout = OUT / 'pmd.stdout'
    stderr = OUT / 'pmd.stderr'
    with stdout.open('xb') as a, stderr.open('xb') as b:
        result = subprocess.run(cmd, cwd=work, env=env, stdout=a, stderr=b, timeout=180)
    write(OUT / 'terminal.json', {'actualExit': result.returncode, 'terminalAtUTC': utc(),
                                  'stdout': ref(stdout), 'stderr': ref(stderr)})
    raw = []
    processing = []
    for node in ET.parse(xml).getroot():
        kind = node.tag.rsplit('}', 1)[-1]
        if kind == 'file':
            path = str(Path(node.get('name')).relative_to(work))
            assert path in paths
            raw.extend({'path': path, 'rule': x.get('rule'), 'line': int(x.get('beginline')),
                        'message': ' '.join(''.join(x.itertext()).split())} for x in node)
        elif kind in ('configerror', 'error'):
            processing.append(node.attrib)
    assert result.returncode == (4 if raw else 0) and not processing
    write(OUT / 'raw.json', {'actualExit': result.returncode, 'source': CORE, 'report': ref(xml),
                            'names': NAMES, 'issues': raw, 'processingErrors': processing})
    print(json.dumps({'pmdExit': result.returncode, 'scope': len(paths), 'findings': len(raw)}))


if __name__ == '__main__':
    main()
