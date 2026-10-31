"""Seven Source-only purposes; never execute thread retention, kernel/readiness or publication."""
import re
import json
import xml.etree.ElementTree as ET
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16266-release-interrupt-two-purpose-v1','9afbe28a7e0fb0197b81c4a2da781a55b9d81dbccf41577ec0f60bc448434cd7')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
REPORTS=[('PG13505-main-assignment-seven-v1','aaa38f93d84f57a9ef670699063e6f290fc863326badd2db9d7a4592730929bf'),('PG13534-main-assignment-final-four-v1','36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda')]
OUT=data.BASE/'PG16291-thread-five-gonefd-two-purpose-v2'
PREFIX='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/'
PINS={'platform/FixedUnitCgroupNamespace.java':'96e4b3cfcdb5129e4f7a60e1395ef201a466cea5239d01b488ffd91049382345',
      'file/MorningPermitPublication.java':'e5b630dcdb19d95e5e99ddf55f97286dd9e652924096af1d978698c017c5fef2',
      'platform/MorningCaddyReadiness.java':'e5e4b289865f86279ec541a13753fa4cc44f8f8ccacbf9d28a9f8d92735ccb9d',
      'platform/MorningServiceReadiness.java':'bb546fa7c261e71d7d923eedbc7b5d64efda3ceff6e6c7f05e570e2e12acb617'}
SITES={('platform/FixedUnitCgroupNamespace.java',50):'INTERRUPTION_READ_BEFORE_CONTEXT',
       ('platform/FixedUnitCgroupNamespace.java',53):'INTERRUPTION_READ_AFTER_CONTEXT_AND_UID',
       ('file/MorningPermitPublication.java',75):'CAPTURE_CONSTRUCTION_THREAD_ID',
       ('file/MorningPermitPublication.java',242):'COMPARE_OWNER_THREAD_ID',
       ('file/MorningPermitPublication.java',309):'CLEAR_INTERRUPTION_INSIDE_INDEFINITE_RETENTION',
       ('platform/MorningCaddyReadiness.java',404):'DISAPPEARED_FD_NOT_OWNED_EVIDENCE',
       ('platform/MorningServiceReadiness.java',243):'DISAPPEARED_FD_NOT_OWNED_EVIDENCE'}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def raw_span(text,attrs):
    lines=text.splitlines(keepends=True);a,b=int(attrs['beginline'])-1,int(attrs['endline'])-1
    c,e=int(attrs['begincolumn'])-1,int(attrs['endcolumn'])-1
    require(0<=a<=b<len(lines) and 0<=c<len(lines[a]) and 0<=e<=len(lines[b]),'raw halfopen coordinate bounds')
    require(all(v.isascii() and '\t' not in v and '\x00' not in v for v in lines[a:b+1]),'raw target lines ASCII no tab/null')
    start=sum(len(v.encode()) for v in lines[:a])+len(lines[a][:c].encode())
    end=sum(len(v.encode()) for v in lines[:b])+len(lines[b][:e].encode())
    require(end>start,'positive raw span');return start,end,text.encode()[start:end].decode()

def check_text(short,text):
    compact=''.join(text.split())
    if short=='platform/FixedUnitCgroupNamespace.java':
        body=compact.split('voidcheck()throwsIOException{',1)[1].split('}Snapshotobserve(',1)[0]
        require(body=='require(!Thread.currentThread().isInterrupted());context.recheck();require(security.effectiveUid()==0);require(!Thread.currentThread().isInterrupted());','exact current-thread read/check order')
        require('if(!valid)thrownewIOException("maintenancecgroupnamespaceunavailable");' in compact,'fixed rejection')
    elif short=='file/MorningPermitPublication.java':
        require('privatefinallongthread=Thread.currentThread().threadId();' in compact
                and 'privatevoidowner()throwsIOException{require(thread==Thread.currentThread().threadId());}' in compact,'construction/owner thread-id pair')
        require('privatestaticvoidretainNative(){for(;;){java.util.concurrent.locks.LockSupport.parkNanos(java.util.concurrent.TimeUnit.SECONDS.toNanos(1));Thread.interrupted();' in compact,'retention park and actual clear, never claim read-only')
        require('Retainretain=MorningPermitPublication::retainNative;' in compact and 'retainedRetain.indefinitely();' in compact,'native retention dependency, not invoked')
    else:
        expected='catch (NoSuchFileException gone) {\n            /* '+('Never counts as owned evidence.' if 'Caddy' in short else 'Kernel FD closed; cannot become owned evidence.')+' */\n          }'
        require(text.count(expected)==1,'only missing FD empty catch with explicit non-evidence comment')
        require('Stringtarget=Files.readSymbolicLink(entry).toString();' in compact and 'descriptors.add(target.substring(8,target.length()-1));' in compact,'successful readlink/socket match only contributes')
        require('if(before.isEmpty())returnfalse;' in compact if 'Service' in short else 'if(sockets.isEmpty())returnfalse;' in compact,'no listeners cannot pass')
        require('returnbefore.stream().anyMatch(after::contains);' in compact if 'Service' in short else 'returnsockets.stream().anyMatch(after::contains);' in compact,'before/after shared socket required in Source')
    require(not re.search(r'new\s+Thread\b|Executors\s*\.',text),'no direct new worker in reviewed whole Source')

def saved_xml_rows():
    rows=[];refs=[]
    for folder,pin in REPORTS:
        m=read((folder,pin));require(m['actualExit']==m['productTestsExecuted']==0,'saved static only')
        blob=(data.BASE/folder/'pmd.xml').read_bytes();require(data.sha(blob)==m['reports']['pmd'],'original current-coordinate XML hash')
        refs.append(dict(manifest=folder,sha256=pin,pmdSha256=data.sha(blob),candidateSourceHashes={p:h for p,h in m['candidateSourceHashes'].items() if p in {PREFIX+k for k in PINS}}))
        for node in ET.fromstring(blob):
            if node.tag.rpartition('}')[2]!='file':continue
            name=node.get('name');marker='/src/schubert-nk-'
            require(marker in name,'public normal source marker');path=name[name.index(marker)+1:]
            if path not in {PREFIX+k for k in PINS}:continue
            for item in node:
                require(item.tag.rpartition('}')[2]=='violation','only raw diagnostic')
                attrs=dict(item.attrib);message=''.join(item.itertext()).strip()
                row=dict(path=path,attributes=attrs,message=message)
                rows.append(dict(**row,rawDiagnosticRowSha256=data.sha(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()),
                    rawReportManifest=folder,rawReportManifestSha256=pin,rawReportSha256=data.sha(blob),rawReportSource=m['source'],
                    rawCandidateSourceSha256=m['candidateSourceHashes'][path]))
        verify(m['invocation'])
    return rows,refs

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)];require(all(v['actualExit']==0 and v['source']==SOURCE for v in (prior,obs)),'current source')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==199 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==121,'prior finite domains')
    observed={v['staticObservationId']:v for v in data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])}
    raw,report_refs=saved_xml_rows()
    texts={short:(data.ROOT/(PREFIX+short)).read_text() for short in PINS}
    for short,text in texts.items():require(data.sha(text.encode())==PINS[short],'whole Source hash');check_text(short,text)
    selection=[v for v in queue if v['rule'] in {'DoNotUseThreads','EmptyCatchBlock'}]
    require({(v['path'].removeprefix(PREFIX),int(v['attributes']['beginline'])) for v in selection}==set(SITES) and len(selection)==7,'exact seven sites')
    labels=[]
    for short,text in texts.items():
        variants=[text.replace('Thread.currentThread().isInterrupted()','Thread.interrupted()'),text.replace('security.effectiveUid() == 0','security.effectiveUid() != 0')] if 'FixedUnit' in short else [text.replace('thread == Thread.currentThread().threadId()','thread != Thread.currentThread().threadId()'),text.replace('Thread.interrupted();','Thread.currentThread().isInterrupted();')] if 'Permit' in short else [text.replace('catch (NoSuchFileException gone)','catch (IOException gone)'),text.replace('/* Never counts as owned evidence. */' if 'Caddy' in short else '/* Kernel FD closed; cannot become owned evidence. */','descriptors.add("UNKNOWN");')]
        for number,bad in enumerate(variants):
            require(bad!=text,'nondegenerate metadata variant')
            try:check_text(short,bad)
            except ValueError:labels.append(short+'-'+str(number))
            else:raise ValueError('false purpose contract')
    purposes=[]
    for row in selection:
        short=row['path'].removeprefix(PREFIX);line=int(row['attributes']['beginline']);kind=SITES[short,line]
        current=observed[row['id']];matches=[v for v in raw if v['path']==row['path'] and v['attributes']==row['attributes']]
        require(len(matches)==1,'unique original attrs');old=matches[0]
        require(current['currentSource']==SOURCE and current['sourceSha256']==row['sourceSha256']==PINS[short]
                and current['attributes']==row['attributes'] and current['message']==old['message'] and old['rawCandidateSourceSha256']==PINS[short],'same whole current Source/raw diagnostic')
        start,end,token=raw_span(texts[short],row['attributes'])
        require(token=='Thread' if row['rule']=='DoNotUseThreads' else token.startswith('catch (NoSuchFileException gone) {') and token.endswith('}'),'exact raw token/block')
        retained=kind.startswith('CLEAR_');gone=kind.startswith('DISAPPEARED_')
        purpose=('Clears the interrupt flag after one-second parkNanos in an indefinite retention loop; preserves ownership for external hard deadline, not a read-only check or normal termination.' if retained else 'A missing FD at readSymbolicLink contributes no owned socket evidence; only NoSuchFileException is consumed, other IO failures propagate. Source ready requires nonempty and overlapping before/after socket sets.' if gone else 'Reads current interruption before or after context/UID checks, fixed rejection on interruption; no interrupt clearing.' if 'INTERRUPTION' in kind else 'Captures the construction thread identity and compares it at owner boundaries; rejects a different thread, not a substitute for capability or generation authentication.')
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',manualPurpose=purpose,
            residualRisk='Source-only direct shape, no type/CFG/all schedule/transitive provider proof, actual FD/PID reuse, kernel generation, socket/readiness, publication, abort/retirement, retention recovery or external deadline acceptance.',
            purposeKind=kind,interruptStateClearingAtSite=retained,indefiniteRetention=retained,externalDeadlineProven=False,directWorkerCreationAtSite=False,
            savedXmlDiagnosticRowSha256=old['rawDiagnosticRowSha256'],rawReportManifest=old['rawReportManifest'],rawReportManifestSha256=old['rawReportManifestSha256'],rawReportSha256=old['rawReportSha256'],rawReportSource=old['rawReportSource'],rawCandidateSourceSha256=old['rawCandidateSourceSha256'],originalDiagnosticSha256=data.sha(old['message'].encode()),
            canonicalSpanStart=start,canonicalSpanEndExclusive=end,canonicalSpanSha256=data.sha(token.encode()),spanBasis='RAW_HALFOPEN_ASCII_TARGET_LINES_NOT_AST_OR_JAVA_UNICODE_TRANSLATED_RANGE',
            productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';approved=(data.ROOT/design).read_bytes()
    require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    require(len(remaining)==192 and all(v['rule']=='AvoidCatchingGenericException' for v in remaining),'remaining generic only, not all F03 pass')
    for v in (prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes={PREFIX+k:v for k,v in PINS.items()},savedCurrentCoordinateReportReferences=report_refs,approvedDesignSha256=data.sha(approved),
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=7,newReferenceConnections=0,
        combinedSelectedReferences=1171,combinedPurposeReviewed=128,combinedPurposeOrReferenceRows=1299,remainingSelectedUnreferenced=192,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
