"""Current generated60 direct contracts and unchanged28 static applicability, no old PT transfer."""
from collections import Counter
import datetime
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
import pg7420_batch_generated_host as execution
import pg7424_batch_generated_six_compile as compilation
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7430-batch-generated-review-v1'
PREFIX='dev/codex/schubert/nk/batch/monitoring/'
RECORDS={
 'ObservationContext':('clearance','at','elapsed'),
 **{name+'$Evaluation':('suppliedValuePresent','event') for name in (
    'TimedFilesystemMonitor','TimedJvmHeapMonitor','TimedDbPoolMonitor','TimedSyncLatencyMonitor','TransferHealthMonitor')},
 'TransferMetricRecorder$Counts':('files','bytes')}
ENUMS=('AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity','AlertLifecycle$CauseClearance',
 'BatchMetricContract$Step','BatchMetricContract$Status','MetricContract','MetricContract$Kind','MonitoringModePolicy',
 'MonitoringModePolicy$DetailService','ContinuousConditionWindow$State','TransferMetricRecorder$Suffix')

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only static and generated contract review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7422-batch-generated-post-v1/manifest.json',None),
      ('physical','PG7426-batch-generated-byte-bridge-v1/manifest.json',None),
      ('trace','PG7428-batch-generated-trace-v1/manifest.json',None),
      ('previous','PG7288-transfer-health-post-v1/manifest.json','afac4559457cc1b93b359da1193d34d08558a868cf0513f5b2d9045a9d64da70'),
      ('previousReview','PG7296-transfer-health-review-v1/manifest.json','8f67cfb0db7d4fc2bc0e7fdef9a3130ceb51e0e7a674dd918f6f11aaff52cfb1'),
      ('inventory','PG7416-generated-value-inventory-v1/manifest.json','92f7329fa38699d44f0c913a49b7d71e4521318f5e7e6d74a2a655a7e492149b'),
      ('jdkFilter','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness bytes')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];old=proofs['previous'];p=proofs['physical'];t=proofs['trace'];prior=proofs['previousReview']
    require(c['source']==p['source']==t['source']==compilation.SOURCE and c['tests']==176 and c['suites']==24
      and c['actualCrcMismatch']==0 and c['actualSessions']==1 and len(c['executableClasses'])==42
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual176 with all42 positive four counters')
    fresh=c['staticRaw']['pmd'];before=old['staticRaw']['pmd'];canonical=lambda row:json.dumps(row,sort_keys=True)
    require(len(fresh['findings'])==28 and Counter(map(canonical,fresh['findings']))==Counter(map(canonical,before['findings']))
      and fresh['actualExit']==4 and fresh['processingErrors']==0 and prior['actualExit']==0
      and prior['unclassified']==0 and prior['rawPmdFindings']==28,'all28 raw exact individual reasons, no new finding or suppression')
    require(c['physicalClasses']==old['physicalClasses']
      and all(c['sourceFiles'].get(path)==digest for path,digest in old['sourceFiles'].items()),'all prior Main/Test source and physical bytes exact before rationale reuse')
    require(c['spotbugs']['actualExit']==0 and c['spotbugs']['findings']==0
      and c['staticRaw']['checkstyle']['actualExit']==0 and not c['staticRaw']['checkstyle']['findings'],'actual current SB/CS zero')
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    cases=[r for r in raw['cases'] if r['classname'].endswith('.GeneratedBatchValueContractTest')]
    require(len(cases)==7 and all(r['result']=='PASS' for r in cases),'seven actual generated cases, not definitions')
    types={r['className']:r for r in proofs['inventory']['generatedTypes']};rows=[]
    for name in (*RECORDS,*ENUMS):
        full=PREFIX+name;row=types[full]
        require(row['role']=='batch' and c['physicalClasses'].get(full+'.class')==row['sha256']
          and c['sourceFiles'].get(row['sourcePath'])==row['sourceSha256'],'actual current executed type and source equal inspected metadata')
        methods={m['name']:m for m in row['methods']}
        if name in RECORDS:
            require(row['kind']=='RECORD' and tuple(r['name'] for r in row['components'])==RECORDS[name],'every source record component explicit')
            chosen=['equals','hashCode','toString',*RECORDS[name]]
            require(all(methods[m]['shape']=='JDK_OBJECTMETHODS_BOOTSTRAP' for m in chosen[:3])
              and all(methods[m]['shape']=='FIELD_ACCESSOR_SHAPE_SOURCE_REVIEW_REQUIRED' for m in chosen[3:]),'actual javac ObjectMethods and accessor shape; source/direct oracle review also required')
        else:
            require(row['kind']=='ENUM' and methods['values']['shape']=='ENUM_VALUES_FACTORY'
              and methods['valueOf']['shape']=='ENUM_VALUEOF_FACTORY','both actual generated enum factories')
            chosen=['values','valueOf']
        rows.append(dict(className=full,sha256=row['sha256'],sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
          kind=row['kind'],methods=[methods[m] for m in chosen],componentFields=row['components'],
          sourceAccessorReview='1656 source review and ordinary typed accessor assertions; no handwritten override',
          testIds='GENB001..007',directOrdinaryContractsVerified=True,customExclusionAdded=False))
    require(len(rows)==19 and sum(len(r['methods']) for r in rows)==60,'seven records/twelve enums/all sixty methods, not coverage numerator')
    jdk=proofs['jdkFilter'];jacoco=host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==jdk['jdkModulesSha256'] and host.sha(jacoco)==jdk['jacocoCoreSha256']
      and jdk['generatedMethodCount']==21 and jdk['officialFilterDelegation']['matcher']=='RecordsFilter$Matcher',
      'reuse exact platform31fold/filter delegation static property, not previous API runtime outcomes')
    require(t['editAnchorCounts']==dict(changed=0,unchanged=80,introduced=1) and len(t['physicalRows'])==69
      and sum(r['currentSourceExecutionAccepted'] for r in t['physicalRows'])==42
      and not p['historicalApi']['currentSourceExecutionAccepted'] and not p['historicalWeb']['currentSourceExecutionAccepted'],
      'all81 provenance/currentBatch42 versus historical26 physical domains')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      witnesses=pins,generatedTypes=rows,generatedMethodCount=60,actualNewOrdinaryCases=7,currentWholeComponentTests=176,
      jdkModulesSha256=jdk['jdkModulesSha256'],jacocoCoreSha256=jdk['jacocoCoreSha256'],platformByteProofReused=True,
      independentOracle='1656 fixed literal factories, per-component differences, 31fold/JDK Boolean-Enum-Object identity/Optional and primitive fixed text, no production record methods in expected',
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=28,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      editAnchorCounts=t['editAnchorCounts'],counters=c['counters'],coverageNumeratorsNotSynthesized=True,
      standardCompilerPlumbingFilterOnly=True,customExclusionsAdded=False,ptExecutedByReview=0,
      relatedBug='BUG-1662',relatedExpansion='YKT-1413',expansionClosed=False,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,generatedTypes=19,generatedMethods=60,actualNewOrdinaryCases=7,rawFindings=28,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
