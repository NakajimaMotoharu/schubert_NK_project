"""New Web14 and Batch14 standard JVM composition, original28/2; no API replay."""
import scoped_prometheus_host as run
import json
import re

SOURCE = 'a62763d2d7ed5ba6531064166352b976fbf8feb2'
COMPILE = run.host.W / 'pg8578-web-batch-system-six-compile-v1'
COMPILE_SHA = '0a7393ea2f1293935875ad1d653cf3ea582a87ad86e17a03fb442a543dc6eeba'
COUNTS = {'WebSystemMetricsTest': 14, 'BatchSystemMetricsTest': 14}

EXPECTED = {
    'dev.codex.schubert.nk.web.monitoring.WebSystemMetricsTest',
    'dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest',
}

def selected(body):
    matches = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', body, flags=re.S)
    run.require(len(matches) == 1, 'one explicit selection declaration')
    names = re.findall(r'"([a-zA-Z0-9_.]+)"', matches[0])
    run.require(len(names) == 2 and set(names) == EXPECTED, 'exact role-local selection before any JVM')
    return names

def preflight():
    helper = run.host.ROOT / 'tools/quality/architecture/WebBatchSystemMetricsJunitLauncher.java'
    body = helper.read_text()
    names = selected(body)
    for fqcn in names:
        role = fqcn.split('.')[4]
        name = fqcn.rpartition('.')[2]
        fixture = run.host.ROOT / ('src/schubert-nk-' + role + '/src/test/java/' + fqcn.replace('.', '/') + '.java')
        text = fixture.read_text()
        run.require(re.search(r'package\s+' + re.escape(fqcn.rpartition('.')[0]) + r'\s*;', text) is not None and re.search(r'class\s+' + name + r'\b', text) is not None and COUNTS[name] == 14, 'selected class matches actual compile fixture and count')
    rejected = []
    anchor = 'dev.codex.schubert.nk.web.monitoring.WebSystemMetricsTest'
    for name, mutant in (
        ('foreign', body.replace(anchor, 'dev.codex.schubert.nk.api.monitoring.ApiGcMetricRegistrationTest')),
        ('missing', body.replace('"' + anchor + '"', '""')),
        ('duplicate', body.replace(anchor, 'dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest'))):
        try:
            selected(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('selection guard must reject each metadata mutant')
    return dict(selected=names, negatives=rejected, helperSha256=run.host.sha(helper), productTestsExecuted=0)

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8580-web-batch-system-host-v1'
    run.OUT = run.host.BASE / 'PG8580-web-batch-system-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebBatchSystemMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchSystemMetricsTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8580-WEB-BATCH-SYSTEM'
    run.FIXTURES = {}
    metadata = preflight()
    proof = run.host.BASE / 'PG8579-web-batch-system-selection-preflight-v1'
    run.require(not proof.exists(), 'new-only selection metadata')
    proof.mkdir()
    run.host.write(proof / 'manifest.json', dict(actualExit=0, source=SOURCE, **metadata))
    print(json.dumps(dict(selectionPreflightSha256=run.host.sha(proof / 'manifest.json'))), flush=True)
    run.main()
