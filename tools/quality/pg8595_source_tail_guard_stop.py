"""Preserve actual pre-coverage metadata fixture failure, no production/JUnit replay."""
import datetime
import json
from pathlib import Path
import copy
import scoped_prometheus_post as post
import pg8592_api_standard_assembly_host as original
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    out = post.host.BASE / 'PG8595-source-tail-guard-stop-v1'
    assert not out.exists() and not (post.host.W / 'pg8594-api-standard-assembly-post-v1').exists()
    file = post.host.W / 'pg8592-api-standard-assembly-host-v1/manifest.safe.json'
    assert post.host.sha(file) == '2b75cd3c64cf84795540fffc0e6d419e25725988e70cc4f19f1db363773cac68'
    raw = json.loads(file.read_text())
    post.common.SOURCE = original.SOURCE
    post.COUNTS = original.COUNTS
    post.assess(raw)
    changed = copy.deepcopy(raw)
    changed['source'] = changed['source'][:-1] + '0'
    assert changed['source'] == raw['source'] and raw['source'].endswith('0')
    post.assess(changed)
    library = post.host.ROOT / 'tools/quality/scoped_prometheus_post.py'
    verify(invocation)
    out.mkdir()
    post.host.write(out / 'manifest.json', dict(actualExit=1, source=raw['source'], bug='BUG-1708', rollout='YKT-1459', timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), invocation=invocation, originalRawManifestSha256=post.host.sha(file), originalTests=13, originalSuites=1, originalJunitExit=0, oldMutationChangedSource=False, metadataFixtureFailure=True, originalPostLibrarySha256=post.host.sha(library), originalPostLibrary=library.read_text(), postSlotCreated=False, coverageExecuted=False, staticExecuted=False, productTestsExecutedByPreservation=0, whole451Accepted=False, formalUpdated=False, newAccepted=0))
    print(json.dumps(dict(preserved=True, oldMutationChanged=False, originalTests=13, productTestsExecuted=0, manifestSha256=post.host.sha(out / 'manifest.json'))))
