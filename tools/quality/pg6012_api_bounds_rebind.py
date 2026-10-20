"""626 exact unchanged plus10 explicitly re-reviewed reasons, no old PASS import."""
import copy
import json
import os
from collections import Counter, defaultdict
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6006_api_bounds_selected import OLD, PLAN, PLAN_SHA
from pg6010_api15_public import SOURCE, STATIC_SHA
from pg5910_storage_static_rebind import ordered_pairs
from pg5918_api_static_rebind import prior_disposition
from pg5758_static_rebind import bind_one
from pg5958_private_lock_reason_review import moved_pairs
from pg5982_web_static_rebind import references
from static_disposition_overlay import load

def changed_reason(row,old):
    path=row['sourcePath'];rule=row['rule']
    if rule=='DoNotUseThreads' and path.endswith(('/ApiManagementServer.java','/QuestionWorkerService.java')):
        detail='Existing standalone management executor/completion ownership or synchronous worker interrupt restoration remains outside a Jakarta EE container. Same private actor/thread policy and failure handling; no Root/process/Unit ownership or live provider condition is inferred.'
    elif rule=='UnusedReturnValue' and path.endswith('/RequestLogDetails.java'):
        text=(ROOT/path).read_text()
        if 'reader.setStrictness(Strictness.STRICT);' not in text or 'reader.endObject();' not in text or 'reader.peek();' not in text:
            raise ValueError('the exact strict post-root validation call must remain')
        detail='The post-root strict JsonReader.peek call is used for validation side effects and rejects trailing JSON; its return value is deliberately not an output value. The UTF8-byte bound constant changes neither strict reader scope nor the independent malformed/trailing fixture expectations.'
    elif rule=='UseConcurrentHashMap' and path.endswith('/AuthContextCodec.java'):
        text=(ROOT/path).read_text()
        if 'Map<String, byte[]> copies = new HashMap<>();' not in text or 'keys = Map.copyOf(copies);' not in text:
            raise ValueError('constructor-local map is copied before private final publication')
        detail='This constructor-local key-copy builder is not a shared mutable map; the published map remains Map.copyOf and the existing key-byte ownership/close lock remains unchanged. A concurrent map would not improve this local scope and is not required. The private AES32 constant changes no ownership or lifetime.'
    else:
        raise ValueError('no unspecified API changed-source reason transfer')
    value=copy.deepcopy(row);why=old['priorReason']+' Current bc0 explicit re-review: '+detail
    value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition=old['priorDisposition'],reason=why,priorReason=why,
        rawWarningRetained=True,currentWholeJoinPending=True,currentWholeCaseRefs=[],plannedCurrentTestRefs=references(old),historicalCaseIds=[],
        reviewSource=SOURCE,priorReviewSource=OLD,explicitCurrentSourceRereview=True,currentTypedMeasurementClaimed=False,
        implementationReviewedNoAdditionalChangeRequired=True,historicalPtImportedAsCurrent=False)
    return value


def main():
    bp=BASE/'PG6002-direct-jdbc-finally63-v1/manifest.json';bsha='ad81ef51ee6c97ec86f72266a3e8bfd8183cb4789b91cd00949395ba8fbfd181';oldrows=load(bp,bsha,OLD)
    sp=BASE/'PG6008-api-bounds-static-v1/manifest.json'
    if sha(sp)!=STATIC_SHA or sha(PLAN)!=PLAN_SHA:
        raise ValueError('immutable actual current static/24 change declaration')
    public=json.loads(sp.read_bytes());raw=json.loads(sp.with_name('findings.json').read_bytes());plan=json.loads(PLAN.read_bytes())
    if not public['all15ExecutableProof']['allMethodDescriptorsAndSymbolicInstructionsEqual'] or len(public['all15ExecutableProof']['classes'])!=15:
        raise ValueError('all24 actual executable/descriptor equivalence, in addition to public ABI and nested proof')
    proofs=[]
    for name,pub,source in (('pg5992-web-contract-static-v1',BASE/'PG5992-web-contract-static-v1/manifest.json',OLD),('pg6008-api-bounds-static-v1',sp,SOURCE)):
        path=W/name/'manifest.safe.json';v=json.loads(pub.read_bytes())
        if sha(path)!=v['privateManifestSha256']:raise ValueError('actual851/1666 private identity hash')
        proof=json.loads(path.read_bytes())
        if proof['source']!=source or proof['actualExit']!=0 or len(proof['allSourceHashes'])!=851 or len(proof['auxClassHashes'])!=1666:raise ValueError('actual fixed source/allMain proof')
        proofs.append(proof)
    before,current=proofs;left=defaultdict(list);right=defaultdict(list)
    for r in oldrows:left[r['sourcePath']].append(r)
    for r in raw:right[r['sourcePath']].append(r)
    pairs=ordered_pairs(oldrows,raw);changed={r['path'] for r in plan['sourcePlans']}
    for declaration in plan['sourcePlans']:
        path=declaration['path'];previous=W/'pg5990-web-contract-selected921-v1/source'/path
        if sha(previous)!=declaration['beforeSha256'] or sha(ROOT/path)!=declaration['predictedAfterSha256']:raise ValueError('exact planned before/after source')
        pairs.update(moved_pairs(left[path],right[path],set(declaration['findingIds']),previous.read_text(),(ROOT/path).read_text()))
    decided={r['findingId']:r for r in oldrows if r['status']!='NOT_REVIEWED_CURRENT_SOURCE'};used=set();counts=Counter();result=[]
    for row in raw:
        pair=pairs.get(row['findingId']);old=decided.get(pair[0]['findingId']) if pair else None
        if old and row['sourcePath'] in changed:
            value=changed_reason(row,old);kind='EXPLICIT_CURRENT_REVIEW'
        else:
            value,kind=bind_one(row,[prior_disposition(old)] if old else [],(ROOT/row['sourcePath']).read_bytes(),before['auxClassHashes'],current['auxClassHashes'])
            if kind=='REBOUND':value.update(historicalCaseIds=[],plannedCurrentTestRefs=references(old),currentWholeCaseRefs=[],currentWholeJoinPending=True,historicalPtImportedAsCurrent=False)
        if kind in ('REBOUND','EXPLICIT_CURRENT_REVIEW'):
            used.add(old['findingId']);counts[kind]+=1;value.update(priorReviewManifestSha256=bsha,priorReviewSource=OLD,currentPhysicalProofSha256=sha(W/'pg6008-api-bounds-static-v1/manifest.safe.json'),priorRawXmlOrdinal=old['rawXmlOrdinal'],sourceFileOccurrenceRank=pair[1])
        result.append(value)
    if len(result)!=1348 or len(used)!=636 or set(decided)-used or counts!=Counter(REBOUND=626,EXPLICIT_CURRENT_REVIEW=10):
        raise ValueError('all636 individually bound or re-reviewed;1348 raw retained;no dropped or duplicate reason')
    out=BASE/'PG6012-api-bounds-dispositions-v1';os.umask(0o077);out.mkdir();fp=out/'findings.json'
    with fp.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=SOURCE,priorReviewSource=OLD,priorReviewManifestSha256=bsha,currentRawFindings=1348,inventoryFile='findings.json',inventorySha256=sha(fp),
               statusCounts=dict(Counter(r['status']for r in result)),bindingOutcomes=dict(counts),heldPriorDispositions=[],currentWholeJoinPending=True,
               historicalPtImportedAsCurrent=False,executedPtAdded=0,ptAlternativeCompleted=0,sourceCodeChanged=False,F03Accepted=False,formalAccepted=False,vmActions=0)
    with (out/'manifest.json').open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,unchanged626=626,rereviewed10=10,pending=636,unreviewed=712,raw=1348,manifestSha256=sha(out/'manifest.json'),inventorySha256=sha(fp))))


if __name__=='__main__':
    main()
