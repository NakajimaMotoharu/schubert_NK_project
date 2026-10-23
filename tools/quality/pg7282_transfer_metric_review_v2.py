"""BUG1657/YKT1410: all28 raw findings, private-only fix, four negative guards and59 provenance rows."""
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from pg7192_heap_quality_review import anchors
from transfer_metric_fix_contract import verify_private_rename

OUT=host.BASE/'PG7282-transfer-metric-review-v2'
PINS={
 'current':('PG7274-transfer-metric-post-v2/manifest.json','f167da99fa7062a2d890cd451dc99882b4ff553f1b041aec6b2087c7e4d6f876'),
 'originalTransfer':('PG7268-transfer-metric-post-v1/manifest.json','2d59873dacf13a4297567a52ddcd22b402b5a6e75ccd6b3c00ead5a76585f208'),
 'old':('PG7254-batch-metric-post-v1/manifest.json','379cef1807e526b900bd9ff61c1fd96224bad8be09e355862133adad7f34bc9a'),
 'oldReview':('PG7262-batch-metric-review-v1/manifest.json','81a39ba0ce57971f66f300a5a6961e472f214a141563ed675fe553cf9a9e3f57'),
 'physical':('PG7278-transfer-metric-six-post-v2/manifest.json','f5941f082d691d71f33e1315c52012afdac7011f6763220fb3a60b21a64a2c3b'),
 'trace':('PG7280-transfer-metric-trace-v2/manifest.json','1975ccbc56108eff443fc9e3e067ae4440843e55e57edf4ad342c7a6d22fcdd3'),
 'previous':('PG7260-batch-metric-trace-v1/manifest.json','90ad5b48b1fd626d4e52dc103e90bd551a07248764b8f2d4a82e581815d1674b')}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only fixed-source review')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original public witness');proofs[key]=json.loads(file.read_bytes())
    current=proofs['current'];original=proofs['originalTransfer'];old=proofs['old'];physical=proofs['physical'];trace=proofs['trace']
    require(current['source']==physical['source']==trace['source']=='1470b0ea110bcf9598bcdc423745b812b580f9ad'
      and current['tests']==161 and current['suites']==22 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and len(current['executableClasses'])==40 and len(current['sourceFiles'])==46
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current161/40 actual positive counters')
    require(original['source']=='936c727ea50906c64520b607cc9e93b6fd584544' and original['tests']==161
      and original['suites']==22 and proofs['oldReview']['source']==old['source'] and proofs['oldReview']['unclassified']==0,
      'original defective-source success is distinct; old unchanged reasons qualified')
    key=lambda r:json.dumps(r,sort_keys=True)
    fresh=current['staticRaw']['pmd'];prior=old['staticRaw']['pmd'];defective=original['staticRaw']['pmd']
    prior_rows=Counter(map(key,prior['findings']));defect_rows=Counter(map(key,defective['findings']))
    require(len(fresh['findings'])==28 and len(defective['findings'])==31
      and Counter(map(key,fresh['findings']))==prior_rows and prior_rows<=defect_rows
      and fresh['actualExit']==4 and fresh['processingErrors']==0,'all28 unchanged raw findings; exact three removed without suppression')
    resolved=[]
    for raw,count in (defect_rows-prior_rows).items():
        row=json.loads(raw);require(count==1 and row['rule']=='AvoidFieldNameMatchingMethodName'
          and row['class'] in ('TransferMetricRecorder.Usage','TransferMetricRecorder.Suffix'),'only the three registered naming defects')
        resolved.append(row)
    legacy_naming=[r for r in fresh['findings'] if r['rule']=='AvoidFieldNameMatchingMethodName']
    prior_naming=[r for r in prior['findings'] if r['rule']=='AvoidFieldNameMatchingMethodName']
    require(len(resolved)==3 and len(legacy_naming)==3
      and Counter(map(key,legacy_naming))==Counter(map(key,prior_naming))
      and all(r['class']=='MonitoringModePolicy' for r in legacy_naming)
      and {r['message'] for r in legacy_naming}=={
        'Field detailedMetricsEnabled has the same name as a method',
        'Field retentionDays has the same name as a method',
        'Field retentionBytes has the same name as a method'}
      and not any(r['class'].startswith('TransferMetricRecorder') for r in legacy_naming),
      'new Transfer rule zero and exact three old individually approved enum accessor rows only')
    for row in prior['findings']:
        path='src/schubert-nk-batch/src/main/java/'+row['package'].replace('.','/')+'/'+row['class'].split('.',1)[0]+'.java'
        require(path in current['sourceFiles'] and current['sourceFiles'][path]==old['sourceFiles'][path],
                'no previous rationale for changed issue-bearing Main')
    main_path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/TransferMetricRecorder.java'
    changes={p for p,h in original['sourceFiles'].items() if current['sourceFiles'].get(p)!=h}
    require(changes=={main_path} and set(original['sourceFiles'])==set(current['sourceFiles']),
      'one Main changed, all other45 Main/Test source bytes and every oracle unchanged')
    blob=lambda revision:subprocess.check_output(['git','show',revision+':'+main_path],cwd=host.ROOT)
    before=blob(original['source']);after=blob(current['source']);rename=verify_private_rename(before,after)
    changed_paths=subprocess.check_output(['git','diff','--name-only',original['source'],current['source'],'--','src'],cwd=host.ROOT,text=True).splitlines()
    require(changed_paths==[main_path],'entire src changed only in the nine private tokens')
    mutants=[('extra-byte',after+b'\n'),('public-accessor',after.replace(b'Counts part()',b'Counts changedPart()')),
      ('missing-rename',after.replace(b'return suffixLabel;',b'return label;')),('unchanged-original',before)]
    negatives=[]
    for label,mutant in mutants:
        try:verify_private_rename(before,mutant)
        except ValueError:negatives.append(dict(kind=label,rejected=True))
        else:raise ValueError('private-only independent guard accepted mutation')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],
      'actual current SB/CS zero')
    counts=anchors(trace['sourceRows'],{r['path']:r for r in proofs['previous']['sourceRows']},dict(changed=0,unchanged=57,introduced=2))
    require(len(trace['physicalRows'])==51 and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==40
      and physical['allPhysicalClassCount']==1720 and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'current40 qualified separate from historical Web/whole1720 inventory')
    value=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,rawPmdFindings=28,rawPmdExit=4,
      unchangedSourceRationaleCount=28,resolvedNamingRows=resolved,newTransferNamingRuleCount=0,
      legacyApprovedNamingRows=legacy_naming,legacyApprovedNamingRuleCount=3,legacyNamingReasonDocument='018/1542',
      privateOnlyChange=rename,negativeGuards=negatives,unclassified=0,suppressionsAdded=0,
      actualViolationsOutstanding=0,editAnchorCounts=counts,closedLimitedScope=['BUG-1657','YKT-1410','BUG-1658','YKT-1411'],
      originalSourceProofNotTransferred=True,ptExecutedByReview=0,whole451Accepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,newTransferNamingRuleCount=0,legacyApprovedNamingRuleCount=3,
      negativeGuards=len(negatives),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
