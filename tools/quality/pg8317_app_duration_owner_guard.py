"""New explicit responsibility guard/canaries on current public source, never initialize products."""
import copy
import datetime
import json
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
        ('bootstrap-sdk', lambda x: x['bootstrap']['dependencies'].append(('io.prometheus', 'prometheus-metrics-exposition-textformats', '1.7.0'))),
        ('bootstrap-java', lambda x: x['bootstrap']['metricJavaImports'].append('FORBIDDEN_FIXTURE_ONLY')),
        ('bootstrap-package', lambda x: x['bootstrap']['legacyMonitoringPaths'].append('FORBIDDEN_FIXTURE_ONLY')),
        ('web-api-edge', lambda x: x['web']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-api', '0.1.0-SNAPSHOT'))),
        ('api-web-edge', lambda x: x['api']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-web', '0.1.0-SNAPSHOT'))),
        ('app-sdk-missing', lambda x: x['api'].update(dependencies=[])),
        ('api-type-swapped', lambda x: x['api']['java'].update(imports=['io.micrometer.core.instrument.Timer'])),
        ('web-owner-swapped', lambda x: x['web']['java'].update(package='dev.codex.schubert.nk.bootstrap.monitoring')))
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
    assert len(rejected) == 8 and all(host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items())
    verify(invocation)
    OUT.mkdir(exist_ok=False)
    value = dict(actualExit=0, source=SOURCE, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), normalManifestSha256=host.sha(normal_file), invocation=invocation, ownerModel=model, sourceHashes=files, bootstrapSources=len(bootstrap_files), negativeGuards=rejected, productClassInitialization=0, productionPT=0, coverageMeasured=False, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, bug='BUG-1697', rollout='YKT-1448')
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, negatives=len(rejected), bootstrapSources=len(bootstrap_files), manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
