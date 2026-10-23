"""Current21 unchanged static reasons and all42 immediate-edit anchors, including independent negative guards."""
from collections import Counter
import copy
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7192-heap-quality-review-v1'
PINS={
 'current':('PG7184-heap-input-post-v1/manifest.json','886b6965fb80bf30cbe964d7858b7687e8a40987ab076ff673d2a5802a727009'),
 'oldStaticRationale':('PG7168-observation-clock-post-v1/manifest.json','580abe8ff4eea75f6f2fda9fbd45c787f16b468a2536f16590705734f23bdcc5'),
 'physical':('PG7188-heap-input-six-post-v1/manifest.json','78c3cb12d7a708a520bccd6d3e3c142a14c61647765906db0e73172dbf3a1519'),
 'trace':('PG7191-heap-input-trace-v2/manifest.json','06588f80a3e0ade520c2af93f9a39b9b6f1767d885038195e0c072ebda482291'),
 'previousTrace':('PG7174-observation-clock-trace-v1/manifest.json','b0a847a40ca446eb3b77e018c46c7767063834a551596fceef7a97a392bf5d6c')}


def require(value,message):
    if not value:raise ValueError(message)


def anchors(rows,previous,expected=None):
    expected=expected or dict(changed=1,unchanged=38,introduced=3)
    size=sum(expected.values())
    require(len(rows)==size and len({r['path'] for r in rows})==size,'complete unique row set')
    counts=dict(changed=0,unchanged=0,introduced=0)
    for row in rows:
        prior=previous.get(row['path'])
        if prior is None:
            require(row['previousSourceByteSha256'] is None and row['sourceIntroducedSincePreviousTrace'] is True
              and row['sourceChangedSincePreviousTrace'] is False,'new source has no previous anchor')
            counts['introduced']+=1
        else:
            changed=row['sha256']!=prior['sha256']
            require(row['previousSourceByteSha256']==prior['sha256'] and row['sourceIntroducedSincePreviousTrace'] is False
              and row['sourceChangedSincePreviousTrace'] is changed,'immediate previous source/hash flag consistency')
            counts['changed' if changed else 'unchanged']+=1
    require(counts==expected,'exact declared changes and additions')
    return counts


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only review')
    proofs={}
    for name,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact public original proof pin');proofs[name]=json.loads(file.read_bytes())
    current=proofs['current'];old=proofs['oldStaticRationale'];physical=proofs['physical'];trace=proofs['trace']
    require(current['source']==physical['source']==trace['source']=='dc46262abceaac42085a813d872f25669700a096'
      and current['tests']==100 and current['suites']==14 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual100 and all24 exact positive counters')
    fresh=current['staticRaw']['pmd'];before=old['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    require(len(fresh['findings'])==21 and Counter(map(canonical,fresh['findings']))==Counter(map(canonical,before['findings']))
      and fresh['actualExit']==4 and fresh['processingErrors']==0,'all21 actual raw rows unchanged, no dropped/unknown finding')
    issue_sources=set()
    for finding in fresh['findings']:
        path='src/schubert-nk-batch/src/main/java/'+finding['package'].replace('.','/')+'/'+finding['class'].split('.')[0]+'.java'
        require(current['sourceFiles'].get(path)==old['sourceFiles'].get(path) and path in current['sourceFiles'],
                'all rationale-bearing Main source bytes unchanged, no inheritance for changed code')
        issue_sources.add(path)
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']}
    counts=anchors(trace['sourceRows'],previous);negative=[]
    changed=next(i for i,r in enumerate(trace['sourceRows']) if r['sourceChangedSincePreviousTrace'])
    unchanged=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous and not r['sourceChangedSincePreviousTrace'])
    introduced=next(i for i,r in enumerate(trace['sourceRows']) if r['sourceIntroducedSincePreviousTrace'])
    edits=[(unchanged,'previousSourceByteSha256','0'*64),(changed,'sourceChangedSincePreviousTrace',False),
           (unchanged,'sourceIntroducedSincePreviousTrace',True),(introduced,'previousSourceByteSha256','0'*64)]
    for index,field,value in edits:
        mutant=copy.deepcopy(trace['sourceRows']);mutant[index][field]=value
        try:anchors(mutant,previous)
        except ValueError:negative.append(dict(field=field,rejected=True))
        else:raise ValueError('independent edit-provenance guard failed')
    require(len(trace['physicalRows'])==35 and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==24
      and physical['allPhysicalClassCount']==1704 and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'all new physical classes, current24 distinct from historical Web nine')
    result=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,rawPmdFindings=21,rawPmdExit=4,
      rationaleReference='018/1587; only unchanged issue-bearing Main source',issueSourceFiles=sorted(issue_sources),
      unclassified=0,suppressionsAdded=0,actualViolationsOutstanding=0,editAnchorCounts=counts,negativeGuards=negative,
      closedToolScope=['BUG-1656','YKT-1409'],ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,rawFindings=21,anchorCounts=counts,negativeGuards=len(negative),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
