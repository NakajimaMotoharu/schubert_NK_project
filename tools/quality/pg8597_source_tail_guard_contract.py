"""Independent source-mutator literals and same original13 metadata rejection, not product PT."""
import copy
import datetime
import json
from pathlib import Path
import scoped_prometheus_post as post
import pg8592_api_standard_assembly_host as original
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    out = post.host.BASE / 'PG8597-source-tail-guard-contract-v1'
    assert not out.exists()
    literals = [('0000000000000000000000000000000000000000', '0000000000000000000000000000000000000001'), ('123456781', '123456780'), ('12345678f', '123456780')]
    for before, expected in literals:
        assert post.different_source_tail(before) == expected and before != expected
    rejected = []
    for value in (None, '', 0):
        try:
            post.different_source_tail(value)
        except ValueError:
            rejected.append(repr(value))
        else:
            raise AssertionError('all invalid source boundaries reject')
    rawfile = post.host.W / 'pg8592-api-standard-assembly-host-v1/manifest.safe.json'
    assert post.host.sha(rawfile) == '2b75cd3c64cf84795540fffc0e6d419e25725988e70cc4f19f1db363773cac68'
    raw = json.loads(rawfile.read_text())
    post.common.SOURCE = original.SOURCE
    post.COUNTS = original.COUNTS
    post.assess(raw)
    changed = copy.deepcopy(raw)
    changed['source'] = post.different_source_tail(raw['source'])
    assert changed['source'] != raw['source'] and raw['source'].endswith('0')
    try:
        post.assess(changed)
    except ValueError:
        pass
    else:
        raise AssertionError('original13 source-only metadata mutation rejects')
    paths = ['tools/quality/scoped_prometheus_post.py', 'tools/quality/pg8518_metric_role_join_post.py', 'tools/quality/pg8594_api_standard_assembly_post.py', 'tools/quality/pg8582_web_batch_system_post.py']
    assert 'post.different_source_tail' in (post.host.ROOT / paths[1]).read_text()
    assert all('import scoped_prometheus_post as post' in (post.host.ROOT / p).read_text() for p in paths[2:])
    verify(invocation)
    out.mkdir()
    post.host.write(out / 'manifest.json', dict(actualExit=0, source=original.SOURCE, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), invocation=invocation, bug='BUG-1708', rollout='YKT-1459', literalVectors=[dict(input=a, expected=b) for a,b in literals], invalidRejected=rejected, original13SourceOnlyMutationRejected=True, originalRawManifestSha256=post.host.sha(rawfile), files={p: post.host.sha(post.host.ROOT / p) for p in paths}, schemaUsesSameMutator=True, wrappersUseSharedPost=True, oldSuccessfulRunsReplayed=False, metadataOnly=True, productTestsExecuted=0, coverageQualified=False, formalUpdated=False, whole451Accepted=False))
    print(json.dumps(dict(actualExit=0, literalVectors=3, invalidRejected=3, original13Replayed=False, manifestSha256=post.host.sha(out / 'manifest.json'))))
