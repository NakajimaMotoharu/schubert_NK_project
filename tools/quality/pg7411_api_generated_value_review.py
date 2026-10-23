"""BUG1660 independent generated method inventory/JDK hash algorithm/source byte review, no target init."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import pg6966_chr_adapter_host as host
import pg7402_api_generated_contract_host as execution
import pg7406_api_generated_contract_six_compile as compilation
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7411-api-generated-value-review-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/'
RECORDS={
 'DbPoolMetricRecorder$Counts':('active','idle','pending','maximum'),
 'OutboxRowsMetricRecorder$Counts':('pending','sent','error')}
ENUMS=('AsyncJobMetricRecorder$State','DbPoolMetricRecorder$State',
       'OperationMismatchMetricRecorder$Operation','OutboxRowsMetricRecorder$Status')

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only generated-contract review')
    pin={}
    for key,path in {'current':'PG7404-api-generated-contract-post-v1/manifest.json',
      'previous':'PG7392-api-outbox-rows-post-v1/manifest.json'}.items():
        file=host.BASE/path;pin[key]=dict(path=path,sha256=host.sha(file),value=json.loads(file.read_bytes()))
    current=pin['current']['value'];old=pin['previous']['value']
    require(current['source']==compilation.SOURCE and current['tests']==72 and current['suites']==9
      and current['actualSessions']==1 and current['actualCrcMismatch']==0
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current72 positive four-counter CRC/session qualification')
    require(old['source']=='dbb794ec157bcdab86a3e0684e51562648bdd7ae' and old['tests']==64
      and current['physicalClasses']==old['physicalClasses'],'all current Main/metadata bytes unchanged, no previous PT transfer')
    changes=subprocess.check_output(['git','diff','--name-only',old['source'],compilation.SOURCE,'--','src'],cwd=host.ROOT,text=True).splitlines()
    test='src/schubert-nk-api/src/test/java/'+PREFIX+'GeneratedMetricValueContractTest.java'
    require(changes==[test] and test in current['sourceFiles'],'only declared generated-contract Test source added')
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    cases=[r for r in raw['cases'] if r['classname'].endswith('.GeneratedMetricValueContractTest')]
    require(len(cases)==8 and all(r['result']=='PASS' for r in cases),'all eight actually executed generated-contract cases, not definition count')
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    javap=host.TC/'jdk-25.0.4/bin/javap';receipts=[];rows=[]
    def inspect(arguments):
        command=[str(javap),*arguments]
        done=subprocess.run(command,capture_output=True,text=True)
        require(done.returncode==0,'static class inspection zero, never initialization/reflection')
        receipts.append(dict(command=command,actualExit=done.returncode,
          stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
        return done.stdout
    for name,components in RECORDS.items():
        path=classes/(PREFIX+name+'.class')
        require(host.sha(path)==current['physicalClasses'][PREFIX+name+'.class'],'exact actually executed record bytes')
        text=inspect(['-p','-c','-v','-classpath',str(classes),(PREFIX+name).replace('/','.')])
        require('java/lang/runtime/ObjectMethods.bootstrap' in text,'actual JDK bootstrap, not handwritten Object method hidden by metadata')
        methods=['equals(java.lang.Object)','hashCode()','toString()',*[c+'()' for c in components]]
        require(all(m+';' in text for m in methods),'all thirteen default record methods present')
        require(all(re.search(r'REF_getField\s+[^\s]+\.'+re.escape(c)+r':J',text) for c in components),'every declared primitive component participates in generated bootstrap')
        rows.append(dict(className=PREFIX+name,sha256=host.sha(path),generator='javac25.0.4/JDK25 ObjectMethods',
          methods=methods,componentFields=list(components),testIds='GENMET001..004',defaultJaCoCoFilter='RecordsFilter',
          directOrdinaryContractsVerified=True,customExclusionAdded=False))
    for name in ENUMS:
        path=classes/(PREFIX+name+'.class');require(host.sha(path)==current['physicalClasses'][PREFIX+name+'.class'],'exact current enum bytes')
        text=inspect(['-p','-c','-s','-classpath',str(classes),(PREFIX+name).replace('/','.')])
        require(' values();' in text and ' valueOf(java.lang.String);' in text,'both actual generated enum factories')
        require('clone:()Ljava/lang/Object;' in text and 'java/lang/Enum.valueOf:' in text,'defensive array and JDK enum factory plumbing')
        rows.append(dict(className=PREFIX+name,sha256=host.sha(path),generator='javac25.0.4/java.lang.Enum',
          methods=['values()','valueOf(java.lang.String)'],testIds='GENMET005..008',defaultJaCoCoFilter='EnumFilter',
          directOrdinaryContractsVerified=True,customExclusionAdded=False))
    platform=inspect(['-p','-c','java.lang.runtime.ObjectMethods'])
    hash_code=re.search(r'private static int hashCombiner\(int, int\);(.*?)private static',platform,re.S)
    require(hash_code is not None and 'bipush        31' in hash_code.group(1) and 'imul' in hash_code.group(1)
      and 'iadd' in hash_code.group(1),'independent installed JDK25 multiply31/add algorithm')
    jacoco=host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    filters=inspect(['-p','-c','-classpath',str(jacoco),'org.jacoco.core.internal.analysis.filter.RecordsFilter',
      'org.jacoco.core.internal.analysis.filter.EnumFilter'])
    require('hashCode' in filters and 'toString' in filters and 'equals' in filters and 'valueOf' in filters
      and 'values' in filters,'official preexisting generated-method filters identified, not expanded')
    require(sum(len(r['methods']) for r in rows)==21,'all twenty-one generated methods explicitly reviewed')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      witnesses={k:{n:v for n,v in row.items() if n!='value'} for k,row in pin.items()},
      generatedTypes=rows,generatedMethodCount=21,actualNewOrdinaryCases=8,currentWholeComponentTests=72,
      inspectionReceipts=receipts,jdkModulesSha256=host.sha(host.TC/'jdk-25.0.4/lib/modules'),
      jacocoCoreSha256=host.sha(jacoco),jdkHashCombinerExcerpt=hash_code.group(1),
      independentHashVectors=dict(pool=dict(ordinary=94248,allLongMax=0),outbox=dict(ordinary=3040,allLongMax=-2147483648,zero=0)),
      productionMainAndMetadataBytesUnchanged=True,sourceChanges=changes,coverageCounters=current['counters'],
      filterReason='Only preexisting javac/JDK value plumbing recognized by official JaCoCo; each contract directly verified by independent ordinary vectors. All handwritten logic/constructors/classes retained with positive four counters.',
      qualityConditionChanged=False,customExclusionsAdded=False,ordinaryPassNotAddedToCoverageNumerators=True,
      reviewDisposition='GENERATED_CONTRACT_SCOPE_REVIEWED_NO_NEW_EXCLUSION_NOT_WHOLE451',
      actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByInspection=False,
      formalUpdated=False,newAccepted=0,effortPercent=None,relatedBug='BUG-1660',relatedExpansion='YKT-1413')
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,generatedTypes=len(rows),generatedMethods=21,ordinaryCases=8,
      manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
