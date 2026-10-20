"""560 exact unchanged plus13 explicitly re-reviewed reasons, no old PASS import."""
import copy
import json
import os
from collections import Counter, defaultdict
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5990_web_contract_selected import OLD, PLAN, PLAN_SHA
from pg5994_web24_public import SOURCE, STATIC_SHA
from pg5910_storage_static_rebind import ordered_pairs
from pg5918_api_static_rebind import prior_disposition
from pg5758_static_rebind import bind_one
from pg5958_private_lock_reason_review import moved_pairs
from pg5982_web_static_rebind import references
from static_disposition_overlay import load

CATCH_SHA = 'adc3a1cb8f8af5fe68c2ce1538ee395b1fbac020b06286b556728c6e8070d644'
REFERENCE_SHA = 'f015ecf872d9e0c09796ef5555bd169f13fb34966629dd9f3d46c6991c59a62e'


def require_current_facts(fact):
    if fact.get('source') != SOURCE or any(type(fact.get(k)) is not int or fact[k] != 0 for k in ('actualExit','compileExit','independentFixtureExit')):
        raise ValueError('each same-current-source type/helper/fixture gate independently0')


def changed_reason(row, old, catches, identities):
    path=row['sourcePath'];rule=row['rule'];resolved=[]
    if rule=='DoNotUseThreads' and path.endswith(('/WebManagementServer.java','/WebHttpAdmission.java')):
        detail='Standalone existing loopback management executor/HTTP in-flight owner and interrupt status remain required outside a Jakarta EE container. Same executor count, bounds, completion and stop contracts; no thread policy or operational ownership is inferred.'
    elif rule=='AvoidCatchingGenericException' and path.endswith('/WebBrokerContexts.java'):
        resolved=[f for f in catches if f['path']==path and int(f['firstLine'])<=int(row['beginline'])<=int(f['lastLine'])]
        if len(resolved)!=1 or 'java.lang.Error' not in resolved[0]['type'] or any(resolved[0][k] != v for k,v in {'sameThrows':'1','otherThrows':'0','returns':'0','assignments':'0','finalDirect':'true'}.items()):
            raise ValueError('same current resolved fatal parameter directly rethrown before ordinary redaction')
        detail='Exact fatal Error parameter is directly rethrown before checked redaction; the TCP-port constant changes neither close lock nor exception identity. No normal return/retry/graph traversal is added.'
    elif rule=='CompareObjectsWithEquals' and path.endswith(('/EncryptedSessionRequestCache.java','/EncryptedWebSessionRepository.java')):
        resolved=[f for f in identities if f['path']==path and int(f['firstLine'])==int(row['beginline']) and int(f['lastLine'])==int(row['endline'])]
        if len(resolved)!=1 or resolved[0]['operator']!='NOT_EQUAL_TO':
            raise ValueError('one current reference inequality at the actual diagnostic')
        fact=resolved[0]
        if path.endswith('/EncryptedSessionRequestCache.java'):
            if (fact['leftType'],fact['rightType'],fact['rightExpression']) != ('java.lang.Object','dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository','sessions'):
                raise ValueError('exact configured repository instance, never equals-compatible foreign owner')
            detail='Reference equality authenticates the configured repository owner, not value equality; Ajax fixed string changes no repository binding or request-cache safety.'
        else:
            if (fact['leftType'],fact['rightType'],fact['leftExpression'],fact['rightExpression']) != ('java.lang.Throwable','java.lang.Throwable','failure','rollback'):
                raise ValueError('exact self-suppression identity guard, no exception graph comparison')
            detail='Reference inequality prevents self-suppression when rollback throws the same object; value equality would not preserve identity. Maximum-version constant leaves CAS/transaction/failure precedence unchanged.'
    else:
        raise ValueError('no unspecified changed-source reason transfer')
    value=copy.deepcopy(row);why=old['priorReason']+' Current b471 explicit re-review: '+detail
    value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition=old['priorDisposition'],reason=why,priorReason=why,
                 rawWarningRetained=True,currentWholeJoinPending=True,currentWholeCaseRefs=[],plannedCurrentTestRefs=references(old),historicalCaseIds=[],
                 currentTypeFacts=resolved,reviewSource=SOURCE,priorReviewSource=OLD,explicitCurrentSourceRereview=True,
                 implementationReviewedNoAdditionalChangeRequired=True,historicalPtImportedAsCurrent=False)
    return value


def main():
    bp=BASE/'PG5982-web-static-dispositions-v1/manifest.json';bsha='7c195396d242b237c2b254ebc07b544fd142663b9c2662758131b8795f665f97';oldrows=load(bp,bsha,OLD)
    sp=BASE/'PG5992-web-contract-static-v1/manifest.json'
    if sha(sp)!=STATIC_SHA or sha(PLAN)!=PLAN_SHA:
        raise ValueError('immutable actual current static/24 change declaration')
    public=json.loads(sp.read_bytes());raw=json.loads(sp.with_name('findings.json').read_bytes());plan=json.loads(PLAN.read_bytes())
    if not public['all24ExecutableProof']['allMethodDescriptorsAndSymbolicInstructionsEqual'] or len(public['all24ExecutableProof']['classes'])!=24:
        raise ValueError('all24 actual executable/descriptor equivalence, in addition to public ABI and nested proof')
    cp=W/'pg5998-current-catch-facts-v1/manifest.safe.json';rp=W/'pg6000-current-reference-facts-v1/manifest.safe.json'
    if sha(cp)!=CATCH_SHA or sha(rp)!=REFERENCE_SHA:
        raise ValueError('actual fresh current catch/reference resolved symbols')
    catches,identities=(json.loads(p.read_bytes()) for p in (cp,rp))
    for facts in (catches,identities):require_current_facts(facts)
    proofs=[]
    for name,pub,source in (('pg5978-web-form-static-v1',BASE/'PG5978-web-form-static-v1/manifest.json',OLD),('pg5992-web-contract-static-v1',sp,SOURCE)):
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
        path=declaration['path'];previous=W/'pg5984-web-form-selected921-v2/source'/path
        if sha(previous)!=declaration['beforeSha256'] or sha(ROOT/path)!=declaration['predictedAfterSha256']:raise ValueError('exact planned before/after source')
        pairs.update(moved_pairs(left[path],right[path],set(declaration['findingIds']),previous.read_text(),(ROOT/path).read_text()))
    decided={r['findingId']:r for r in oldrows if r['status']!='NOT_REVIEWED_CURRENT_SOURCE'};used=set();counts=Counter();result=[]
    for row in raw:
        pair=pairs.get(row['findingId']);old=decided.get(pair[0]['findingId']) if pair else None
        if old and row['sourcePath'] in changed:
            value=changed_reason(row,old,catches['rows'],identities['rows']);kind='EXPLICIT_CURRENT_REVIEW'
        else:
            value,kind=bind_one(row,[prior_disposition(old)] if old else [],(ROOT/row['sourcePath']).read_bytes(),before['auxClassHashes'],current['auxClassHashes'])
            if kind=='REBOUND':value.update(historicalCaseIds=[],plannedCurrentTestRefs=references(old),currentWholeCaseRefs=[],currentWholeJoinPending=True,historicalPtImportedAsCurrent=False)
        if kind in ('REBOUND','EXPLICIT_CURRENT_REVIEW'):
            used.add(old['findingId']);counts[kind]+=1;value.update(priorReviewManifestSha256=bsha,priorReviewSource=OLD,currentPhysicalProofSha256=sha(W/'pg5992-web-contract-static-v1/manifest.safe.json'),priorRawXmlOrdinal=old['rawXmlOrdinal'],sourceFileOccurrenceRank=pair[1])
        result.append(value)
    if len(result)!=1366 or len(used)!=573 or set(decided)-used or counts!=Counter(REBOUND=560,EXPLICIT_CURRENT_REVIEW=13):
        raise ValueError('all573 individually bound or re-reviewed;1366 raw retained;no dropped or duplicate reason')
    out=BASE/'PG5996-web-contract-dispositions-v1';os.umask(0o077);out.mkdir();fp=out/'findings.json'
    with fp.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=SOURCE,priorReviewSource=OLD,priorReviewManifestSha256=bsha,currentRawFindings=1366,inventoryFile='findings.json',inventorySha256=sha(fp),
               statusCounts=dict(Counter(r['status']for r in result)),bindingOutcomes=dict(counts),heldPriorDispositions=[],currentWholeJoinPending=True,
               historicalPtImportedAsCurrent=False,executedPtAdded=0,ptAlternativeCompleted=0,sourceCodeChanged=False,F03Accepted=False,formalAccepted=False,vmActions=0)
    with (out/'manifest.json').open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,unchanged560=560,rereviewed13=13,pending=573,unreviewed=793,raw=1366,manifestSha256=sha(out/'manifest.json'),inventorySha256=sha(fp))))


if __name__=='__main__':
    main()
