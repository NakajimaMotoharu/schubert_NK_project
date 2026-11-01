"""Own metadata-resolver tests only; no Product or original JUnit execution."""
import copy
import dataclasses
import json
import g07_host_class_provenance_inputs as data
import trace_owner_explicit_registry_v3 as resolver
import trace_owner_explicit_query_v2 as prior
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18432-explicit-owner-rules24-qualified-v1'
PREFLIGHT=('PG18430-explicit-same-byte24-owner-preflight-v1','7117274b0623981b644cc3ae4413f14b460187a312ff07fbf30fb0e75f972d3e')
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(data.BASE/PREFLIGHT[0]/'manifest.json',PREFLIGHT[1])
    rows=data.read_checked(data.BASE/PREFLIGHT[0]/'selected-owner-bridges.json',p['selectedBridgesSha256'])
    blob=(data.BASE/'PG9982-plain-core-trace-v1/manifest.json').read_bytes()
    paths=tuple(r['path'] for r in rows);rules=resolver.from_original_bytes(blob,paths)
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    labels=[]
    for row in rows:
        resolved=resolver.canonical(row['path'],logical,row['sha256'],rules)
        require(resolved==row['resolvedCandidate'],'24 exact explicit normal candidates')
        labels.append('candidate-'+row['path'])
    first=paths[0];pin=rows[0]['sha256']
    baseline=copy.deepcopy(logical);baseline[first]=dict(path=first,owner='WBS-F02',costOwner='WBS-F02')
    require(resolver.canonical(first,baseline,pin,rules)==prior.canonical(first,baseline,pin),'baseline priority');labels.append('baseline-priority')
    core=prior.ROOT+'UserQueryCanonicalCoreTest.java';corepin=prior.RULES[core][0]
    require(resolver.canonical(core,logical,corepin,rules)==prior.canonical(core,logical,corepin),'old exact query rule unchanged');labels.append('prior-query-rule')
    metric='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ExistingMetricTest.java'
    require(resolver.canonical(metric,logical,'0'*64,rules)==prior.canonical(metric,logical,'0'*64),'old monitoring rule unchanged');labels.append('prior-monitoring-rule')
    for path,pin,label in [(first,'0'*64,'changed-sha-stays-unknown'),(first,None,'missing-sha-stays-unknown'),('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/UnregisteredTest.java','0'*64,'unknown-path')]:
        require(resolver.canonical(path,logical,pin,rules)['ownershipStatus']=='UNKNOWN','no guessed or historical owner transfer');labels.append(label)
    rejected=[]
    for content,selected,label in [(blob+b' ',paths,'wrong-full-hash'),(bytearray(blob),paths,'mutable-blob'),(blob,(),'empty-paths'),(blob,(first,first),'duplicate-path'),(blob,('src/schubert-nk-api/src/test/java/UnknownTest.java',),'unregistered-path'),(blob,('src/schubert-nk-api/src/test/java/RootFailedStartRecoveryTest.java',),'held-root-name'),(blob,('src/schubert-nk-api/private/Private.java',),'private-path'),(blob,('src/schubert-nk-api/../Other.java',),'traversal'),(blob,(None,),'null-path'),(blob,tuple('src/schubert-nk-api/'+str(n)+'.java' for n in range(25)),'scope-overflow')]:
        try:resolver.from_original_bytes(content,selected)
        except ValueError:rejected.append(label)
        else:raise ValueError('false factory '+label)
    try:rules.entries[first]=('0'*64,'WBS-F03','WRONG')
    except TypeError:rejected.append('immutable-entry-map')
    else:raise ValueError('mutable rule map')
    try:rules.registry_sha256='0'*64
    except dataclasses.FrozenInstanceError:rejected.append('immutable-rule-record')
    else:raise ValueError('mutable record')
    try:resolver.canonical(first,logical,pin,None)
    except ValueError:rejected.append('unverified-rules')
    else:raise ValueError('missing verified metadata')
    require(data.sha((data.ROOT/'tools/quality/trace_owner_explicit_registry_v3.py').read_bytes())==p['resolverSourceSha256'],'executed resolver immutable')
    require(data.sha((data.ROOT/'tools/quality/trace_owner_join.py').read_bytes())=='f71ab155344149f6997937c00b62cbed161652c5f7dc9fabbeb11825f81bca75','old helper immutable')
    verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,preflightManifestSha256=PREFLIGHT[1],resolverSourceSha256=p['resolverSourceSha256'],selectedBridgesSha256=p['selectedBridgesSha256'],positiveAndPriorityVectors=len(labels),positiveLabels=labels,negativeAndImmutabilityVectors=len(rejected),negativeLabels=rejected,qualifiedCandidatePaths=24,trustedLocalMetadataApiNotSecurityGrant=True,oldRulesPreserved=True,all24SameCurrentBytes=True,oldRuntimeTransferred=False,productTestsExecuted=0,coverageExecuted=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(positive=len(labels),negative=len(rejected))))
if __name__=='__main__':main()
