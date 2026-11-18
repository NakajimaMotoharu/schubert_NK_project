"""Independently verify both stored controller rule decisions and unchanged product source."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
SOURCE = Path('tools/quality/architecture/ModuleDependencyAudit.java')
RESULT = E / 'PG40068-f02-controller-fences-independent-v1'
PROOFS = [next(E.glob(f'PG{n}-*/manifest.json')) for n in (40064, 40066)]
SS = next(Path('documents/300_SS').rglob('311_*.md'))
EXPECTED_ORIGINS = {
    'JdbcController': 'java.sql.Connection',
    'StorageController': 'dev.codex.schubert.nk.storage.KnownValue',
    'SpringJmsController': 'org.springframework.jms.core.JmsTemplate',
    'JakartaController': 'jakarta.jms.Message',
    'JavaxController': 'javax.jms.Message',
    'NioFilesController': 'java.nio.file.Files',
    'FileChannelController': 'java.nio.channels.FileChannel',
    'LegacyFileController': 'java.io.File',
    'AnnotatedEndpoint': 'java.nio.file.Path',
    'NamedHandler': 'javax.jms.Message',
}


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def inspect(path, expected):
    data = read(path)
    assert data['actualExit'] == 0 and data['childArchUnitExit'] == 1
    assert data['tested'] == 12 and data['incorrect'] == 12 - data['correct']
    assert data['correct'] == 2 + len(expected)
    assert not any(data[key] for key in ('productClassesLoaded', 'productJarsScanned', 'productTests'))
    assert sha(git('show', f"{data['source']}:{SOURCE}")) == data['toolInput']['sha256']
    assert ref(data['verifier']['path']) == data['verifier']
    for label, receipt in data['receipts'].items():
        assert read(path.parent / (label + '-exit.json')) == receipt
        assert ref(receipt['stdout']['path']) == receipt['stdout']
        assert ref(receipt['stderr']['path']) == receipt['stderr']
        assert receipt['actualExit'] == (1 if label == 'audit' else 0)
    stdout = Path(data['receipts']['audit']['stdout']['path']).read_text().splitlines()
    assert 'ARCHUNIT\t1.4.2\t24\t24' in stdout
    imports = [int(line.rsplit('\t', 1)[1]) for line in stdout if line.startswith('MODULE\t')]
    assert sorted(imports) == [1, 1, 1, 1, 1, 19]
    findings = [line.split('\t') for line in stdout if line.startswith('FINDING\t')]
    assert all(bits[1] == 'CONTROLLER_BOUNDARY' for bits in findings)
    assert len(findings) == len(expected)
    assert {klass.rsplit('.', 1)[1]: target for _, _, klass, target in findings} == expected
    return data


def main():
    baseline = inspect(PROOFS[0], {key: EXPECTED_ORIGINS[key] for key in ('JdbcController', 'StorageController')})
    corrected = inspect(PROOFS[1], EXPECTED_ORIGINS)
    assert baseline['source'] != corrected['source']
    assert baseline['verifier'] == corrected['verifier']
    assert baseline['toolInput']['sha256'] != corrected['toolInput']['sha256']
    spec = git('show', f"{corrected['canonicalDesign']}:{SS}")
    assert 'ControllerはJDBC、JMS template、filesystem APIを直接呼ばない。'.encode() in spec
    assert git('diff', '--name-only', baseline['source'], corrected['source'], '--', 'src') == b''
    assert git('diff', '--name-only', corrected['productionCoreMain'], corrected['source'], '--',
               'src/**/src/main', 'src/**/pom.xml', 'pom.xml') == b''
    assert [r['testId'] for r in baseline['cases']] == [r['testId'] for r in corrected['cases']]
    assert all(row['actual'] == row['expected'] for row in corrected['cases'])
    RESULT.mkdir()
    report = dict(
        actualExit=0, source=corrected['source'], productionCoreMain=corrected['productionCoreMain'],
        initial=ref(PROOFS[0]), corrected=ref(PROOFS[1]), rawFindingsBefore=2, rawFindingsAfter=10,
        initialCorrect=4, initialIncorrect=8, correctedCorrect=12, correctedIncorrect=0,
        syntheticClasses=24, syntheticJars=6, unchangedOtherRules=4, productTests=0,
        productRuntimeInvocations=0, productCoverageNew=0, currentProductJarRebuilt=0,
        design=dict(path=str(SS), source=corrected['canonicalDesign'], sha256=sha(spec)),
        fixturesUnchanged=True, wholeF02Accepted=False, wholeF03Accepted=False, whole451Accepted=False,
        acceptedDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        verifier=ref(Path(__file__)),
    )
    path = RESULT / 'manifest.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(ref(path))


if __name__ == '__main__':
    main()
