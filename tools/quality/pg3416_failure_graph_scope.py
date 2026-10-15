"""Whole Main exception-edge scope and actual existing five-handler regression witnesses."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from lan_server import run

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
GRAPHS = {
    'api/messaging/outbound/OutboxJmsSender': ('api', 'messaging.outbound.OutboxDispatcherTest', 'cause3404TypedGraphTerminatesCyclesAndVisitsBothProviderEdges', 'FIXED_CAUSE_LINK_IDENTITY_GRAPH'),
    'web/logging/WebLogMessageSender': ('web', 'logging.WebLogMessageSenderTest', 'duplicateDetectionUsesTypedCauseAndLinkedGraphNotTextAndTerminatesCycles', 'EXISTING_CAUSE_LINK_IDENTITY_GRAPH'),
    'web/revocation/RevocationRetryCoordinator': ('web', 'revocation.RevocationRetryCoordinatorTest', 'rerun005gFatalIdentityNestedCyclicFailuresAndResourceAfterconditions', 'EXISTING_CAUSE_SUPPRESSED_IDENTITY_FATAL_GRAPH'),
    'web/session/SessionStoreException': ('web', 'session.SessionFailureGraphTest', 'mixedCauseAndSuppressedCyclesTerminateAndReachableFatalRetainsIdentity', 'EXISTING_CAUSE_SUPPRESSED_IDENTITY_FATAL_GRAPH'),
    'api/security/AuthenticationInfrastructureException': ('api', 'security.AuthenticationFailureGraphTest', 'suppressedCyclesTerminateAndReachableFatalRetainsIdentity', 'EXISTING_SUPPRESSED_IDENTITY_JDBC_FATAL_GRAPH')}
SINGLE = {
    'web/messaging/JmsRequestReplyClient': 'ExecutionException single unwrap; never follows another cause; registry cancellation in finally',
    'api/messaging/inbound/ApiMessagingRuntime': 'Single owned fixed closeGroups wrapper unwrap; no cause iteration',
    'batch/platform/ConfigurationGroupResolver': 'Future ExecutionException single unwrap into fixed I/O/runtime or exact fatal; no graph traversal',
    'batch/platform/InspectorUnitProbe': 'Future ExecutionException single unwrap and typed rethrow; no graph traversal'}


def main():
    rows = []; targets = {}; observed = set()
    for p in sorted((ROOT / 'src').glob('*/src/main/java/**/*.java')):
        text = p.read_text(); relative = str(p.relative_to(ROOT))
        hits = [(i, line.strip()) for i, line in enumerate(text.splitlines(), 1)
                if re.search(r'\.get(?:Cause|LinkedException|NextException|Suppressed)\s*\(', line)]
        if not hits:
            continue
        assert p.read_bytes() == subprocess.check_output(['git', 'show', SOURCE + ':' + relative], cwd=ROOT)
        key = str(p).split('/dev/codex/schubert/nk/', 1)[1][:-5]
        if key in GRAPHS:
            assert 'IdentityHashMap' in text and ('seen.add(' in text or 'seen.put(' in text)
            disposition = GRAPHS[key][3]; observed.add(key)
        elif key in SINGLE:
            assert all('getCause()' in line for _, line in hits)
            disposition = SINGLE[key]
        else:
            assert all('getSuppressed().length' in line for _, line in hits), 'unclassified graph access: ' + relative
            disposition = 'BOUNDED_SUPPRESSED_ARRAY_LENGTH_ONLY; no node traversal, recursive call or replacement candidate'
        targets[relative] = {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'disposition': disposition,
                             'accesses': [{'line': i, 'code': line} for i, line in hits]}
        rows.extend((relative, i) for i, _ in hits)
    assert observed == set(GRAPHS)
    data = [{'key': key, 'module': v[0], 'class': 'dev.codex.schubert.nk.' + v[0] + '.' + v[1], 'method': v[2]}
            for key, v in GRAPHS.items()]
    remote = """import json,hashlib,xml.etree.ElementTree as E
from pathlib import Path
b=Path('/home/mini/schubert-nk-pgpt');p=b/'runs/PG3409-related-qualified-v1/manifest.safe.json';qualified=json.loads(p.read_bytes());assert qualified['actualExit']==qualified['mavenExit']==0 and qualified['tests']==60
results=[]
for item in INPUT:
 x=b/('source-PG3408-related-v1/src/schubert-nk-'+item['module']+'/target/surefire-reports/TEST-'+item['class']+'.xml');h=hashlib.sha256(x.read_bytes()).hexdigest();assert h==qualified['modules'][item['module']]['xmlHashes'][x.name]
 r=E.parse(x).getroot();matches=[c for c in r.findall('testcase')if c.get('classname')==item['class']and c.get('name')==item['method']];assert len(matches)==1 and not any(k.tag in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']for k in matches[0]);results.append({**item,'actualFound':1,'nonSuccess':0,'xmlSha256':h})
print(json.dumps({'witnesses':results,'relatedManifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
"""
    rc, text = run("python3 - <<'SCOPE'\nINPUT=" + repr(data) + '\n' + remote + '\nSCOPE', timeout=30)
    assert rc == 0
    actual = json.loads(text.strip())
    proof = {'actualExit': 0, 'run': 'PG3416-failure-graph-scope', 'candidateSource': SOURCE,
             'bug': 'BUG1299', 'ykt': 'YKT1065', 'mainFilesWithAccesses': len(targets), 'accesses': len(rows),
             'graphHandlers': 5, 'unclassified': 0, 'targets': targets, 'actualWitnesses': actual,
             'newProductionPtCredit': 0, 'testReplay': False, 'vmActions': 0,
             'scopeBoundary': 'Finite graph traversal and actual five handler cycle/fatal witnesses only; whole candidate/native and final YKT closure pending',
             'formalUpdated': False, 'pgptAllComplete': False}
    os.umask(0o077)
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3416-failure-graph-scope'; out.mkdir()
    p = out / 'manifest.json'; p.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'mainFiles': len(targets), 'accesses': len(rows),
                      'handlersWithActualCycleWitness': 5, 'manifestSha256': hashlib.sha256(p.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
