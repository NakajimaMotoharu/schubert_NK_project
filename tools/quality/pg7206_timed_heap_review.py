"""All23 raw static findings and all44 source anchors, current108 actual scope only."""
from collections import Counter
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from pg7192_heap_quality_review import anchors

OUT=host.BASE/'PG7206-timed-heap-review-v1'
PINS={
 'current':('PG7198-timed-heap-post-v1/manifest.json','e0186e220a22556c0706b55513f287924e6326bd75699fd19a5bca85cfa0a6be'),
 'oldRationale':('PG7184-heap-input-post-v1/manifest.json','886b6965fb80bf30cbe964d7858b7687e8a40987ab076ff673d2a5802a727009'),
 'physical':('PG7202-timed-heap-six-post-v1/manifest.json','5c1b8abcad3f66926675e1c41951b95197643fcbb5d0b44888797677e6027b32'),
 'trace':('PG7204-timed-heap-trace-v1/manifest.json','79b1052ccafe79754ab4178702b7a4ef302ba670fd4c9ba05a3fe7ff818139a7'),
 'previous':('PG7191-heap-input-trace-v2/manifest.json','06588f80a3e0ade520c2af93f9a39b9b6f1767d885038195e0c072ebda482291')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only review')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original public proof');proofs[key]=json.loads(file.read_bytes())
    current=proofs['current'];old=proofs['oldRationale'];physical=proofs['physical'];trace=proofs['trace']
    require(current['source']==physical['source']==trace['source']=='41905e2f089eec0aeea8c8f0acca9cc657814a00'
      and current['tests']==108 and current['suites']==15 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current108/positive four counters')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items()),'all previous30 Java source bytes unchanged')
    fresh=current['staticRaw']['pmd'];before=old['staticRaw']['pmd'];key=lambda r:json.dumps(r,sort_keys=True)
    old_rows=Counter(map(key,before['findings']));new_rows=Counter(map(key,fresh['findings']))
    require(old_rows<=new_rows and len(before['findings'])==21 and len(fresh['findings'])==23
      and fresh['actualExit']==4 and fresh['processingErrors']==0,'all21 prior raw rows with exactly two added')
    reviewed=[];methods=set()
    for raw,count in (new_rows-old_rows).items():
        row=json.loads(raw);require(count==1 and row['class']=='TimedJvmHeapMonitor'
          and row['method'] in ('observe','snapshot') and row['rule']=='AvoidSynchronizedStatement','exact two reviewed private locks')
        methods.add(row['method']);reviewed.append(dict(raw=row,disposition='CONTRACT_REQUIRED',reasonDocument='018/1596',testIds=['HEAPTIME007']))
    require(methods=={'observe','snapshot'},'no unclassified or missing finding')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    previous={r['path']:r for r in proofs['previous']['sourceRows']}
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=42,introduced=2))
    require(len(trace['physicalRows'])==37 and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==26
      and physical['allPhysicalClassCount']==1706 and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'all actual physical classes/qualified current26 distinct from historical Web')
    value=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,rawPmdFindings=23,rawPmdExit=4,
      unchangedSourceRationaleCount=21,rationaleReference='018/1587,1592; reasons only, not past execution',
      newRows=reviewed,unclassified=0,suppressionsAdded=0,actualViolationsOutstanding=0,editAnchorCounts=counts,
      ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=23,unclassified=0,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
