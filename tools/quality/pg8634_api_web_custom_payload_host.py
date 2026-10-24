"""New Web14 and Batch14 standard JVM composition, original28/2; no API replay."""
import scoped_prometheus_host as run
import json
import re

SOURCE = 'f817b004781e6c32aa2d384dd12855cad7175ddc'
COMPILE = run.host.W / 'pg8632-api-web-custom-payload-six-compile-v1'
COMPILE_SHA = '8039af9b7750d5b689c4663cdb6f02634ad857ed76ad52f6f7d3bba25c0d1c9b'
COUNTS = {'WebCustomMetricPayloadTest': 13, 'ApiCustomMetricPayloadTest': 13}

EXPECTED = {
    'dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest',
    'dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest',
}

def selected(body):
    matches = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', body, flags=re.S)
    run.require(len(matches) == 1, 'one explicit selection declaration')
    names = re.findall(r'"([a-zA-Z0-9_.]+)"', matches[0])
    run.require(len(names) == 2 and set(names) == EXPECTED, 'exact role-local selection before any JVM')
    return names

def preflight():
    helper = run.host.ROOT / 'tools/quality/architecture/ApiWebCustomMetricPayloadJunitLauncher.java'
    body = helper.read_text()
    names = selected(body)
    for fqcn in names:
        role = fqcn.split('.')[4]
        name = fqcn.rpartition('.')[2]
        fixture = run.host.ROOT / ('src/schubert-nk-' + role + '/src/test/java/' + fqcn.replace('.', '/') + '.java')
        text = fixture.read_text()
        run.require(re.search(r'package\s+' + re.escape(fqcn.rpartition('.')[0]) + r'\s*;', text) is not None and re.search(r'class\s+' + name + r'\b', text) is not None and COUNTS[name] == 13, 'selected class matches actual compile fixture and count')
    rejected = []
    anchor = 'dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest'
    for name, mutant in (
        ('foreign', body.replace(anchor, 'dev.codex.schubert.nk.api.monitoring.ApiGcMetricRegistrationTest')),
        ('missing', body.replace('"' + anchor + '"', '""')),
        ('duplicate', body.replace(anchor, 'dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest'))):
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
    run.SLOT = run.host.W / 'pg8634-api-web-custom-payload-host-v1'
    run.OUT = run.host.BASE / 'PG8634-api-web-custom-payload-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiWebCustomMetricPayloadJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiCustomMetricPayloadTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8634-API-WEB-CUSTOM'
    run.FIXTURES = {}
    metadata = preflight()
    proof = run.host.BASE / 'PG8633-api-web-custom-payload-selection-preflight-v1'
    run.require(not proof.exists(), 'new-only selection metadata')
    proof.mkdir()
    run.host.write(proof / 'manifest.json', dict(actualExit=0, source=SOURCE, **metadata))
    print(json.dumps(dict(selectionPreflightSha256=run.host.sha(proof / 'manifest.json'))), flush=True)
    run.main()
