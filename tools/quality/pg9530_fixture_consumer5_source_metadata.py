"""Five zero-Main fixture primaries derived from all exact known direct consumers; no target run."""
from collections import defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9530-fixture-consumer5-source-metadata-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PREFIX='src/schubert-nk-'
TABLE=[
 ('api','api/messaging/inbound/FatalIsolationFixture','WBS-P005-03',{'CommittedTerminalAdmissionContractTest','FatalIsolationConsumersContractTest'}),
 ('api','api/security/AdminAuthFixture','WBS-P007-03',{'AdminCommandAuthenticatorTest'}),
 ('batch','batch/cleanup/HandoffJdbcProbe','WBS-P004-04',{'InspectorLockHandoffTest'}),
 ('batch','batch/file/CompletionJdbcProbe','WBS-P017-04',{'BackupBundleCompletionTest'}),
 ('batch','batch/repository/BatchJdbcProbe','WBS-P017-07',{'CleanupRepositoryTest','CleanupTerminalRepositoryTest'})]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require_primary(consumers,owners):
    if not consumers or any(path not in owners for path in consumers):raise ValueError('all consumers require known canonical owners')
    found={owners[path] for path in consumers}
    if len(found)!=1 or None in found:raise ValueError('one non-null owner across all consumers required')
    return next(iter(found))

def vectors():
    assert require_primary({'a','b'},{'a':'WBS-X','b':'WBS-X'})=='WBS-X'
    for consumers,owners in ((set(),{}),({'a'},{'b':'WBS-X'}),({'a','b'},{'a':'WBS-X','b':'WBS-Y'}),({'a'},{'a':None})):
        try:require_primary(consumers,owners)
        except ValueError:pass
        else:raise AssertionError('ambiguous or unowned fixture consumer accepted')
    return 5

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    graph_dir=BASE/'PG9386-composite-reference-graph-v3'
    raw=(graph_dir/'manifest.json').read_bytes();assert sha(raw)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(raw);assert graph['actualExit']==0 and graph['source']==SOURCE
    raw_classes=(graph_dir/'test-class-metadata.json').read_bytes();assert sha(raw_classes)==graph['testMetadataSha256']
    raw_unknown=(graph_dir/'unresolved.json').read_bytes();assert sha(raw_unknown)==graph['unresolvedSha256']
    classes=json.loads(raw_classes);unknown={x['path']:x for x in json.loads(raw_unknown)}
    prior_raw=(BASE/'PG9522-api-web42-source-join-v1/manifest.json').read_bytes();assert sha(prior_raw)=='4f85bf805c3e32dbe668e6374bf6a70cb6fa6c0d93edd1ef4ea99bc30925f927'
    prior=json.loads(prior_raw);assert prior['source']==SOURCE and prior['actualExit']==0
    owners={x['path']:x['canonicalOwner'] for x in prior['sourceRows']}
    inv=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    for x in inv['artifacts']:
        assert x['owner']==x['costOwner'];owners[x['path']]=x['owner']
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes();assert sha(normal_raw)=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];source_root=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'
    symbols=defaultdict(set)
    for c in classes:symbols[c['className']].add(c['path'])
    count=vectors();rows=[]
    for module,name,primary,names in TABLE:
        path=PREFIX+module+'/src/test/java/dev/codex/schubert/nk/'+name+'.java'
        assert path not in owners and unknown[path]['mainOwners']==[]
        fixture_symbols={c['className'] for c in classes if c['path']==path}
        assert fixture_symbols and all(symbols[n]=={path} for n in fixture_symbols)
        consumers={c['path'] for c in classes if c['path']!=path and fixture_symbols & set(c['references'])}
        assert require_primary(consumers,owners)==primary and {Path(c).stem for c in consumers}==names
        assert all(c.startswith(PREFIX+module+'/') for c in consumers)
        proofs=[]
        for consumer in sorted(consumers):
            assert sha((ROOT/consumer).read_bytes())==hashes[consumer]==sha((source_root/consumer).read_bytes())
            proofs.append(dict(path=consumer,sha256=hashes[consumer],owner=owners[consumer]))
        assert sha((ROOT/path).read_bytes())==hashes[path]==sha((source_root/path).read_bytes())
        rows.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,relatedOwners=[],
          originalReferenceOwners=[],reviewedConsumerWitnesses=proofs,fixtureClassSymbols=sorted(fixture_symbols),
          witnessScope='ALL_DIRECT_SYMBOL_CONSUMERS_HAVE_ONE_REGISTERED_OWNER_NOT_DUT_OR_RUNTIME_ACCEPTANCE',
          unresolvedRuntimeReasons=unknown[path]['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='EXACT_SINGLE_CANONICAL_CONSUMER_FIXTURE_RESPONSIBILITY_1932_NOT_MAIN_CP_OR_PT'))
    assert len(rows)==5
    verify(invocation);OUT.mkdir()
    for name,value in (('candidates.json',rows),):
        with (OUT/name).open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    with (OUT/'manifest.json').open('x') as f:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          graphManifestSha256=sha(raw),priorManifestSha256=sha(prior_raw),normalManifestSha256=sha(normal_raw),
          candidatesSha256=sha((OUT/'candidates.json').read_bytes()),fixtureSources=5,consumerSources=7,consumerOwnerVectors=count,
          targetRuntimeInvocations=0,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False),f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(dict(actualExit=0,fixtures=5,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
