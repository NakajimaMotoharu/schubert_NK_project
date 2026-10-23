"""All1738 Main byte identity, current Batch qualification, explicit historical API/Web domains."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
import pg6966_chr_adapter_host as host
import pg6960_archunit as architecture
import pg7424_batch_generated_six_compile as compilation
import pg7362_api_pool_observation_host as sdk
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7426-batch-generated-byte-bridge-v1'
PINS={
 'previousPhysical':('PG7408-api-generated-contract-six-post-v1/manifest.json','2c4db84ee9a0c354aca88ef4dd03220d8b6ea9cd8eb8b80e44e2b39b9877924b'),
 'previousCompile':('PG7406-api-generated-contract-six-compile-v1/manifest.json','a0db7057aa326c291c421aa052ca88e9548ae032d625ed79bd63766166f8f89c'),
 'previousBatch':('PG7288-transfer-health-post-v1/manifest.json','afac4559457cc1b93b359da1193d34d08558a868cf0513f5b2d9045a9d64da70'),
 'currentBatch':('PG7422-batch-generated-post-v1/manifest.json',None),
 'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/GeneratedBatchValueContractTest.java'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only physical bridge')
    proofs={};pins={}
    for key,(name,digest) in PINS.items():
        path=host.BASE/name;actual=host.sha(path)
        require(digest is None or digest==actual,'fixed original public witness')
        proofs[key]=json.loads(path.read_bytes());pins[key]=dict(path=name,sha256=actual)
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes());old=proofs['previousCompile'];prev=proofs['previousPhysical']
    require(raw['source']==compilation.SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
      and raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY','actual normal compile terminal, no PT claimed')
    require(old['source']==prev['source']=='fcedc05b1b61b74b6b8a3fe3d9e5ea8d19859650'
      and old['actualExit']==0 and prev['actualExit']==0,'prior fixed Main/source proof')
    changes=subprocess.check_output(['git','diff','--name-status',old['source'],compilation.SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines()
    require(changes==['A\t'+TEST],'one Test addition only, no production/POM/settings edits')
    snapshot=compilation.SLOT/'snapshot';inputs=raw['begin']['inputHashes'];prior_inputs=old['begin']['inputHashes']
    require(set(inputs)-set(prior_inputs)=={TEST} and set(prior_inputs)<=set(inputs)
      and all(inputs[p]==h for p,h in prior_inputs.items()),'entire original Main/Test/POM snapshot unchanged plus one Test')
    require(all(host.sha(snapshot/p)==h==host.sha(host.ROOT/p) for p,h in inputs.items()),'current and frozen source inputs exact')
    def physical(jars):
        result={}
        require(set(jars)==set(architecture.MODULES),'all six actual artifacts')
        for role,row in jars.items():
            file=Path(row['path']);require(host.sha(file)==row['sha256'],'owned original Jar hash')
            with zipfile.ZipFile(file) as jar:
                for entry in jar.namelist():
                    if entry.endswith('.class'):
                        key=role+':'+entry;require(key not in result,'unique physical owner')
                        result[key]=hashlib.sha256(jar.read(entry)).hexdigest()
        return result
    actual=physical(raw['jars']);before=physical(old['jars'])
    require(actual==before and len(actual)==prev['allPhysicalClassCount']==1738,'every Main class byte including debug identical, no semantic normalization')
    current=proofs['currentBatch'];historical=proofs['previousBatch']
    require(current['source']==compilation.SOURCE and current['tests']==176 and current['suites']==24
      and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and len(current['executableClasses'])==42 and len(current['physicalClasses'])==43
      and current['physicalClasses']==historical['physicalClasses']
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current Batch176/24/session/CRC/four positive scope')
    batch={'batch:'+p:h for p,h in current['physicalClasses'].items()}
    require(all(p.startswith('batch:dev/codex/schubert/nk/batch/monitoring/') and actual.get(p)==h for p,h in batch.items()),'actual Batch namespace and actual normal versus executed bytes')
    deps=raw['begin']['dependencyJarHashes'];aux=current['additionalSdkAuxiliaryJarHashes']
    require(deps==sdk.DEPENDENCIES==old['begin']['dependencyJarHashes']
      and aux==historical['additionalSdkAuxiliaryJarHashes'] and len(aux)==4
      and deps=={**aux,**sdk.EXTRA} and not(set(aux)&set(sdk.EXTRA))
      and all(host.sha(Path(p))==h for p,h in deps.items()),'normal six SDK4+API auxiliary2 versus Batch SDK4 explicit, never role alias')
    prior_arch=proofs['architecture'];arch=prev['architecture']
    require(host.sha(architecture.SOURCE)==prior_arch['toolSourceSha256']
      and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
      and arch['receipt']['actualExit']==0 and arch['result']['physical']==1738
      and not arch['result']['findings'] and len(arch['result']['rules'])==5
      and all(v==0 for v in arch['result']['rules'].values()),'exact immutable rule/tool/library and byte inputs permit static property reuse, not execution transfer')
    rows=[dict(r) for r in prev['newSourceDelta']]
    rows.append(dict(path=TEST,status='A',sha256=inputs[TEST],owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0))
    rows.sort(key=lambda r:r['path']);require(len(rows)==81 and len({r['path'] for r in rows})==81,'all81 original-source additions and semantic POM changes')
    api=dict(prev['currentApi']);api.update(byteIdentityOnly=True,currentSourceExecutionAccepted=False,coverageNotTransferred=True)
    web=dict(prev['historicalWeb']);require(not web['currentSourceExecutionAccepted'],'historical Web domain remains historical')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      witnesses=pins,compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),jars=raw['jars'],
      allPhysicalClassCount=1738,allPhysicalMainSha256=actual,oldPhysicalUnchanged=1669,
      exactPriorMainBytesUnchanged=1738,productionSourceChanges=changes,newSourceDelta=rows,reviewedPomChanges=prev['reviewedPomChanges'],
      currentBatch=dict(source=current['source'],tests=176,suites=24,physicalClasses=batch,counters=current['counters'],actualCrcMismatch=0,
        actualSessions=1,currentSourceExecutionAccepted=True),historicalApi=api,historicalWeb=web,
      currentNormalCompileSdkJarHashes=deps,currentBatchAuxiliaryJarHashes=aux,apiOnlyAuxiliaryJarHashes=sdk.EXTRA,
      architecture=dict(result=arch['result'],originalReceipt=arch['receipt'],proofReusedByExactByteIdentity=True,newRuleExecution=False),
      testsExecutedByBridge=0,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,targetClassLoadOrInitialization=False,original4222Replayed=False,original44Replayed=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1738,currentBatch=43,historicalApi=16,historicalWeb=10,sources=81,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
