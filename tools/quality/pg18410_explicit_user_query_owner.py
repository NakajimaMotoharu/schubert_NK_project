"""Qualify exact two Test-owner candidates from original explicit registration, not old PT success."""
import copy
import re
import g07_host_class_provenance_inputs as data
import trace_owner_join as original
import trace_owner_explicit_query_v2 as rules
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18410-explicit-user-query-owner-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    import json
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    old=data.read_checked(data.BASE/'PG9982-plain-core-trace-v1/manifest.json','ddca86f481cba3be23f37c2b2c4f580caf04ad0090670c8848ff755cada66855')
    prev=data.read_checked(data.BASE/'PG18388-current3008-weblog-claim-registry-v1/manifest.json','f561fa5e450285c6811f195c5a68670f1ddd090ef8782ce2a0815e6b1766b2b6')
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(old['actualExit']==prev['actualExit']==normal['actualExit']==0 and prev['source']==normal['source']==SOURCE and old['source']=='70165b0768a1fabd13371cc25a55978fcf3452ba','separate historical and current domains')
    old_rows={r['path']:r for r in old['sourceRows']};rows=[];labels=[]
    base_path=data.ROOT/'tools/quality/trace_owner_join.py'
    require(data.sha(base_path.read_bytes())=='f71ab155344149f6997937c00b62cbed161652c5f7dc9fabbeb11825f81bca75','old helper immutable')
    for path,(pin,basis) in rules.RULES.items():
        row=old_rows[path];blob=(data.ROOT/path).read_bytes()
        require(data.sha(blob)==row['sha256']==normal['begin']['inputHashes'][path]==prev['owners'][path]['sha256']==pin,'full original and current Test byte bridge')
        require(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P010-01' and row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' and row['mainSourceSubjects']==[rules.MAIN],'explicit candidate and original Main')
        require(row['currentSourcePtQualificationInferred'] is row['historicalCostsReallocated'] is row['historicalRunReassigned'] is False and row['additionalSharedCostPp']==0 and row['actualAllocatedPp'] is None,'no runtime/cost/acceptance from old record')
        names=re.findall(r'@Test\s+void\s+(\w+)\(',blob.decode())
        require(len(names)==len(row['methodTestIds'])==4 and len(set(names))==4,'complete explicit four methods, not executed')
        require(prev['owners'][path]['ownershipStatus']=='UNKNOWN','reproduce current missed candidate')
        resolved=rules.canonical(path,logical,pin)
        require(resolved==dict(canonicalOwner='WBS-P010-01',canonicalCostOwner='WBS-P010-01',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis=basis),'exact candidate expected')
        rows.append(dict(path=path,sha256=pin,previousOwner=prev['owners'][path],resolvedOwner=resolved,originalExplicitOwner=row['canonicalOwner'],independentSpecification=row['independentSpec'],methodTestIds=row['methodTestIds'],currentDeclaredMethods=names,oldRuntimeTransferred=False,additionalSharedCostPp=0,actualAllocatedPp=None))
        labels.append('positive-'+path.rsplit('/',1)[-1])
        for bad,label in [('0'*64,'wrong-hash'),(None,'null-hash')]:
            try:rules.canonical(path,logical,bad)
            except ValueError:labels.append(label+'-'+path.rsplit('/',1)[-1])
            else:raise ValueError('false source bridge')
    first=next(iter(rules.RULES));pin=rules.RULES[first][0]
    baseline=copy.deepcopy(logical);baseline[first]=dict(path=first,owner='WBS-P005-01',costOwner='WBS-P005-01')
    require(rules.canonical(first,baseline,pin)==original.canonical(first,baseline),'baseline always wins');labels.append('baseline-priority')
    for path in ['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQueryCanonicalCoreTest.java',rules.ROOT+'UnknownTest.java','src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ExistingMetricTest.java']:
        require(rules.canonical(path,logical,'0'*64)==original.canonical(path,logical),'all other old results unchanged');labels.append('unchanged-'+path.rsplit('/',1)[-1])
    for kind in ['missing','owner','cost']:
        broken=copy.deepcopy(logical)
        if kind=='missing':broken.pop(rules.MAIN)
        elif kind=='owner':broken[rules.MAIN]['owner']='WBS-F03'
        else:broken[rules.MAIN]['costOwner']='WBS-F03'
        try:rules.canonical(first,broken,pin)
        except ValueError:labels.append('reject-main-'+kind)
        else:raise ValueError('false Main basis')
    try:rules.RULES[first]=('0'*64,'WRONG')
    except TypeError:labels.append('immutable-rules')
    else:raise ValueError('mutable exact evidence rules')
    require(data.sha(base_path.read_bytes())=='f71ab155344149f6997937c00b62cbed161652c5f7dc9fabbeb11825f81bca75','original unchanged')
    helper=data.ROOT/'tools/quality/trace_owner_explicit_query_v2.py'
    verify(old['invocation']);verify(prev['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'owner-bridges.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,helperSha256=data.sha(helper.read_bytes()),originalHelperSha256='f71ab155344149f6997937c00b62cbed161652c5f7dc9fabbeb11825f81bca75',originalExplicitRegistrySha256='ddca86f481cba3be23f37c2b2c4f580caf04ad0090670c8848ff755cada66855',previousTechnicalRegistrySha256='f561fa5e450285c6811f195c5a68670f1ddd090ef8782ce2a0815e6b1766b2b6',normalManifestSha256='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3',ownerBridgesSha256=data.sha((OUT/'owner-bridges.json').read_bytes()),qualifiedToolVectors=len(labels),toolVectorLabels=labels,newlyResolvedCandidateOwners=2,newBaselineOwners=0,sourceChanged=False,oldRuntimeTransferred=False,productTestsExecuted=0,coverageExecuted=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(len(labels))
if __name__=='__main__':main()
