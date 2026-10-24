"""New explicit responsibility guard/canaries on current public source, never initialize products."""
import copy
import datetime
import json
import hashlib
import subprocess
from pathlib import Path
import pg6966_chr_adapter_host as host
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture, verify

SOURCE = 'd496e7430d70a9edb4092c2b09ca78b8ecfd9004'
OUT = host.BASE / 'PG8317-app-duration-owner-guard-v1'


def main():
    invocation = capture(Path(__file__))
    normal_file = host.BASE / 'PG8316-app-duration-six-compile-v1/manifest.json'
    assert host.sha(normal_file) == '2b979a3b19cb662a6c74d42dc48b426ac9086d34c312928e093a434b88839196'
    normal = json.loads(normal_file.read_text())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == 0
    assert all(host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items())
    model = {role: contract.pom((host.ROOT / ('src/schubert-nk-' + role + '/pom.xml')).read_bytes()) for role in ('bootstrap', 'api', 'web')}
    prior_web = subprocess.check_output(['git', 'show', 'f02fae44edbcf7abba214a6507935c15ae5f9ee9:src/schubert-nk-web/pom.xml'], cwd=host.ROOT)
    legacy = [entry for entry in contract.pom(prior_web)['dependencies'] if entry[:2] == ('dev.codex.schubert', 'schubert-nk-api')]
    assert legacy == [('dev.codex.schubert', 'schubert-nk-api', '${project.version}', 'test')]
    files = {}
    for role, name in (('api', 'ApiDurationMetricExporter'), ('web', 'WebDurationMetricExporter')):
        path = host.ROOT / ('src/schubert-nk-' + role + '/src/main/java/dev/codex/schubert/nk/' + role + '/monitoring/' + name + '.java')
        model[role]['java'] = contract.java(path.read_text())
        files[str(path.relative_to(host.ROOT))] = host.sha(path)
    bootstrap_files = sorted((host.ROOT / 'src/schubert-nk-bootstrap/src/main/java').rglob('*.java'))
    assert bootstrap_files
    model['bootstrap']['metricJavaImports'] = []
    model['bootstrap']['legacyMonitoringPaths'] = []
    for path in bootstrap_files:
        value = path.read_text()
        if 'import io.micrometer.' in value or 'import io.prometheus.' in value:
            model['bootstrap']['metricJavaImports'].append(str(path.relative_to(host.ROOT)))
        if '/bootstrap/monitoring/' in str(path):
            model['bootstrap']['legacyMonitoringPaths'].append(str(path.relative_to(host.ROOT)))
        files[str(path.relative_to(host.ROOT))] = host.sha(path)
    contract.validate(model)
    changes = (
        ('bootstrap-sdk', lambda x: x['bootstrap']['dependencies'].append(('io.prometheus', 'prometheus-metrics-exposition-textformats', '1.7.0', 'compile'))),
        ('bootstrap-java', lambda x: x['bootstrap']['metricJavaImports'].append('FORBIDDEN_FIXTURE_ONLY')),
        ('bootstrap-package', lambda x: x['bootstrap']['legacyMonitoringPaths'].append('FORBIDDEN_FIXTURE_ONLY')),
        ('web-api-edge', lambda x: x['web']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-api', '0.1.0-SNAPSHOT', 'compile'))),
        ('api-web-edge', lambda x: x['api']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-web', '0.1.0-SNAPSHOT', 'compile'))),
        ('app-sdk-missing', lambda x: x['api'].update(dependencies=[])),
        ('api-type-swapped', lambda x: x['api']['java'].update(imports=['io.micrometer.core.instrument.Timer'])),
        ('web-owner-swapped', lambda x: x['web']['java'].update(package='dev.codex.schubert.nk.bootstrap.monitoring')),
        ('legacy-test-promoted', lambda x: x['web'].update(dependencies=[entry[:3] + ('compile',) if entry == legacy[0] else entry for entry in x['web']['dependencies']])))
    rejected = []
    for name, change in changes:
        mutant = copy.deepcopy(model)
        change(mutant)
        try:
            contract.validate(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('ownership negative must reject')
    assert len(rejected) == 9 and all(host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items())
    verify(invocation)
    OUT.mkdir(exist_ok=False)
    value = dict(actualExit=0, source=SOURCE, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), normalManifestSha256=host.sha(normal_file), invocation=invocation, ownerModel=model, sourceHashes=files, bootstrapSources=len(bootstrap_files), negativeGuards=rejected, legacyTestDependencyWitness=dict(source='f02fae44edbcf7abba214a6507935c15ae5f9ee9', webPomSha256=hashlib.sha256(prior_web).hexdigest(), dependencies=legacy, productionScopeAllowed=False), initialGuardFailure='ef46be6c5 omitted dependency scope; rejected unchanged existing PT-IDEM-016 test-only edge before publication; original failure/Git source retained', productClassInitialization=0, productionPT=0, coverageMeasured=False, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, bug='BUG-1697', rollout='YKT-1448')
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, negatives=len(rejected), bootstrapSources=len(bootstrap_files), manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
