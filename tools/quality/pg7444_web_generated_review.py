"""Five Web generated value types/four actual cases, all five raw static rows individually retained."""
from collections import Counter
import datetime
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
import pg7434_web_generated_host as execution
import pg7442_web_generated_byte_trace as bridge
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7444-web-generated-review-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only generated/quality review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7436-web-generated-post-v1/manifest.json',None),
      ('byteTrace','PG7442-web-generated-byte-trace-v1/manifest.json',None),
      ('previous','PG7140-http-terminal-post-v2/manifest.json','1e66707fc37eef6842dda56ff945635b64f0d8ce0cab6a197b0b4ac0ed4a8653'),
      ('previousReview','PG7144-terminal-quality-review-v1/manifest.json',None),
      ('inventory','PG7416-generated-value-inventory-v1/manifest.json','92f7329fa38699d44f0c913a49b7d71e4521318f5e7e6d74a2a655a7e492149b'),
      ('jdkFilter','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original proof')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];old=proofs['previous'];bt=proofs['byteTrace'];prior=proofs['previousReview']
    require(c['source']==bt['source']==bridge.SOURCE and c['tests']==27 and c['suites']==4
      and c['actualSessions']==1 and c['actualCrcMismatch']==0 and len(c['executableClasses'])==9
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual current27/4/nine positive four counters')
    canonical=lambda row:json.dumps(row,sort_keys=True)
    pmd=c['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(pmd['actualExit']==4 and pmd['processingErrors']==0 and len(pmd['findings'])==5
      and Counter(map(canonical,pmd['findings']))==Counter(map(canonical,before['findings']))
      and prior['actualExit']==0 and prior['unclassified']==0 and len(prior['rows'])==5,'all five identical individually classified rows')
    require(c['physicalClasses']==old['physicalClasses'] and all(c['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items()),
      'unchanged issue-bearing source/byte before static rationale reuse')
    require(all(c['staticRaw'][k]['actualExit']==0 and not c['staticRaw'][k]['findings']
      and c['staticRaw'][k]['processingErrors']==0 for k in ('checkstyle','spotbugs')),'actual current CS/SB no violations or missing classes')
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes());cases=[r for r in raw['cases'] if r['classname'].endswith('.GeneratedWebValueContractTest')]
    require(len(cases)==4 and all(r['result']=='PASS' for r in cases),'four actual independent ordinary generated contracts')
    types={r['className']:r for r in proofs['inventory']['generatedTypes']};rows=[]
    for suffix in ('Labels','Metric','Route','Method','Status'):
        full=PREFIX+'HttpMetricContract$'+suffix;row=types[full];methods={m['name']:m for m in row['methods']}
        require(row['role']=='web' and c['physicalClasses'].get(full+'.class')==row['sha256']
          and c['sourceFiles'].get(row['sourcePath'])==row['sourceSha256'],'actual current byte/source ownership matches static inventory')
        if suffix=='Labels':
            require(row['kind']=='RECORD' and [r['name'] for r in row['components']]==['route','method','status'],'all source record components')
            chosen=['equals','hashCode','toString','route','method','status']
            require(all(methods[m]['shape']=='JDK_OBJECTMETHODS_BOOTSTRAP' for m in chosen[:3])
              and all(methods[m]['shape']=='FIELD_ACCESSOR_SHAPE_SOURCE_REVIEW_REQUIRED' for m in chosen[3:]),'generated bootstrap/accessor shape plus direct source/typed oracle review')
        else:
            require(row['kind']=='ENUM' and methods['values']['shape']=='ENUM_VALUES_FACTORY'
              and methods['valueOf']['shape']=='ENUM_VALUEOF_FACTORY','both closed generated enum factories')
            chosen=['values','valueOf']
        rows.append(dict(className=full,sha256=row['sha256'],sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
          methods=[methods[m] for m in chosen],componentFields=row['components'],testIds='GENWEB001..004',
          directOrdinaryContractsVerified=True,sourceAccessorReview='1658 source declaration/default accessor and direct typed assertions',customExclusionAdded=False))
    require(sum(len(r['methods']) for r in rows)==14,'exact fourteen generated methods separately verified, not numeric coverage')
    jdk=proofs['jdkFilter'];jacoco=host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==jdk['jdkModulesSha256'] and host.sha(jacoco)==jdk['jacocoCoreSha256'],
      'exact previously inspected platform31fold and official filter bytes, not old runtime test transfer')
    require(len(bt['sourceRows'])==82 and len(bt['physicalRows'])==69 and bt['editAnchorCounts']==dict(changed=0,unchanged=81,introduced=1)
      and sum(r['currentSourceExecutionAccepted'] for r in bt['physicalRows'])==9
      and not bt['historicalBatch']['currentSourceExecutionAccepted'] and not bt['historicalApi']['currentSourceExecutionAccepted'],
      'all source/physical/currentWeb9 and other historical domains explicit')
    value=dict(actualExit=0,source=bridge.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      generatedTypes=rows,generatedMethodCount=14,actualNewOrdinaryCases=4,currentWholeComponentTests=27,counters=c['counters'],
      rawPmdFindings=5,rawPmdExit=4,individualRationaleRows=prior['rows'],unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      jdkModulesSha256=jdk['jdkModulesSha256'],jacocoCoreSha256=jdk['jacocoCoreSha256'],platformByteProofReused=True,
      independentOracle='1658 fixed literal to typed enum constants, each Labels field difference/platform final Enum identity31fold/fixed full-field text',
      coverageNumeratorsNotSynthesized=True,customExclusionsAdded=False,ptExecutedByReview=0,relatedBug='BUG-1663',relatedExpansion='YKT-1413',
      expansionClosed=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,generatedTypes=5,generatedMethods=14,actualNewOrdinaryCases=4,rawFindings=5,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
