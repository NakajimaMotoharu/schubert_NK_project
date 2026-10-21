"""Exact current diagnostic/source/original-XML join; held operational scopes stay held."""
import copy
import inspect
import json
import os
import subprocess
import sys
from collections import Counter
import pg6674_current4170_static_join as prior
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5910_storage_static_rebind import ordered_pairs
from static_disposition_overlay import load,validate_rationales
from pg6708_original4184_artifacts import read_whole

OLD='f16f717d4e5338e7f5b44faef179ada0cf19aae0'
PRIOR=BASE/'PG6674-current4170-static-join-v1/manifest.json'
PRIOR_SHA='4ecb6700cc19f3df7a25190a9c7959869931164178851f97595c6e510e0b3d9f'
QSHA='9c92e0bf1ed2ef22826e41d53f42cd6916e5e0bf07c6f472a6717dfa3908f961'
EXPECTED_RAW=1404
EXPECTED_PAIRS=1250
CONTEXTS={k:v for k,v in prior.CONTEXTS.items() if k in (
    'SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers','ArtemisReplyConsumers')}
CONTEXTS.update(
 ApiBrokerContexts='SSC334: caller-owned context factory, copy wipe; fixed final catalog only after finite fatal graph. Pre-acquisition three-slot scratch keeps every close graph through all required reverse close attempts; raw partial primary/individual suppression table remains unchanged when retained.',
 ArtemisConnectionFactoryProvider='SSC334: twelve approved setter calls, one owned close on setup failure, legacy direct primary/cleanup table and raw primary identity; only unattached secondary invokes qualified fallback after normal UNKNOWN callback return.',
 ApiMessagingRuntime='SSC334: public assembly of real child cause carriers; startup notification and cleanup graphs classified only after all acquired groups close, close final guard after all reverse group attempts; successful phase is not closed again.',
 WebBrokerContexts='SSC334: copied credential is wiped in outer lock finally; fixed context/close catalog carries no provider graph, module JMS/SQL fatal classification precedes it; setup raw primary and one-close ownership remain unchanged.')
RULES=dict(prior.RULES)
RULES['AvoidCatchingGenericException']='Owned cleanup/startup or fixed diagnostic boundary: retain the approved raw carrier when its graph is preserved, otherwise classify the complete finite graph only after required cleanup. Catch never proves a successful rollback or release.'
SUPPLEMENT={k:list(v) for k,v in prior.SUPPLEMENT.items()}
for name,cases in {
 'SyncRequestConsumers':['api.messaging.inbound.ConsumerCleanup333Test'],
 'WebLogConsumers':['api.messaging.inbound.ConsumerCleanup333Test'],
 'QuestionWorkConsumers':['api.messaging.inbound.ConsumerCleanup333Test'],
 'ArtemisReplyConsumers':['web.messaging.ReplyCleanup333Test'],
 'ApiBrokerContexts':['api.messaging.config.BrokerGraph334Test','api.messaging.config.ApiFactoryOwnershipTest'],
 'ArtemisConnectionFactoryProvider':['api.messaging.config.BrokerGraph334Test','api.messaging.config.ApiFactoryOwnershipTest'],
 'ApiMessagingRuntime':['api.messaging.inbound.ParentGraph334Test','api.messaging.inbound.ApiMessagingRuntimeTest'],
 'WebBrokerContexts':['web.messaging.BrokerGraph334Test','web.messaging.WebBrokerFactoryOwnershipTest']}.items():
    SUPPLEMENT.setdefault(name,[]).extend(cases)


def bindings():
    scope={**vars(prior.prior),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    for name in ('rebind_unchanged','original_refs'):
        exec(compile(inspect.getsource(getattr(prior.prior,name)),'<current4184 '+name+'>','exec'),scope)
    return scope


def review_changed(row):
    name=row['sourcePath'].rsplit('/',1)[-1].removesuffix('.java');rule=row['rule']
    if name not in CONTEXTS or rule not in RULES:
        raise ValueError('only eight individually reviewed contexts and explicit diagnostic rules')
    text=(ROOT/row['sourcePath']).read_text();lines=text.splitlines();line=int(row['beginline'])
    snippet=' | '.join(lines[max(0,line-2):min(len(lines),int(row['endline'])+2)])
    words=prior.catch_words(text,line) if rule in ('AvoidCatchingGenericException','EmptyCatchBlock') else []
    if rule=='EmptyCatchBlock' and (words or 'rollback' not in '\n'.join(lines[max(0,line-5):line])):
        raise ValueError('only already-fatal best-effort rollback empty catch')
    if rule=='DoNotThrowExceptionInFinally' and (name!='ArtemisReplyConsumers' or 'selectedFatal' not in snippet):
        raise ValueError('only the approved selected-fatal notification finally')
    result=copy.deepcopy(row)
    result.update(status='CONTEXT_NOT_APPLICABLE' if rule=='CloseResource' else 'REQUIRED_CONTRACT',
      reason=CONTEXTS[name]+' '+RULES[rule]+' SSC333334 keeps unretained secondary graphs until required cleanup completes; direct-fatal priority and nonreturn UNKNOWN are not relaxed.',
      reviewedSourceSnippet=snippet,rawWarningRetained=True,ptAlternativeCompleted=0,
      reviewMethod='EXACT_CURRENT_SOURCE_SPAN_AND_COMPONENT_CONTRACT',formalAccepted=False,
      relatedQualityEvidence='1470/1471 and same-source original127/full4184; related regression only, not per-site fault causality')
    return result


def main():
    qp,q,cases=read_whole();source=q['productionSource'];old=load(PRIOR,PRIOR_SHA,OLD)
    sp=BASE/'PG6712-broker-parent-qualification-v3/manifest.json'
    if QSHA is None or sha(sp)!=QSHA:raise ValueError('freeze actual original127 raw static first')
    selected=json.loads(sp.read_bytes());pp=W/'pg6712-broker-parent-qualification-v3/manifest.safe.json';rp=pp.with_name('findings.safe.json')
    proof=json.loads(pp.read_bytes())
    if not(selected['source']==proof['source']==source and sha(pp)==selected['privateManifestSha256']
           and sha(rp)==selected['findingsSha256'] and proof['allSourceHashes']==q['allSourceHashes']
           and proof['allPhysicalMainSha256']==q['allPhysicalMainSha256']):
        raise ValueError('all8511667 same-source original static/whole')
    raw=json.loads(rp.read_bytes());pairs=ordered_pairs(old,raw)
    if EXPECTED_RAW is None or EXPECTED_PAIRS is None or (len(raw),len(pairs))!=(EXPECTED_RAW,EXPECTED_PAIRS):
        raise ValueError('freeze actual all raw/entire-file pairs after original qualification')
    scope=bindings();result=[];counts=Counter()
    for row in raw:
        if row['sourceSha256']!=q['allSourceHashes'][row['sourcePath']]:raise ValueError('each current raw source hash')
        pair=pairs.get(row['findingId'])
        if pair is None:
            value=review_changed(row);counts['currentChangedReviewed']+=1
        else:
            value=scope['rebind_unchanged'](row,pair[0]);counts['unchangedPriorHeld' if value['status']=='NOT_REVIEWED_CURRENT_SOURCE' else 'exactCurrentRationaleReauthenticated']+=1
        value=scope['original_refs'](value,cases,source)
        if value['status']!='NOT_REVIEWED_CURRENT_SOURCE':
            value.update(currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(qp.with_name('cases.json')))
        result.append(value)
    if [r['findingId'] for r in raw]!=[r['findingId'] for r in result]:raise ValueError('all current raw IDs/order retained')
    validate_rationales(result)
    out=BASE/'PG6716-current4184-static-join-v1';os.umask(0o077);out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(result,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=source,rawFindings=len(raw),inventoryFile='findings.json',inventorySha256=sha(out/'findings.json'),
      statusCounts=dict(Counter(r['status'] for r in result)),joined=dict(counts),priorManifestSha256=PRIOR_SHA,
      currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(qp.with_name('cases.json')),
      testsExecuted=0,pmdRawRemoved=0,checkstyleFindings=0,formalAccepted=False,F03Accepted=False,
      ptAlternativeCompleted=0,vmActions=0,newAcceptedLeaves=0,effortPercent=None,
      operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      toolSha256=sha(ROOT/'tools/quality/pg6716_current4184_static_join.py'),pythonVersion=sys.version.split()[0],
      command='python3 -B tools/quality/pg6716_current4184_static_join.py',wholeReplayed=False,additionalBuildsIssued=0)
    target=out/'manifest.json'
    with target.open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],manifestSha256=sha(target))))


if __name__=='__main__':main()
