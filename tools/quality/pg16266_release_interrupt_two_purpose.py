"""Two current-source cancellation-read purposes; no release, crypto, filesystem or Thread execution."""
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16199_release_collector_map3_purpose_v2 import bounded_span,PATH,CALLER,MAIN_PIN,CALLER_PIN

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16261-admission-saved12-reference-v2','17e8fc659e467506b6bbb5b7c01eb773f7f7d0166f9182326323df0de2845b31')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
PREVIOUS_REVIEW=('PG16199-release-collector-map3-purpose-v2','1e1efedd74db655a592a0e3f83f24bc92a5467a0e4329c8919f5cbfb99e10ecd')
OUT=data.BASE/'PG16266-release-interrupt-two-purpose-v1'
GUARD='require(!Thread.currentThread().isInterrupted());'
METHODS={'checked':('  private StartupReleaseManifest.Snapshot checked(', '\n  private void own('),
         'read':('  private FileValue read(', '\n  private JarValue archive(')}
PURPOSE='Reads the current caller interruption state without creating, starting, sleeping or clearing a Thread at this site. The exact require guard precedes reader.checked or each channel.read; false follows the fixed UNAVAILABLE source rejection, not a successful result.'
RISK='Source-only direct-order purpose: no type/CFG proof, callback transitive behavior, already-open channel avoidance, blocking-I/O completion, actual cancellation, parent deadline, ownership, signing, deployment or runtime acceptance.'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def method(text,name):
    first,last=METHODS[name];require(text.count(first)==text.count(last)==1,'unique explicit method boundary')
    return text.split(first,1)[1].split(last,1)[0]

def direct_contract(text,name):
    compact=''.join(text.split());callee='reader.checked(' if name=='checked' else 'channel.read('
    require(compact.count(GUARD)==1 and compact.count(callee)==1 and compact.index(GUARD)<compact.index(callee),'direct guard before relevant read')
    require(not re.search(r'\bnew\s+Thread\b|\bExecutors\s*\.|Thread\.(?:sleep|interrupted|startVirtualThread)\s*\(',text),'no direct worker creation/clearing/wait in reviewed method')
    if name=='read':require('while(true){'+GUARD in compact and 'ResourceScope.acquire(' in compact and 'SeekableByteChannel::close' in compact
            and compact.index('io.open(')<compact.index(GUARD),'each-chunk check, already-open possibility disclosed')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs,previous=[read(v) for v in (PRIOR,OBS,PREVIOUS_REVIEW)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (prior,obs,previous)) and previous['prefixMetadataNegativeVectors']==6
            and previous['prefixMetadataPositiveVectors']==1,'same Source and qualified bounded-prefix helper')
    body=(data.ROOT/PATH).read_text();caller=(data.ROOT/CALLER).read_text()
    require(data.sha(body.encode())==previous['currentSourceHashes'][PATH]==MAIN_PIN and data.sha(caller.encode())==previous['currentSourceHashes'][CALLER]==CALLER_PIN,'unchanged previously reviewed whole Main/caller')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==201 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==119,'separate prior domains')
    selected=[v for v in queue if v['path']==PATH and v['rule']=='DoNotUseThreads'];require(len(selected)==2,'exact two current sites')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observed={v['staticObservationId']:v for v in observed}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW)
    scopes={name:method(body,name) for name in METHODS}
    for name,text in scopes.items():direct_contract(text,name)
    reject=''.join(body[body.index('  private static void require(boolean valid)'):].split())
    require('if(!valid)thrownewStorageIoException(StorageIoException.Reason.UNAVAILABLE);' in reject,'fixed source failure, no success return')
    negatives=[]
    for name,text in scopes.items():
        compact=''.join(text.split());callee='reader.checked(' if name=='checked' else 'channel.read('
        variants=[('missing',compact.replace(GUARD,'')),('clearing',compact.replace('Thread.currentThread().isInterrupted()','Thread.interrupted()')),
                  ('worker','new Thread(() -> {});'+text),('late',compact.replace(GUARD,'').replace(callee,callee+'/*after-read*/')+GUARD)]
        for label,bad in variants:
            try:direct_contract(bad,name)
            except ValueError:negatives.append(name+'-'+label)
            else:raise ValueError('false interruption-purpose variant')
    purposes=[]
    for current in selected:
        name=current['attributes']['method'];require(name in scopes,'fixed actual methods')
        actual=observed[current['id']];original=[v for v in raw if v['path']==PATH and v['attributes']==current['attributes']]
        require(len(original)==1 and actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']==MAIN_PIN
                and actual['attributes']==current['attributes'] and actual['path']==PATH and actual['message']==original[0]['message'],'exact raw/current diagnostic and distinct Source binding')
        original=original[0];start,stop,token=bounded_span(body,current['attributes']);require(token=='Thread','exact reported token')
        purposes.append(dict(**current,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_INTERRUPTION_READ_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',
            manualPurpose=PURPOSE,residualRisk=RISK,directMethod=name,methodSourceSha256=data.sha(scopes[name].encode()),
            alreadyOpenedChannelPossible=name=='read',perChunkGuard=name=='read',directWorkerCreationAtSite=False,interruptStateClearingAtSite=False,
            originalFindingId=original['id'],originalRowSha256=original['rowSha256'],originalInputSha256=original['inputSha256'],
            originalDiagnosticSha256=data.sha(original['message'].encode()),canonicalSpanStart=start,canonicalSpanEndExclusive=stop,
            canonicalSpanSha256=data.sha(token.encode()),spanBasis='QUALIFIED_RAW_ASCII_PREFIX_BEFORE_LATER_UNICODE_ESCAPE',
            productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';approved=(data.ROOT/design).read_bytes()
    require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT)
            and data.sha(approved)==previous['approvedDesignSha256'],'same approved design, no specification change')
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    for v in (prior,obs,previous):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],
        sourceHashes={PATH:MAIN_PIN,CALLER:CALLER_PIN},previousWholeSourceReviewSha256=PREVIOUS_REVIEW[1],approvedDesignSha256=data.sha(approved),
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newManualReviews=2,newReferenceConnections=0,combinedSelectedReferences=1171,combinedPurposeReviewed=121,combinedPurposeOrReferenceRows=1292,
        remainingSelectedUnreferenced=199,directContractMetadataNegativeVectors=len(negatives),directContractNegativeLabels=negatives,
        boundedAsciiPrefixSpans=True,wholeSourceHashPreserved=True,actualReleaseVerificationOrSigningOrPublicationCalls=0,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,
        wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
