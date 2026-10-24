"""Actual canonical-owner validator and independent golden ownership cases; metadata only/PT0."""
import copy
import datetime
import json
from pathlib import Path
import trace_owner_join as owner
import pg8958_canonical_owner_join as audit
from host_tool_invocation import capture,verify

def main():
    invocation=capture(Path(__file__))
    out=audit.host.BASE/'PG8960-canonical-owner-guards-v1'
    qualified=audit.host.BASE/'PG8958-canonical-owner-join-v1/manifest.json'
    assert not out.exists() and audit.host.sha(qualified)=='208fa4cd2ecb4ca62631fae6cc60ebaef39abd410edd64da00f4d3a29f244755'
    result=json.loads(qualified.read_text());inventory=json.loads(audit.INVENTORY.read_text())
    raw=json.loads(audit.TRACE.read_text());normal=json.loads(audit.NORMAL.read_text())
    logical={row['path']:row for row in inventory['artifacts']};hashes=normal['begin']['inputHashes']
    assert audit.digest(inventory['artifacts'])==result['logicalInventoryDatasetSha256']
    assert audit.digest(inventory['currentPhysicalCandidate'])==result['historicalPhysicalDatasetSha256']
    rows=result['sourceRows'];owner.validate(rows,raw['sourceRows'],logical,hashes,'WBS-P018-09')
    index={row['path']:i for i,row in enumerate(rows)}
    native=index['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java']
    config=index['src/deployment/monitoring/prometheus/debug.yml.template']
    pom=index['src/schubert-nk-api/pom.xml']
    mutations=[
      ('baseline-owner-overwritten',lambda value:value[native].update(owner='WBS-P018-09',canonicalOwner='WBS-P018-09')),
      ('baseline-costowner-overwritten',lambda value:value[native].update(canonicalCostOwner='WBS-C07')),
      ('change-owner-reassigned',lambda value:value[native].update(changeOwner='WBS-P018-06')),
      ('historical-cost-reallocation',lambda value:value[native].update(historicalCostsReallocated=True)),
      ('invented-exclusive-cost',lambda value:value[native].update(actualAllocatedPp=0)),
      ('old-pt-transferred',lambda value:value[native].update(currentSourcePtQualificationInferred=True)),
      ('historical-run-reassigned',lambda value:value[native].update(historicalRunReassigned=True)),
      ('wrong-current-hash',lambda value:value[native].update(sha256='0'*64)),
      ('missing-row',lambda value:value.pop()),
      ('duplicate-assignment',lambda value:value.__setitem__(-1,copy.deepcopy(value[0]))),
      ('new-candidate-falsely-accepted',lambda value:value[config].update(ownershipStatus='ACCEPTED')),
      ('config-double-assigned',lambda value:value[config].update(owner='WBS-P018-09',canonicalOwner='WBS-P018-09')),
      ('module-build-owner-changed',lambda value:value[pom].update(canonicalOwner='WBS-C07'))]
    rejected=[]
    for name,mutate in mutations:
        changed=copy.deepcopy(rows);mutate(changed)
        try: owner.validate(changed,raw['sourceRows'],logical,hashes,'WBS-P018-09')
        except (ValueError,KeyError): rejected.append(name)
        else: raise AssertionError('every forged owner correction must reject')
    # Expected owners below are explicit WBS/1839 decisions, never inferred from the resolver.
    fixtures=[
      ('src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebServiceMetricBinding.java','WBS-P018-09'),
      ('src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/persistence/AsyncJobCountRepository.java','WBS-P018-09'),
      ('src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt','WBS-P018-09'),
      ('src/deployment/monitoring/prometheus/debug.yml.template','WBS-C07'),
      ('src/schubert-nk-api/pom.xml','WBS-F02'),
      ('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java','WBS-C06'),
      ('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java','WBS-C02')]
    for path,expected in fixtures:
        resolved=owner.canonical(path,logical)
        assert resolved['canonicalOwner']==resolved['canonicalCostOwner']==expected
    # Namespace similarity never resolves an unknown/private path or reallocates its cost.
    unknown='src/unclassified/Unknown.java';source={unknown:'1'*64}
    original=[dict(path=unknown,sha256='1'*64,owner='WBS-P018-09')]
    unknown_rows=owner.join_rows(original,logical,source,'WBS-P018-09')
    assert unknown_rows[0]['ownershipStatus']=='UNKNOWN' and unknown_rows[0]['canonicalOwner'] is None
    forged=copy.deepcopy(unknown_rows);forged[0].update(owner='WBS-P018-09',canonicalOwner='WBS-P018-09')
    try: owner.validate(forged,original,logical,source,'WBS-P018-09')
    except ValueError: rejected.append('unknown-guessed-from-change-owner')
    else: raise AssertionError('unknown must stay unknown')
    assert owner.canonical('src/deployment/monitoring/example.private.json',logical)['ownershipStatus']=='UNKNOWN'
    for path in ('/outside/private.java','src/../private.java'):
        try: owner.proposed_owner(path)
        except ValueError: rejected.append('unsafe-path:'+path)
        else: raise AssertionError('outside namespace rejects without filesystem access')
    verify(invocation);out.mkdir()
    audit.host.write(out/'manifest.json',dict(actualExit=0,source=audit.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,joinManifestSha256=audit.host.sha(qualified),actualResolverSha256=audit.host.sha(Path(owner.__file__)),independentGoldenCases=fixtures,metadataCounterexamples=rejected,logicalInventoryDatasetUnchanged=True,historicalPhysicalDatasetUnchanged=True,productTestsExecuted=0,coverage=None,historicalCostsReallocated=False,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,goldenCases=len(fixtures),metadataCounterexamples=len(rejected),productPtExecuted=0,manifestSha256=audit.host.sha(out/'manifest.json'))))

if __name__=='__main__':
    main()
