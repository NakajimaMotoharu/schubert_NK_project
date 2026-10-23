"""Independent additive-scope review, requiring literal source/count/pins and unchanged rationale bytes.

No original test execution, PMD suppression or acceptance publication. Only explicitly declared private locks
may be introduced by this limited reviewer. Different finding types require another explicit review.
"""
from collections import Counter
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from pg7192_heap_quality_review import anchors

def require(value,message):
    if not value:raise ValueError(message)

def review(*, entrypoint, out, pins, source, tests, suites, executable, physical_count,
           added_physical, anchor_counts, new_class, test_ids, reason_document,
           lock_methods=('observe','snapshot'),allow_no_new_findings=False):
    invocation=capture(Path(entrypoint));require(not out.exists(),'new-only additive static review')
    proofs={}
    for key,(path,digest) in pins.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original witness pin');proofs[key]=json.loads(file.read_bytes())
    current=proofs['current'];old=proofs['old'];physical=proofs['physical'];trace=proofs['trace']
    require(current['source']==physical['source']==trace['source']==source and current['tests']==tests
      and current['suites']==suites and len(current['executableClasses'])==executable
      and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current complete positive scope')
    require(proofs['oldReview']['source']==old['source'] and proofs['oldReview']['unclassified']==0
      and proofs['oldReview']['actualExit']==0,'original reasons qualified for original source')
    canonical=lambda r:json.dumps(r,sort_keys=True)
    fresh=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    prior=Counter(map(canonical,before['findings']));now=Counter(map(canonical,fresh['findings']))
    require((bool(lock_methods) or allow_no_new_findings) and len(set(lock_methods))==len(lock_methods),
            'explicit unique methods or expressly declared zero new findings')
    require(prior<=now and sum((now-prior).values())==len(lock_methods) and fresh['actualExit']==4
      and fresh['processingErrors']==0,'all raw prior rows plus exact declared additions, no suppression/unknown')
    for row in before['findings']:
        path='src/schubert-nk-batch/src/main/java/'+row['package'].replace('.','/')+'/'+row['class']+'.java'
        require(path in current['sourceFiles'] and current['sourceFiles'][path]==old['sourceFiles'][path],
                'unchanged issue-bearing source required for inherited rationale')
    rows=[];methods=set()
    for raw,count in (now-prior).items():
        row=json.loads(raw);require(count==1 and row['class']==new_class
          and row['method'] in lock_methods and row['rule']=='AvoidSynchronizedStatement',
          'only explicitly reviewed private lock rows')
        methods.add(row['method']);rows.append(dict(raw=row,disposition='CONTRACT_REQUIRED',testIds=test_ids,
          reasonDocument=reason_document,reason='PRIVATE_FINAL_OWNER_LOCK; dependent state serialized; no exposed monitor or reverse callback'))
    require(methods==set(lock_methods),'all declared methods classified once')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],
      'actual current SB/CS zero')
    counts=anchors(trace['sourceRows'],{r['path']:r for r in proofs['previous']['sourceRows']},anchor_counts)
    require(len(trace['physicalRows'])==added_physical
      and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==executable
      and physical['allPhysicalClassCount']==physical_count and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'all physical additions/current executable qualification distinct from historical Web')
    result=dict(actualExit=0,source=source,invocation=invocation,witnesses=pins,rawPmdFindings=len(fresh['findings']),
      rawPmdExit=4,unchangedSourceRationaleCount=len(before['findings']),newRows=rows,unclassified=0,suppressionsAdded=0,
      actualViolationsOutstanding=0,editAnchorCounts=counts,ptExecutedByReview=0,whole451Accepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);out.mkdir();host.write(out/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,rawFindings=len(fresh['findings']),unclassified=0,anchors=counts,manifestSha256=host.sha(out/'manifest.json'))))
