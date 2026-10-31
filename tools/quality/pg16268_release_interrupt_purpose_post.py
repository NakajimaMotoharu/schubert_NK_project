"""Independent byte/line and direct-order checks for two Source-only interruption purposes."""
import copy
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16266_release_interrupt_two_purpose import SOURCE,PRIOR,OBS,RAW,PATH,CALLER,MAIN_PIN,CALLER_PIN,PREVIOUS_REVIEW,read

PIN='9afbe28a7e0fb0197b81c4a2da781a55b9d81dbccf41577ec0f60bc448434cd7'
OUT=data.BASE/'PG16268-release-interrupt-purpose-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,prior,obs,previous=[read(v) for v in [('PG16266-release-interrupt-two-purpose-v1',PIN),PRIOR,OBS,PREVIOUS_REVIEW]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (m,prior,obs,previous)),'same current source')
    purposes=data.read_checked(data.BASE/'PG16266-release-interrupt-two-purpose-v1/purposes.json',m['purposesSha256'])
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256']);by_id={v['id']:v for v in queue}
    after=data.read_checked(data.BASE/'PG16266-release-interrupt-two-purpose-v1/remaining-selected-review-queue.json',m['queueSha256'])
    require(data.sha((data.ROOT/PATH).read_bytes())==MAIN_PIN and data.sha((data.ROOT/CALLER).read_bytes())==CALLER_PIN
            and previous['currentSourceHashes']=={PATH:MAIN_PIN,CALLER:CALLER_PIN},'unchanged fully reviewed Sources')
    blob=(data.ROOT/PATH).read_bytes();lines=blob.splitlines(keepends=True);text=blob.decode()
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW)
    actual=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);actual={v['staticObservationId']:v for v in actual}
    require(len(purposes)==len({v['id'] for v in purposes})==2 and {v['directMethod']for v in purposes}=={'checked','read'},'two actual current method sites')
    guard=b'require(!Thread.currentThread().isInterrupted());';byte_vectors=[]
    for v in purposes:
        cur=by_id[v['id']];a=cur['attributes'];name=a['method'];require(all(v[k]==x for k,x in cur.items()) and a['beginline']==a['endline'],'whole current row')
        index=int(a['beginline'])-1;line=lines[index];column=line.index(b'Thread.currentThread().isInterrupted()')
        prefix=b''.join(lines[:index]);require((prefix+line).isascii() and b'\\u' not in prefix+line and b'\t' not in prefix+line,'explicit prefix not full escaped Source')
        start=len(prefix)+column;stop=start+6
        require(a['begincolumn']==str(column+1) and a['endcolumn']==str(column+6) and blob[start:stop]==b'Thread'
                and v['canonicalSpanStart']==start and v['canonicalSpanEndExclusive']==stop
                and v['canonicalSpanSha256']==data.sha(b'Thread'),'independent byte offset/length/hash')
        first='  private StartupReleaseManifest.Snapshot checked(' if name=='checked' else '  private FileValue read('
        last='\n  private void own(' if name=='checked' else '\n  private JarValue archive('
        body=text[text.index(first)+len(first):text.index(last)];compact=re.sub(r'\s+','',body)
        require(v['methodSourceSha256']==data.sha(body.encode()) and compact.count(guard.decode())==1,'exact enclosing method and guard count')
        callee='reader.checked(' if name=='checked' else 'channel.read('
        require(compact.index(guard.decode())<compact.index(callee) and not any(s in compact for s in ['newThread(','Thread.sleep(','Thread.interrupted(','Executors.']),'direct read order/no clearing or creation')
        if name=='read':require('while(true){'+guard.decode() in compact and compact.index('io.open(')<compact.index(guard.decode())
                and v['alreadyOpenedChannelPossible'] is v['perChunkGuard'] is True,'per-chunk check not pre-open guarantee')
        else:require(v['alreadyOpenedChannelPossible'] is v['perChunkGuard'] is False,'checked not file-channel lifecycle')
        require(v['directWorkerCreationAtSite'] is v['interruptStateClearingAtSite'] is v['ptExecutionExempt'] is False
                and v['productTestsExecuted']==0 and v['currentWholeCaseRefs']==[] and v['manualPurpose'] and v['residualRisk'],'source-only limited purpose')
        origins=[r for r in raw if r['path']==PATH and r['attributes']==cur['attributes']];require(len(origins)==1,'one original raw')
        origin=origins[0];observed=actual[v['id']]
        require(v['originalFindingId']==origin['id'] and v['originalRowSha256']==origin['rowSha256'] and v['originalInputSha256']==origin['inputSha256']
                and observed['currentSource']==SOURCE and observed['sourceSha256']==MAIN_PIN and observed['attributes']==cur['attributes']
                and observed['message']==origin['message'] and v['originalDiagnosticSha256']==data.sha(origin['message'].encode()),'old raw/current Source not silently transferred')
        byte_vectors.append(dict(method=name,line=index+1,start=start,endExclusive=stop,tokenSha256=data.sha(b'Thread')))
    require('if(!valid)thrownewStorageIoException(StorageIoException.Reason.UNAVAILABLE);' in re.sub(r'\s+','',text[text.index('  private static void require(boolean valid)'):]),'fixed rejection branch source')
    ids={v['id']for v in purposes};require(wire(after)==wire([v for v in queue if v['id']not in ids]) and len(after)==199,'exact old remaining rows')
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['priorManifestSha256']==PRIOR[1]
                and value['priorQueueSha256']==prior['queueSha256'] and value['previousWholeSourceReviewSha256']==PREVIOUS_REVIEW[1],'same proof chain')
        require(value['sourceHashes']=={PATH:MAIN_PIN,CALLER:CALLER_PIN} and value['approvedDesignSha256']==previous['approvedDesignSha256'],'all Source/design pins')
        require((value['newManualReviews'],value['newReferenceConnections'],value['combinedSelectedReferences'],value['combinedPurposeReviewed'],
                value['combinedPurposeOrReferenceRows'],value['remainingSelectedUnreferenced'])==(2,0,1171,121,1292,199),'two new purposes not references/PT')
        require(value['purposesSha256']==m['purposesSha256'] and value['queueSha256']==m['queueSha256']
                and value['directContractMetadataNegativeVectors']==8 and len(set(value['directContractNegativeLabels']))==8,'actual files and eight metadata changes')
        require(value['boundedAsciiPrefixSpans'] is value['wholeSourceHashPreserved'] is True
                and all(value[k] is False for k in ['ptExecutionExempt','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and value['actualReleaseVerificationOrSigningOrPublicationCalls']==value['productTestsExecuted']==value['rawSuppressed']==value['externalActions']==value['newAccepted']==0
                and value['actualViolationCount'] is value['effortPercent'] is None,'limited Source purpose, no actual effects')
    contract(m);labels=[]
    for key,value in [('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('previousWholeSourceReviewSha256','0'*64),
        ('sourceHashes',{}),('approvedDesignSha256','0'*64),('newManualReviews',0),('newReferenceConnections',2),('combinedSelectedReferences',1173),
        ('combinedPurposeReviewed',119),('combinedPurposeOrReferenceRows',1290),('remainingSelectedUnreferenced',201),('purposesSha256','0'*64),
        ('queueSha256','0'*64),('directContractMetadataNegativeVectors',0),('directContractNegativeLabels',[]),('boundedAsciiPrefixSpans',False),
        ('wholeSourceHashPreserved',False),('actualReleaseVerificationOrSigningOrPublicationCalls',1),('productTestsExecuted',2),('ptExecutionExempt',True),
        ('sourceChanged',True),('wholeF03Accepted',True),('formalUpdated',True),('actualViolationCount',0),('effortPercent',100)]:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false release interruption purpose '+key)
    require(len(labels)==26,'finite26')
    for v in (m,prior,obs,previous):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        metadataNegativeVectors=26,negativeLabels=labels,independentByteVectors=byte_vectors,underlyingDirectContractMetadataVectors=8,
        combinedSelectedReferences=1171,combinedPurposeReviewed=121,combinedPurposeOrReferenceRows=1292,remainingSelectedUnreferenced=199,
        newManualReviews=2,productTestsExecuted=0,actualReleaseVerificationOrSigningOrPublicationCalls=0,newAccepted=0,wholeF03Accepted=False,
        whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
