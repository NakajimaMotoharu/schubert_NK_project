"""Current raw1405 join, with explicit unsafe secondary spans held rather than approved."""
import copy
import inspect
import json
import os
import subprocess
import sys
from collections import Counter
import pg6640_current4158_static_join as prior
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5910_storage_static_rebind import ordered_pairs
from static_disposition_overlay import load,validate_rationales
from pg6542_jdbc_catch_inventory import LEX,balanced
from pg6670_original4170_artifacts import read_whole

OLD='2d4633fb25e2c47b2adcbada8c932aba727f20fd'
PRIOR=BASE/'PG6640-current4158-static-join-v1/manifest.json'
PRIOR_SHA='16bebde3503b8211ec3fb964411b6cf1376a6354fb1a66b32788af8ea279828e'
CONTEXTS={
 'SyncRequestConsumers':'Four distinct transacted contexts, per-delivery rollback phase proof; API fatal policy halts/notifies without rethrow after normal notification.',
 'WebLogConsumers':'One owned Web-log context; same-delivery confirmed nonfatal rollback only permits broker retry.',
 'QuestionWorkConsumers':'One owned work context; same-delivery confirmed nonfatal rollback only permits broker retry.',
 'ArtemisReplyConsumer':'Public exception identity/checked signature retained; internal synchronous attempted/confirmed ports do not own transactions.',
 'ArtemisReplyConsumers':'Reply owner has pre-acquisition phase ports, per-delivery reset, no duplicate rollback, selected Error identity after notification.',
 'WebRequestLogProducer':'SQL projection guard and local logger/callback graph after one existing owner signal; fixed nonfatal diagnostics/redaction retained.'}
RULES={
 'AvoidCatchingGenericException':'Required typed resource/rollback/fatal boundary; ordinary retry needs affirmative rollback completion and finite nonfatal graph.',
 'AvoidInstanceofChecksInCatchClause':'Explicit approved phase/direct-primary/direct-cleanup discriminator, not permission to infer successful rollback from a catch type.',
 'CompareObjectsWithEquals':'Throwable reference identity, never value equality, controls self-suppression and the approved direct-fatal precedence.',
 'CloseResource':'Ownership transfers into the retained consumer runtime before delivery; caller closes explicitly and partial startup closes acquired contexts. A lexical try-with-resources at acquisition would close the live consumer prematurely.',
 'AvoidUsingVolatile':'The owner readiness/stop state is visible across callback and stop callers; private lifecycle lock and atomic terminal guard remain authoritative.',
 'AvoidSynchronizedStatement':'The private close lock serializes owned context cleanup/retry; no caller-supplied monitor is used.',
 'EmptyCatchBlock':'Best-effort rollback already follows fatal halt; failure cannot authorize ACK/retry/reopen, and the outer owner retains cleanup. The selected fatal/nonzero path is not converted to success.',
 'DoNotThrowExceptionInFinally':'SSC332 explicitly keeps the selected Error after exactly one notification attempt, including notification failure. This finally performs no resource close and skips no remaining owned cleanup.'}
SUPPLEMENT={**prior.SUPPLEMENT,
 'SyncRequestConsumers':['api.messaging.inbound.ConsumerGraph332Test','api.messaging.inbound.ConfirmedRollbackCallbackTest','api.messaging.inbound.ConsumerRollbackUnconfirmedContractTest'],
 'WebLogConsumers':['api.messaging.inbound.ConsumerGraph332Test','api.messaging.inbound.ConfirmedRollbackCallbackTest'],
 'QuestionWorkConsumers':['api.messaging.inbound.ConsumerGraph332Test','api.messaging.inbound.ConsumerRollbackUnconfirmedContractTest'],
 'ArtemisReplyConsumer':['web.messaging.ReplyConsumerGraph332Test','web.messaging.ReplyRollbackSignalContractTest'],
 'ArtemisReplyConsumers':['web.messaging.ReplyConsumerGraph332Test','web.messaging.ReplyRollbackSignalContractTest','web.messaging.ReplyRollbackUnconfirmedContractTest'],
 'WebRequestLogProducer':['web.logging.LocalAuditGraph331Test','web.logging.RequestProjectionFailureGraph329Test']}


def bindings():
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    for name in ('rebind_unchanged','original_refs'):
        exec(compile(inspect.getsource(getattr(prior,name)),'<current4170 '+name+'>','exec'),scope)
    return scope


def catch_words(text,line):
    tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    matches=[]
    for at,(word,offset) in enumerate(tokens):
        if word!='catch':continue
        end=balanced(tokens,at+1,'(',')')
        first=text.count('\n',0,offset)+1;last=text.count('\n',0,tokens[end][1])+1
        if first<=line<=last:
            final=balanced(tokens,end+1,'{','}')
            matches.append([w for w,_ in tokens[end+2:final]])
    if len(matches)!=1:raise ValueError('PMD type location must belong to one exact catch header')
    return matches[0]


def review_changed(row):
    name=row['sourcePath'].rsplit('/',1)[-1].removesuffix('.java')
    if name not in CONTEXTS or row['rule'] not in RULES:raise ValueError('explicit six contexts and individually reviewed rules only')
    text=(ROOT/row['sourcePath']).read_text();lines=text.splitlines();line=int(row['beginline']);rule=row['rule']
    snippet=' | '.join(lines[max(0,line-2):min(len(lines),int(row['endline'])+2)])
    words=catch_words(text,line) if rule in ('AvoidCatchingGenericException','EmptyCatchBlock') else []
    # BUG1604: do not call unqualified suppression-disabled startup/multi-close spans required.
    unsafe=(name in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers','ArtemisReplyConsumers')
            and ((rule=='AvoidCatchingGenericException' and ('addSuppressed' in words or 'closeAfterFailure' in words))
                 or (rule=='CompareObjectsWithEquals' and 'addSuppressed' in snippet)))
    result=copy.deepcopy(row)
    if unsafe:
        result.update(status='NOT_REVIEWED_CURRENT_SOURCE',reviewHold='BUG1604_SUPPRESSION_DISABLED_SECONDARY_GRAPH_PENDING',
            reason='BUG1604/YKT1357: startup or multi-close can discard secondary Error when suppression is disabled. Existing full regression is not a counterexample fix or an exception approval.',
            reviewedSourceSnippet=snippet,relatedBug='BUG-1604',relatedYkt='YKT-1357',rawWarningRetained=True)
        return result
    if rule=='EmptyCatchBlock' and (words or 'rollback' not in '\n'.join(lines[max(0,line-5):line])):
        raise ValueError('only explicit already-fatal best-effort rollback may have empty handling')
    if rule=='DoNotThrowExceptionInFinally' and (name!='ArtemisReplyConsumers' or 'selectedFatal' not in snippet):
        raise ValueError('one explicit selected-fatal notification finally')
    status='CONTEXT_NOT_APPLICABLE' if rule=='CloseResource' else 'REQUIRED_CONTRACT'
    result.update(status=status,reason=CONTEXTS[name]+' '+RULES[rule],reviewedSourceSnippet=snippet,
        rawWarningRetained=True,ptAlternativeCompleted=0,reviewMethod='EXACT_CURRENT_SOURCE_SPAN_AND_COMPONENT_CONTRACT',formalAccepted=False)
    return result


def main():
    qp,q,cases=read_whole();source=q['productionSource'];old=load(PRIOR,PRIOR_SHA,OLD)
    sp=BASE/'PG6666-consumer-graph-qualification-v2/manifest.json'
    if sha(sp)!='dc608c847f6f03f31adabdb70b1fc28366472ae77d5c18f36c9a29f518de2edd':raise ValueError('original77 raw static first')
    selected=json.loads(sp.read_bytes());pp=W/'pg6666-consumer-graph-qualification-v2/manifest.safe.json';rp=pp.with_name('findings.safe.json')
    proof=json.loads(pp.read_bytes())
    if not(selected['source']==proof['source']==source and sha(pp)==selected['privateManifestSha256']
           and sha(rp)==selected['findingsSha256'] and proof['allSourceHashes']==q['allSourceHashes']
           and proof['allPhysicalMainSha256']==q['allPhysicalMainSha256']):raise ValueError('all8511667 same-source original static/whole')
    raw=json.loads(rp.read_bytes());pairs=ordered_pairs(old,raw)
    if len(raw)!=1405 or len(pairs)!=1293:raise ValueError('all raw1405/entire-file exact1293/new112')
    scope=bindings();result=[];counts=Counter()
    for row in raw:
        if row['sourceSha256']!=q['allSourceHashes'][row['sourcePath']]:raise ValueError('each current raw source hash')
        pair=pairs.get(row['findingId'])
        if pair is None:
            value=review_changed(row);counts['currentChangedReviewedOrHeld']+=1
        else:
            value=scope['rebind_unchanged'](row,pair[0]);counts['unchangedPriorHeld' if value['status']=='NOT_REVIEWED_CURRENT_SOURCE' else 'exactCurrentRationaleReauthenticated']+=1
        value=scope['original_refs'](value,cases,source)
        if value['status']!='NOT_REVIEWED_CURRENT_SOURCE':value.update(currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(qp.with_name('cases.json')))
        result.append(value)
    if [r['findingId'] for r in raw]!=[r['findingId'] for r in result]:raise ValueError('every current raw ID/order retained')
    validate_rationales(result)
    out=BASE/'PG6674-current4170-static-join-v1';os.umask(0o077);out.mkdir()
    with (out/'findings.json').open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=source,rawFindings=1405,inventoryFile='findings.json',inventorySha256=sha(out/'findings.json'),
        statusCounts=dict(Counter(r['status'] for r in result)),joined=dict(counts),priorManifestSha256=PRIOR_SHA,
        currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(qp.with_name('cases.json')),
        testsExecuted=0,pmdRawRemoved=0,checkstyleFindings=0,formalAccepted=False,F03Accepted=False,
        ptAlternativeCompleted=0,vmActions=0,newAcceptedLeaves=0,effortPercent=None,
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        toolSha256=sha(ROOT/'tools/quality/pg6674_current4170_static_join.py'),pythonVersion=sys.version.split()[0],
        command='python3 -B tools/quality/pg6674_current4170_static_join.py',wholeReplayed=False,additionalBuildsIssued=0)
    target=out/'manifest.json'
    with target.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],manifestSha256=sha(target))))


if __name__=='__main__':main()
