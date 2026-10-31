"""Forty-seven current catch purposes, Source text only; no delivery, Graph, JMS or SQL call."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16345_jms_generic_twenty_purpose_v2 import byte_span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16345-jms-generic-twenty-purpose-v2','516fd56986dae16a471bebbec54e7f0cc2e6a94b8196a8578728a0456202991a')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
ADAPTER_POST=('PG16346-jms-generic-twenty-post-v1','9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814')
OUT=data.BASE/'PG16350-jms-delivery-log-fortyseven-purpose-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/ApiMessagingRuntime.java'
PREFIX='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'
REPLY=PREFIX+'messaging/ArtemisReplyConsumer.java'
REPLIES=PREFIX+'messaging/ArtemisReplyConsumers.java'
REQUEST=PREFIX+'messaging/ArtemisRequestSender.java'
LOG=PREFIX+'logging/WebLogMessageSender.java'
DISPATCH=PREFIX+'logging/WebLogDispatcher.java'
PINS={API:'b67514d342a8f3be8891bb30c003731a98a6dc484814f873dcdb8a85414f60ed',REPLY:'93599988b634badfe849f38f66abc4125ab5cc25e404c32fbda688f0060e101c',
    REPLIES:'134a6f35746447e6e27020ae8b82da5d67c136f0d20c46e94b41e5b8b81bc47f',REQUEST:'2478a0eb7438a76f10e15719fd9c647c899ec62895fdb8ba7a8e26d72bfc3e6c',
    LOG:'8299e7a3b9bef6f654b780dbd06d3831c3a137f806fafdc8e8e480c0473e3738',DISPATCH:'76b0c079bbc7704ccf64ee9a42acf88c0f9f4fc8fd461ff5d306d6ff48e11c66'}
KINDS={API:{184:'START_PRIMARY',190:'START_NOTIFICATION',200:'START_CLEANUP',245:'GROUP_CLOSE'},
    REPLY:{53:'REPLY_FAILURE_ROLLBACK',68:'DLQ_ISOLATION_FAILURE',86:'UNCONFIRMED_ROLLBACK'},
    REPLIES:{63:'REPLY_START_PRIMARY',67:'REPLY_START_CLEANUP',124:'DELIVERY_FAILURE',139:'SELECT_FATAL',153:'FATAL_ROLLBACK_UNCONFIRMED',181:'REPLY_OWNER_CLOSE'},
    REQUEST:{33:'REQUEST_AFTER_OWNED_CLOSE',73:'REQUEST_BODY_FAILURE',77:'REQUEST_PRIMARY_CAPTURE',88:'REQUEST_ROLLBACK_FAILURE',91:'REQUEST_DEFER_FATAL',102:'REQUEST_CLOSE'},
    LOG:{58:'LOG_SEND_FAILURE',64:'LOG_COMMIT_FAILURE',70:'LOG_DEFER_FATAL',77:'LOG_PRIMARY_CAPTURE',85:'LOG_LIFECYCLE_FAILURE',96:'LOG_CLOSE',109:'LOG_ROLLBACK_FAILURE',112:'LOG_ROLLBACK_DEFER_FATAL'},
    DISPATCH:{94:'SQL_BODY_FAILURE',98:'SQL_ROLLBACK_FAILURE',100:'SQL_ROLLBACK_FATAL',110:'SQL_PRIMARY_CAPTURE',122:'SQL_DISTINCT_CLOSE_FATAL'}}
PURPOSES={
    'START_PRIMARY':'Captures failed group startup, notifies terminal/fatal port, attempts captured runtime cleanup and applies the existing direct Error/graph boundary before fixed startup failure.',
    'START_NOTIFICATION':'Retains notification failure separately; a direct notification Error outranks a non-Error startup primary, otherwise non-self suppression preserves the existing carrier.',
    'START_CLEANUP':'Distinguishes cleanup Error from fixed wrapper cause; cleanup can outrank only a non-Error retained primary at this direct table, then raw graph dependencies remain outside this review.',
    'GROUP_CLOSE':'Attempts every unconfirmed group in reverse order, marks only successful close phases, retains the first direct Error and throws failure rather than whole runtime closed.',
    'REPLY_FAILURE_ROLLBACK':'Ordinary checked/runtime reply failure attempts rollback then rethrows; it is distinct from a successfully committed protocol isolation result.',
    'DLQ_ISOLATION_FAILURE':'Failed DLQ send/commit retains protocol failure context, attempts rollback and throws failed isolation/unconfirmed rollback carrier, never committed-fatal success.',
    'UNCONFIRMED_ROLLBACK':'A failing rollback preserves non-self secondary and throws UnconfirmedJmsRollbackException; completion observer runs only after normal rollback return.',
    'REPLY_START_PRIMARY':'Failed listener/start setup invokes owned runtime close, preserves original direct primary Error before graph classification and fixed startup failure.',
    'REPLY_START_CLEANUP':'Retains close failure independently; does not replace an existing direct primary Error with a cleanup Error, and does not mark the owner normally closed.',
    'DELIVERY_FAILURE':'Failure callback classifies selected fatal/isolation/rollback state; only confirmed nonfatal rollback may return for broker-controlled retry, not a fabricated ACK.',
    'SELECT_FATAL':'Captures the selected Error from graph classification for terminal notification and final identity rethrow; no graph execution occurs in this review.',
    'FATAL_ROLLBACK_UNCONFIRMED':'A single attempted fatal rollback may fail; its secondary is not allowed to replace the already selected Error or cause another rollback/ACK.',
    'REPLY_OWNER_CLOSE':'Context close runtime failure goes through the declared fatal classifier and fixed close error; closed becomes true only on normal return.',
    'REQUEST_AFTER_OWNED_CLOSE':'Public request classification follows sendOwned and its finally-owned close, preserving the established close priority before rethrow.',
    'REQUEST_BODY_FAILURE':'Checked/runtime send or commit failure attempts rollback and then propagates; outer primary capture/finally still owns close.',
    'REQUEST_PRIMARY_CAPTURE':'Records the checked/runtime/fatal primary before finally close; it is not a new send retry or success conversion.',
    'REQUEST_ROLLBACK_FAILURE':'Rollback secondary is delegated to attachment; selected fatal is deferred through a carrier so owned close is not skipped.',
    'REQUEST_DEFER_FATAL':'Carries the selected rollback/attachment Error and original failure through the outer finally-owned close, before public classification.',
    'REQUEST_CLOSE':'Fatal close outranks a non-Error primary only; existing direct primary Error is kept and other close failures delegate attachment.',
    'LOG_SEND_FAILURE':'Unconfirmed send attempts rollback and throws fixed WebLogSendException, leaving close and wire wiping in outer finally.',
    'LOG_COMMIT_FAILURE':'Commit failure attempts rollback and fatal inspection before duplicate-confirmed collapse; only the existing duplicate contract may treat confirmation as success.',
    'LOG_DEFER_FATAL':'Fatal classification before duplicate handling is carried as transport failure until owned close; no duplicate success is fabricated for this path.',
    'LOG_PRIMARY_CAPTURE':'Records transport/runtime/Error primary before owned context close; no dispatch database mark is performed here.',
    'LOG_LIFECYCLE_FAILURE':'Unconfirmed outer runtime lifecycle becomes fixed WebLogSendException while wire bytes are wiped; it is not a confirmed broker commit.',
    'LOG_CLOSE':'A direct close Error outranks non-Error primary, otherwise declared attachment preserves the sender-specific first-Error table.',
    'LOG_ROLLBACK_FAILURE':'Rollback secondary is attached or a selected Error is deferred to preserve owned-close ordering.',
    'LOG_ROLLBACK_DEFER_FATAL':'Transport carrier retains selected rollback fatal and original primary before finally-owned close; this is not a retry/ACK.',
    'SQL_BODY_FAILURE':'Action/commit SQL/runtime/Error failure records primary and attempts rollback before rethrow; the whole acquired connection is owned by outer finally.',
    'SQL_ROLLBACK_FAILURE':'SQL/runtime rollback secondary delegates attachment to the existing primary, not normal transaction completion.',
    'SQL_ROLLBACK_FATAL':'An existing direct primary Error remains primary; otherwise rollback Error carries the original primary and is rethrown.',
    'SQL_PRIMARY_CAPTURE':'Setup/body/rollback failure is recorded as the outer primary before connection close; commit success is not inferred after failure.',
    'SQL_DISTINCT_CLOSE_FATAL':'Dispatcher has a distinct contract: a different direct close Error outranks even another primary Error. This must not be normalized to the sender table.'}
CONTROLS={API:['varruntime=newApiMessagingRuntime(groups,terminal);','fatalSignal.run();','runtime.close();','if(retainedinstanceofErrorfatal)throwfatal;',
    'groups.get(index).close();groupClosed[index]=true;','closeGroups(groups,groupClosed);closed=true;'],
    REPLY:['context.commit();returncompleted;','rollbackAfterFailure(context,failure,attempted,confirmed);throwfailure;',
        'thrownewFailedJmsIsolationException(isolationFailure,protocolFailure);','attempted.run();','thrownewUnconfirmedJmsRollbackException(failure,rollbackFailure);','confirmed.run();'],
    REPLIES:['runtime.close();','if(failureinstanceofErrorfatal)throwfatal;','if(closingFailureinstanceofErrorfatal)throwfatal;',
        'rollbackAttempted.set(false);rollbackConfirmed.set(false);','&&rollbackConfirmed.get()){','rollbackAttempted.compareAndSet(false,true)',
        'if(selectedFatal!=null)throwselectedFatal;','context.close();','closed=true;'],
    REQUEST:['sendOwned(correlationId,encodedBody);','primary=exception;throwexception;','closeAfterFailure(context,primary);',
        'vardeferred=newIllegalStateException("JMSrequestrollbackfailed",fatal);','if(closinginstanceofErrorfatal&&!(primaryinstanceofError)){'],
    LOG:['context.commit();','WebStartupException.preserveFatal(failure);','if(!duplicateConfirmed(failure)){','primary=failure;throwfailure;',
        'closeAfterFailure(context,primary);','Arrays.fill(wire,(byte)0);','if(closinginstanceofErrorfatal&&!(primaryinstanceofError)){'],
    DISPATCH:['connection.setAutoCommit(false);','Tvalue=action.execute(connection);connection.commit();returnvalue;','connection.rollback();',
        'if(failureinstanceofError){WebStartupException.attachSecondary(failure,fatal);throwfailure;}',
        'closeAfterFailure(connection,primary);','if(closinginstanceofErrorfatal&&fatal!=primary){']}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def controls(path,text):
    compact=''.join(text.split());require(all(v in compact for v in CONTROLS[path]),'reviewed explicit source controls')
    if path==LOG:require(compact.index('WebStartupException.preserveFatal(failure);')<compact.index('if(!duplicateConfirmed(failure)){'),'fatal classification before duplicate collapse')
    if path==REPLIES:require(compact.index('if(failureinstanceofErrorfatal)throwfatal;')<compact.index('if(closingFailureinstanceofErrorfatal)throwfatal;'),'reply startup primary Error priority')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs,base,adapter_post=[read(v) for v in (PRIOR,OBS,BASE,ADAPTER_POST)]
    require(all(v['actualExit']==0 for v in (prior,obs,base,adapter_post)) and prior['source']==obs['source']==adapter_post['source']==SOURCE
            and adapter_post['utf8ByteNegativeVectors']==4,'qualified static chain and UTF8 adapter')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==172 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==148,'prior exact scope')
    selected=[v for v in queue if v['path'] in PINS];require(len(selected)==47 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'exact six Source warnings')
    observed={v['staticObservationId']:v for v in data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])}
    baseline=data.read_checked(data.BASE/BASE[0]/'findings.json',base['findingsSha256']);texts={p:(data.ROOT/p).read_text() for p in PINS};labels=[]
    for path,text in texts.items():
        require(data.sha(text.encode())==PINS[path],'whole Source unchanged');controls(path,text);compact=''.join(text.split())
        for number,marker in enumerate([CONTROLS[path][0],CONTROLS[path][1],CONTROLS[path][-1]]):
            require(marker in compact,'nondegenerate Source metadata variant');bad=compact.replace(marker,'REMOVED_SOURCE_CONTROL')
            try:controls(path,bad)
            except ValueError:labels.append(path+':'+str(number))
            else:raise ValueError('false source control variant')
    purposes=[]
    for row in selected:
        path=row['path'];o=observed[row['id']];matches=[v for v in baseline if v['path']==path and v['attributes']==row['attributes'] and v['sourceSha256']==row['sourceSha256']]
        require(len(matches)==1,'one original exact diagnostic');original=matches[0];kind=KINDS[path][int(row['attributes']['beginline'])]
        require(o['currentSource']==SOURCE and o['measurementDomain']=='UNCHANGED_MAIN_INPUT_PG13253' and o['sourceSha256']==row['sourceSha256']==PINS[path]
                and o['attributes']==original['attributes'] and o['message']==original['message'],'current Source/attrs/diagnostic origin')
        a,b,token=byte_span(texts[path],row['attributes']);require(token in {'RuntimeException','Exception','Error'} and texts[path].encode()[a:b]==token.encode(),'exact UTF8 type byte span')
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_DELIVERY_SEND_LOG_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Direct Source/manual policy only, no transitive Graph/provider/JMS/JDBC/Throwable cycle/commit-rollback-close/observer return/UNKNOWN-retention runtime assurance. No Root or real resource action.',
            baselineManifestSha256=BASE[1],baselineDiagnosticRowSha256=data.sha(wire(original)),baselineDiagnostic=original,originalDiagnosticSha256=data.sha(original['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='QUALIFIED_PMD_CHARACTER_TO_UTF8_BYTE_HALFOPEN_SPAN',
            dynamicGraphDependencyUnresolved=True,componentSpecificErrorPriorityRetained=True,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    clauses=len({(v['path'],v['attributes']['beginline']) for v in purposes});require(len(remaining)==125 and clauses==32,'47 warning rows/32 clauses, no PT count inflation')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';approved=(data.ROOT/design).read_bytes()
    require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    for v in (prior,obs,base,adapter_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASE[1],baselineFindingsSha256=base['findingsSha256'],adapterPostSha256=ADAPTER_POST[1],approvedDesignSha256=data.sha(approved),
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=47,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=195,combinedPurposeOrReferenceRows=1366,remainingSelectedUnreferenced=125,sourceCatchClauses=clauses,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
