"""Eighteen changed-Main catch purposes from original current-coordinate XML; Source metadata only."""
import subprocess
import g07_host_class_provenance_inputs as data
import pg16291_thread_five_gonefd_two_purpose_v2 as coordinates
from pg16345_jms_generic_twenty_purpose_v2 import byte_span
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16374-maintenance-jdbc-nineteen-purpose-v1','5a07285c8e9198df00f7cb8825127a68f3836518590cfdfdcad78db135ec8e2e')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
COORDINATE=('PG16291-thread-five-gonefd-two-purpose-v2','657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1')
OUT=data.BASE/'PG16380-batch-phase-eighteen-purpose-v1'
PREFIX="src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/"
PINS={
  "file/StartupAdmissionFile.java": "55fdbf46c65a1622f10f19e9ff018b8676c1d3b5a2dcf3ecc80ca5758637c61a",
  "platform/FixedUnitCgroupNamespace.java": "96e4b3cfcdb5129e4f7a60e1395ef201a466cea5239d01b488ffd91049382345",
  "file/MorningBackupArtifacts.java": "6adcab52b4556a1ad56dfef2a5e98dfb986773793b1b32f85c11fea7f459d35e",
  "file/MorningPermitPublication.java": "e5b630dcdb19d95e5e99ddf55f97286dd9e652924096af1d978698c017c5fef2"
}
KINDS={
  "file/StartupAdmissionFile.java": {
    "287": "REVERSE_UNKNOWN",
    "303": "REVERSE_UNKNOWN_AFTER_IO",
    "320": "REVERSE_DRAIN_SECONDARY"
  },
  "platform/FixedUnitCgroupNamespace.java": {
    "178": "FORWARD_UNKNOWN",
    "193": "FORWARD_UNKNOWN_AFTER_IO",
    "209": "FORWARD_DRAIN_SECONDARY"
  },
  "file/MorningBackupArtifacts.java": {
    "548": "BACKUP_BYTES_FAILURE"
  },
  "file/MorningPermitPublication.java": {
    "209": "PUBLICATION_UNSTARTED_CLOSE",
    "236": "PUBLICATION_ABORT_UNCONFIRMED"
  }
}
PURPOSES={
  "REVERSE_UNKNOWN": "Startup view consumes ownership once before reverse FD close; first unchecked/Error primary drains every remaining lower index, appends fixed secondary observations only after drain, then rethrows primary. Consumption is not kernel close success.",
  "REVERSE_UNKNOWN_AFTER_IO": "After initial known StorageIoException, a later unknown supersedes it; remaining lower FDs are attempted before suppression allocation/inspection. Multiple known I/O failures normalize to fixed UNAVAILABLE.",
  "REVERSE_DRAIN_SECONDARY": "Remaining reverse close IO/runtime/Error is recorded as primitive failure flag only; all later attempts precede fixed secondary attachment. No repeated native FD close or successful release is inferred.",
  "FORWARD_UNKNOWN": "Cgroup owner uses its existing forward FD order, consumes once, drains higher indices before fixed secondary attachment and same primary rethrow. Must not normalize to reverse startup-view order.",
  "FORWARD_UNKNOWN_AFTER_IO": "A later forward unknown supersedes preceding known I/O, drains remaining higher indices then rethrows unknown; known-only failure retains original reason only without multiple/suppressed uncertainty.",
  "FORWARD_DRAIN_SECONDARY": "Forward drain records primitive flags for any IO/runtime/Error and continues remaining ownership attempts; later fixed secondary diagnostics are not successful native release.",
  "BACKUP_BYTES_FAILURE": "Owned byte array is zeroed on IO/runtime/Error including input/TWR-close failure before propagating original. Success hands buffer to caller; this does not prove immutable copies/real credential erasure or actual Backup.",
  "PUBLICATION_UNSTARTED_CLOSE": "Abort before issue attempts intent-owner close; only normal return marks aborted. Uncertain IO/runtime/Error enters retained ownership rather than successful abort/unwind; no actual intent action is executed here.",
  "PUBLICATION_ABORT_UNCONFIRMED": "Started abort supervises fresh fixed recovery/quarantine/same-attempt revoke/readback and original close. Any uncertainty retains owner indefinitely under existing external deadline contract; Source review proves neither authority nor real retirement."
}
CONTROLS={
  "file/StartupAdmissionFile.java": [
    "closed=true;",
    "drain(index-1);appendSecondary(primary);throwprimary;",
    "secondaryFailures[index]=true;",
    "for(intindex=count-1;index>=0;index--)"
  ],
  "platform/FixedUnitCgroupNamespace.java": [
    "closed=true;",
    "drain(index+1);appendSecondary(primary);throwprimary;",
    "secondaryFailures[index]=true;",
    "for(intindex=0;index<count;index++)"
  ],
  "file/MorningBackupArtifacts.java": [
    "byte[]owned=newbyte[size];",
    "require(input.read(ByteBuffer.allocate(1))==-1&&input.size()==size);",
    "Arrays.fill(owned,(byte)0);throwfailure;"
  ],
  "file/MorningPermitPublication.java": [
    "if(!started){try{intents.close();aborted=true;",
    "retainedExpected=invalid;intents.close();aborted=true;",
    "retainedRetain.indefinitely();",
    "thrownewIllegalStateException(\"publicationownerretentionreturned\");"
  ]
}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def controls(short,text):
    compact=''.join(text.split());require(all(v in compact for v in CONTROLS[short]),'explicit ownership/control policy')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs,coordinate=[read(v) for v in (PRIOR,OBS,COORDINATE)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (prior,obs,coordinate)),'current Source evidence chain')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==50 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==270,'prior exact domains')
    observations={v['staticObservationId']:v for v in data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])}
    coordinates.PINS=PINS
    original,reports=coordinates.saved_xml_rows()
    texts={short:(data.ROOT/(PREFIX+short)).read_text() for short in PINS};negative=[]
    for short,text in texts.items():
        require(data.sha(text.encode())==PINS[short],'entire current Source byte');controls(short,text);compact=''.join(text.split())
        for n,marker in enumerate([CONTROLS[short][0],CONTROLS[short][1],CONTROLS[short][-1]]):
            require(marker in compact,'nondegenerate Source metadata')
            try:controls(short,compact.replace(marker,'REMOVED_SOURCE_CONTROL'))
            except ValueError:negative.append(short+':'+str(n))
            else:raise ValueError('false source control accepted')
    selected=[v for v in queue if v['path'] in {PREFIX+k for k in PINS}]
    require(len(selected)==18 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'all eighteen warnings')
    purposes=[]
    for row in selected:
        short=row['path'].removeprefix(PREFIX);current=observations[row['id']]
        matches=[v for v in original if v['path']==row['path'] and v['attributes']==row['attributes']]
        require(len(matches)==1,'unique current-coordinate original diagnostic');old=matches[0]
        require(current['currentSource']==SOURCE and current['measurementDomain']=='SAVED_EXACT_BYTE_EIGHT_MAIN_PG13505_13534'
                and current['sourceSha256']==row['sourceSha256']==PINS[short]==old['rawCandidateSourceSha256']
                and current['attributes']==row['attributes'] and current['message']==old['message'],'whole Source/attrs/diagnostic exact, no old coordinate reuse')
        kind=KINDS[short][row['attributes']['beginline']]
        a,b,token=byte_span(texts[short],row['attributes'])
        require(token in {'RuntimeException','Error'} and texts[short].encode()[a:b]==token.encode(),'exact UTF8 type byte')
        purposes.append(dict(**row,currentSource=SOURCE,purposeKind=kind,manualPurpose=PURPOSES[kind],
            reviewStatus='CURRENT_STATIC_BATCH_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',
            residualRisk='Direct Source policy only, no actual FD/native/Backup/credential/publication/revoke/intent recovery/retirement/Root ownership, retained-frame lifetime, callback return or external-deadline acceptance.',
            rawDiagnostic=old,spanBasis='QUALIFIED_PMD_CHARACTER_TO_UTF8_BYTE_HALFOPEN_SPAN',
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),
            productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    require(len(remaining)==32 and len({(v['path'],v['attributes']['beginline']) for v in purposes})==9,'18rows9clauses, not PT')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    approved=(data.ROOT/design).read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved SS unchanged')
    for v in (prior,obs,coordinate):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],
        sourceHashes={PREFIX+k:v for k,v in PINS.items()},savedCurrentCoordinateReportReferences=reports,coordinateToolManifestSha256=COORDINATE[1],approvedDesignSha256=data.sha(approved),
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newManualReviews=18,newReferenceConnections=0,firstEverSemanticReasons=None,combinedSelectedReferences=1171,combinedPurposeReviewed=288,combinedPurposeOrReferenceRows=1459,
        remainingSelectedUnreferenced=32,sourceCatchClauses=9,directContractMetadataNegativeVectors=len(negative),directContractNegativeLabels=negative,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
