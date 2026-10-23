"""Individual applicability:17 unchanged issues, six removed and six new private poll contracts."""
from collections import Counter
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from pg7192_heap_quality_review import anchors

OUT=host.BASE/'PG7220-heap-connection-review-v1'
PINS={
 'current':('PG7212-heap-connection-post-v1/manifest.json','f42c119d34dbe54c5c22f8f75f0d1b1eab80f20b648c419c4ba9d6138e50aa58'),
 'old':('PG7198-timed-heap-post-v1/manifest.json','e0186e220a22556c0706b55513f287924e6326bd75699fd19a5bca85cfa0a6be'),
 'oldReview':('PG7206-timed-heap-review-v1/manifest.json','0f03e23d200e43a2e693f354a8964e90e91dcbccdeedbfcb23e4a3ad2366b5e4'),
 'physical':('PG7216-heap-connection-six-post-v1/manifest.json','687a7487c535c1a954614582da4e78298fea36608dabaac54920dc7c71e6ea2e'),
 'trace':('PG7218-heap-connection-trace-v1/manifest.json','763e8d9e96b4f05e99c8983838fc5c2b5a592d84c50869815407a609690eea71'),
 'previous':('PG7204-timed-heap-trace-v1/manifest.json','79b1052ccafe79754ab4178702b7a4ef302ba670fd4c9ba05a3fe7ff818139a7')}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only review')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact public witness');proofs[key]=json.loads(file.read_bytes())
    current=proofs['current'];old=proofs['old'];physical=proofs['physical'];trace=proofs['trace']
    require(current['source']==physical['source']==trace['source']=='0b8aa6dab9b91d378811b0bda24d6a61bbc73106'
      and current['tests']==124 and current['suites']==17 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current124/four positive counters')
    fresh=current['staticRaw']['pmd'];before=old['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    removed=[r for r in before['findings'] if r['class']=='FilesystemHealthMonitor']
    carried=[r for r in before['findings'] if r['class']!='FilesystemHealthMonitor']
    added=[r for r in fresh['findings'] if r['class']=='MonitoringPoller']
    require(len(removed)==6 and len(carried)==17 and len(added)==6 and len(fresh['findings'])==23
      and Counter(map(canonical,fresh['findings']))==Counter(map(canonical,carried+added))
      and fresh['actualExit']==4 and fresh['processingErrors']==0,'exact17 unchanged/six new; old six absent')
    require(proofs['oldReview']['unclassified']==0,'actual old reasons complete')
    for row in carried:
        path='src/schubert-nk-batch/src/main/java/'+row['package'].replace('.','/')+'/'+row['class']+'.java'
        require(path in current['sourceFiles'] and current['sourceFiles'][path]==old['sourceFiles'][path],
                'no old rationale inherited for changed issue-bearing Main')
    lock_methods=set();failure_rows=set();reviewed=[]
    for row in added:
        if row['rule']=='AvoidSynchronizedStatement':
            require(row['method'] in ('observe','observeNow'),'only two private lock scopes')
            lock_methods.add(row['method']);reason='PRIVATE_FINAL_OWNER_LOCK; serialized callback/elapsed/gap; no exposed this/class lock'
            tests=['POLL007','HEAPCONN008']
        else:
            require(row['rule']=='AvoidCatchingGenericException' and row['method'] in ('observeNow','observeLocked')
              and row['message'] in ('Avoid catching RuntimeException in try-catch block','Avoid catching Error in try-catch block'),
              'only same-identity provider failure boundaries')
            failure_rows.add((row['method'],row['message']));reason='RETHROW_IDENTICAL_FAILURE; mark continuity gap only; no formatting/retry/normal conversion'
            tests=['POLL002','POLL004','POLL006','POLL008','HEAPCONN003','HEAPCONN004']
        reviewed.append(dict(raw=row,disposition='CONTRACT_REQUIRED',reason=reason,reasonDocument='018/1600',testIds=tests))
    require(lock_methods=={'observe','observeNow'} and len(failure_rows)==4,'all six separately classified')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    previous={r['path']:r for r in proofs['previous']['sourceRows']}
    counts=anchors(trace['sourceRows'],previous,dict(changed=3,unchanged=41,introduced=4))
    require(len(trace['physicalRows'])==39 and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==28
      and physical['allPhysicalClassCount']==1708 and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'current28 distinct from historical Web')
    value=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,rawPmdFindings=23,rawPmdExit=4,
      unchangedSourceRationaleCount=17,removedRows=removed,newRows=reviewed,unclassified=0,suppressionsAdded=0,
      actualViolationsOutstanding=0,editAnchorCounts=counts,ptExecutedByReview=0,whole451Accepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=23,unclassified=0,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
