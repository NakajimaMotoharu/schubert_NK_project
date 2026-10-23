"""Exact unchanged Main1738 proof and role-aware82/69 trace, no historical runtime transfer."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
import pg6966_chr_adapter_host as host
import pg7440_web_generated_six_compile as compilation
import pg7362_api_pool_observation_host as sdk
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

SOURCE='6dbf7f17b369f4859517ef544e55cc5f09d61d8f'
OUT=host.BASE/'PG7442-web-generated-byte-trace-v1'
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/GeneratedWebValueContractTest.java'
SPEC='evidence/01_PT/018_NK-OPS-001/1658_Web生成Value契約_追加単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only byte provenance proof')
    proofs={};pins={}
    for key,name,digest in (
      ('previousPhysical','PG7426-batch-generated-byte-bridge-v1/manifest.json','5b00abaa2d709695bfafe0f593ee20dd9ccbdea521d6fd2ef8cf52e1551dd9d4'),
      ('previousCompile','PG7424-batch-generated-six-compile-v1/manifest.json','f210190da07f5da11615b0b004c45095cb6f4960161f6762de1dd68639e64e8f'),
      ('previousTrace','PG7428-batch-generated-trace-v1/manifest.json','fb9f04d8824fe5003a6c55070cd581b59b3de4c1966868284b3af43c633b07f4'),
      ('previousWeb','PG7140-http-terminal-post-v2/manifest.json','1e66707fc37eef6842dda56ff945635b64f0d8ce0cab6a197b0b4ac0ed4a8653'),
      ('currentWeb','PG7436-web-generated-post-v1/manifest.json',None)):
        path=host.BASE/name;sha=host.sha(path);require(digest is None or sha==digest,'exact witness hash')
        proofs[key]=json.loads(path.read_bytes());pins[key]=dict(path=name,sha256=sha)
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes());previous=proofs['previousPhysical'];old=proofs['previousCompile']
    current=proofs['currentWeb'];web=proofs['previousWeb'];snapshot=compilation.SLOT/'snapshot';inputs=raw['begin']['inputHashes']
    require(raw['source']==current['source']==SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
      and raw['testsExecuted']==0 and current['tests']==27 and current['suites']==4
      and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and len(current['executableClasses'])==9 and current['physicalClasses']==web['physicalClasses']
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'genuine current Web27/4, nine positive CRC-bound executables')
    changes=subprocess.check_output(['git','diff','--name-status',previous['source'],SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines()
    require(old['source']==previous['source']=='9d8e520376501de825f26f963d6914beb98b890c'
      and changes==['A\t'+TEST] and set(inputs)-set(old['begin']['inputHashes'])=={TEST}
      and all(inputs.get(p)==h for p,h in old['begin']['inputHashes'].items()),'exact one Test delta, every Main/POM/settings byte unchanged')
    require(all(host.sha(snapshot/p)==h==host.sha(host.ROOT/p) for p,h in inputs.items()),'current/frozen entire source exact')
    physical={}
    require(set(raw['jars'])=={'protocol','storage','bootstrap','api','web','batch'},'all normal six Jars')
    for role,row in raw['jars'].items():
        file=Path(row['path']);require(host.sha(file)==row['sha256'],'owned original Jar bytes')
        with zipfile.ZipFile(file) as jar:
            for name in jar.namelist():
                if name.endswith('.class'):
                    key=role+':'+name;require(key not in physical,'unique owner')
                    physical[key]=hashlib.sha256(jar.read(name)).hexdigest()
    require(physical==previous['allPhysicalMainSha256'] and len(physical)==1738,'every Main byte/debug matches original six, not normalized semantic substitute')
    require(raw['begin']['dependencyJarHashes']==old['begin']['dependencyJarHashes']==sdk.DEPENDENCIES
      and current['additionalSdkAuxiliaryJarHashes']==web['additionalSdkAuxiliaryJarHashes']
      and sdk.DEPENDENCIES=={**current['additionalSdkAuxiliaryJarHashes'],**sdk.EXTRA}
      and all(host.sha(Path(p))==h for p,h in sdk.DEPENDENCIES.items()),'Web SDK4 versus normal six API-only2 explicitly disjoint')
    prior={r['path']:r for r in proofs['previousTrace']['sourceRows']};require(len(prior)==81,'all prior81 trace rows')
    source_delta=[dict(r) for r in previous['newSourceDelta']]
    source_delta.append(dict(path=TEST,status='A',sha256=inputs[TEST],owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0))
    rows=[]
    for item in sorted(source_delta,key=lambda r:r['path']):
        path=item['path'];blob=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        require(inputs[path]==item['sha256']==hashlib.sha256(blob).hexdigest(),'all committed source/path/hash')
        if path in prior:
            row=copy.deepcopy(prior[path]);require(row['sha256']==item['sha256'],'prior81 unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path==TEST,'exact new Test');row=dict(item,kind='TEST',rd='MON005..013',ui='252',ss='313,351',
              testIdFamily='GENWEB001..004',specifications=[dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))],
              previousSourceByteSha256=None,sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'actual executed Web source input')
            row.update(qualificationRelationship='CURRENT_WEB_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_WEB_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentWeb'],source=SOURCE,tests=27,suites=4))
        else:
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR' if path.endswith('/pom.xml')
              else 'HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION'
              if path.endswith('/pom.xml') else 'HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False
        if path.endswith('/HttpMetricContract.java'):
            row['additionalSpecifications']=[dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))];row['additionalTestIdFamily']='GENWEB001..004'
        rows.append(row)
    counts=anchors(rows,prior,dict(changed=0,unchanged=81,introduced=1));classes=[]
    for oldrow in proofs['previousTrace']['physicalRows']:
        row=dict(oldrow);role= row['className'].split(':',1)[0]
        require(physical[row['className']]==row['sha256'],'each traced physical remains actual')
        row.update(qualificationDomain='CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
          executionSource=SOURCE if role=='web' else previous['currentBatch']['source'] if role=='batch' else previous['historicalApi']['source'],
          currentSourceExecutionAccepted=role=='web' and row['executable'])
        classes.append(row)
    require(len(rows)==82 and len(classes)==69 and sum(r['currentSourceExecutionAccepted'] for r in classes)==9,'all82/69/currentWeb9 versus historical59 and metadata')
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),jars=raw['jars'],allPhysicalMainSha256=physical,
      allPhysicalClassCount=1738,oldPhysicalUnchanged=1669,exactPriorMainBytesUnchanged=1738,productionSourceChanges=changes,
      newSourceDelta=source_delta,sourceRows=rows,physicalRows=classes,editAnchorCounts=counts,currentWebCounters=current['counters'],
      currentWeb=dict(source=SOURCE,tests=27,suites=4,physicalClasses={'web:'+p:h for p,h in current['physicalClasses'].items()},currentSourceExecutionAccepted=True),
      historicalBatch=dict(**previous['currentBatch'],byteIdentityOnly=True,coverageNotTransferred=True),historicalApi=previous['historicalApi'],
      architecture=dict(originalProof=previous['architecture'],allInputMainBytesUnchanged=True,newRuleExecution=False),
      sdkHashes=sdk.DEPENDENCIES,coverageUnion=False,wholeSourceCountersNotSynthesized=True,testsExecutedByBridge=0,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassLoadOrInitialization=False)
    value['historicalBatch']['currentSourceExecutionAccepted']=False
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1738,sources=82,addedPhysical=69,currentWebExecutable=9,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
