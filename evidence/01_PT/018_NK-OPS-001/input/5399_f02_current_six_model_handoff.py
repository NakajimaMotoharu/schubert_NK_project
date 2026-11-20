"""Join old validate/model results to the current identical declared build inputs."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
MODULES = ('api', 'batch', 'bootstrap', 'protocol', 'storage', 'web')
POMS = {'pom.xml', 'program/characterization/pom.xml'} | {
    f'src/schubert-nk-{module}/pom.xml' for module in MODULES
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(ref):
    path = Path(ref['path'])
    assert pin(path) == ref
    return json.loads(path.read_bytes())


def blob(source, name):
    return subprocess.check_output(['git', 'show', f'{source}:{name}'])


def main():
    start_file = next(PLAN.glob('1021_F02*'))
    start = json.loads(start_file.read_bytes())['values']
    refs = start['oracleReferences']
    previous, validate, dependency, style, maven, compiler = map(read, refs)
    core = start['productionCoreMain']
    assert previous['productionCoreMain'] == style['productionCore'] == maven['productionCore'] == compiler['productionCore'] == core
    assert validate['actualExit'] == validate['mavenNumericExit'] == dependency['actualExit'] == 0
    assert style['actualExit'] == maven['actualExit'] == compiler['actualExit'] == 0
    assert validate['dependencyConvergencePassed'] == 7 and validate['productClassfilesGenerated'] == 0
    producer = read(validate['producer'])
    producer_exit = Path(validate['producer']['path']).with_name('maven-process-exit.safe.json')
    assert json.loads(producer_exit.read_bytes())['actualExit'] == producer['actualExit'] == 0
    assert validate['source'] == producer['sourceCore']
    assert producer['classfilesGenerated'] == producer['productTestsExecuted'] == 0
    for log in producer['logs']:
        assert pin(Path(log['path'])) == log
    resolved = read(dependency['begin'])
    end = read(dependency['terminal'])
    assert end['source'] == resolved['source'] == dependency['source'] and end['actualExit'] == 0
    assert pin(Path(dependency['stdout']['path'])) == dependency['stdout']
    assert set(resolved['inputs']) == POMS and dependency['actualBuilds'] == 0
    rows = {}
    for name in sorted(POMS):
        data = blob(core, name)
        digest = sha(data)
        assert sha(blob(producer['sourceCore'], name)) == producer['inputHashes'][name] == digest
        assert sha(blob(resolved['source'], name)) == resolved['inputs'][name] == digest
        rows[name] = digest
    wrapper_files = ('mvnw', '.mvn/wrapper/maven-wrapper.properties')
    wrapper = {}
    for name in wrapper_files:
        content = blob(core, name)
        assert content == blob(producer['sourceCore'], name) == blob(resolved['source'], name)
        wrapper[name] = sha(content)
    assert set(validate['declaredProductionAndTestGraph']) == set(MODULES)
    assert validate['declaredProductionAndTestGraph']['web']['testEdges'] == [
        ['api', 'jar'], ['bootstrap', 'test-jar']]
    assert 'api' not in validate['declaredProductionAndTestGraph']['web']['productionEdges']
    assert style['checkstyleCurrentFilenames'] == style['formatterCurrentFilenames'] == 1027

    result = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  source=start['source'], productionCore=core, start=pin(start_file),
                  validateSource=producer['sourceCore'], pomModelSource=resolved['source'],
                  originalValidateExit=pin(producer_exit), receipts=refs[1:], exactPoms=rows,
                  exactWrapper=wrapper, matchedProductPomCount=6, originDependencyConvergence=7,
                  currentProductSourceFormattingCount=1027, currentSourceCompilerCanary=3,
                  sourceScope='declared POM graph and retained metadata resolution only',
                  currentNativeRuntimeVerification=False, currentFullPhysicalBoundaryVerified=False,
                  mavenOrProductsReexecuted=0, protectedClassfilesRead=0, newAcceptance=0,
                  whole451=False, wholeF02=False, recipientsAcknowledged=False)
    out = OPS / start['run']
    out.mkdir()
    manifest = out / 'manifest.json'
    with manifest.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(pin(manifest))


if __name__ == '__main__':
    main()
