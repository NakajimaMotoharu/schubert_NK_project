"""Same-source API174 versus historical Batch261/Web77; exact all1791 including debug."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
import pg6966_chr_adapter_host as host
import pg6960_archunit as architecture
import pg7032_monitoring_six_artifact_post as steps
import pg7102_web_http_six_post as web_pom
import pg8026_exact_duration_six_compile_v4 as compilation
import pg7362_api_pool_observation_host as sdk
import pg7628_api_inbox_replay_host as inbox
from batch_metric_pom_contract import verify_batch_core_pom
from host_tool_invocation import capture,verify
from pg7750_media_stream_six_post_v2 import historical
SLOT=host.W/'pg8040-exact-duration-six-post-v5'
OUT=host.BASE/'PG8040-exact-duration-six-post-v5'
PINS={
'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
'current':('PG8038-exact-duration-post-v5/manifest.json',None),
'batch':('PG7820-restart-metric-six-post-v1/manifest.json','517a658dff9a99eed436382515768fdb4cb4413d18552087c445bf5e9448ad27'),
'web':('PG7948-web-outbox-six-post-v1/manifest.json','14e0f829e73b4ee3ec3f83c288cefd79b5f672171a5c074d9d0d8a69616ece2e'),
'webq':('PG7946-web-outbox-post-v1/manifest.json','7bfe1a10cdbaf81a9b39bb3c8a70774bf37d712c11f6e7f02b017a55bd97a5f0'),
'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
def require(value,message):
    if not value:raise ValueError(message)
def main():
    invocation=capture(Path(__file__));require(not SLOT.exists() and not OUT.exists(),'new-only exact post')
    proofs={};pins={}
    for key,(path,digest) in PINS.items():
        f=host.BASE/path;h=host.sha(f);require(digest is None or h==digest,'pinned original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=h)
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes());snapshot=compilation.SLOT/'snapshot';inputs=raw['begin']['inputHashes']
    c=proofs['current'];batch=proofs['batch']['currentBatch'];web=proofs['web']['currentWeb'];wq=proofs['webq']
    require(raw['source']==c['source']==compilation.SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
      and raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY'
      and c['actualExit']==0 and c['tests']==174 and c['suites']==21 and len(c['physicalClasses'])==38
      and len(c['executableClasses'])==36 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'genuine current174/36/singleexec and compile-only0')
    require(all(host.sha(snapshot/p)==h for p,h in inputs.items()),'all frozen normal Main/Test/POM bytes')
    require(batch['source']=='3751f2150898ddd0ff939571f99e13c888e17653' and batch['tests']==261 and batch['suites']==34
      and len(batch['physicalClasses'])==65 and batch['actualCrcMismatch']==0 and batch['actualSessions']==1,'historical Batch261 monitoring65, no originalStep double-count')
    require(web['source']==wq['source']=='f84acdd7d3b146c3cf6171cfabe66e4d18e35a82'
      and web['tests']==wq['tests']==77 and len(web['physicalClasses'])==19 and wq['actualCrcMismatch']==0
      and wq['actualSessions']==1 and {'web:'+p:h for p,h in wq['physicalClasses'].items()}==web['physicalClasses'],'historical Web77 exact witness')
    baseline=proofs['original']['allPhysicalMainSha256'];api={'api:'+p:h for p,h in c['physicalClasses'].items()}
    require(len(baseline)==1669,'original physical1669')
    expected=dict(baseline)
    for role,domain in (('api',api),('batch',batch['physicalClasses']),('web',web['physicalClasses'])):
        require(not(set(expected)&set(domain)) and all(p.startswith(role+':dev/codex/schubert/nk/'+role+'/monitoring/') for p in domain),'disjoint true role additional physical')
        expected.update(domain)
    require(len(expected)==1791,'1669 plus122 additional physical, originalStep only once')
    actual={};jars={};require(set(raw['jars'])==set(architecture.MODULES),'all six normal Jars')
    for role,row in raw['jars'].items():
        f=Path(row['path']);require(host.sha(f)==row['sha256'],'frozen normal Jar');jars[role]=f
        with zipfile.ZipFile(f) as jar:
            for entry in jar.namelist():
                if entry.endswith('.class'):
                    key=role+':'+entry;require(key not in actual,'unique physical owner')
                    actual[key]=hashlib.sha256(jar.read(entry)).hexdigest()
    require(actual==expected,'all1791 physical bytes incl debug exact')
    parts=subprocess.check_output(['git','diff','--name-status','-z',proofs['original']['productionSource'],compilation.SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'complete delta grammar');rows=[];poms={}
    reviewers={'src/schubert-nk-api/pom.xml':verify_batch_core_pom,'src/schubert-nk-batch/pom.xml':verify_batch_core_pom,'src/schubert-nk-web/pom.xml':web_pom.verify_core_pom}
    extras={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':'WBS-C02',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':'WBS-C06'}
    for i in range(0,len(parts),2):
        status,path=parts[i].decode(),parts[i+1].decode()
        allowed=path.startswith(tuple('src/schubert-nk-'+role+'/src/'+kind+suffix for role in ('api','web','batch')
          for kind,suffix in (('main/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/resources/','monitoring/'))))
        if status=='M':
            require(path in reviewers and path not in poms,'only declared POM modifications')
            poms[path]=reviewers[path](subprocess.check_output(['git','show',proofs['original']['productionSource']+':'+path],cwd=host.ROOT),(snapshot/path).read_bytes())
        else:require(status=='A' and (allowed or path in extras),'no legacy Main/DDL/config/oracle modification')
        rows.append(dict(path=path,status=status,sha256=inputs[path],owner=extras.get(path,'WBS-P018-09'),
          sharedReference='WBS-C07' if allowed or path in poms else None,sharedAdditionalCostPp=0))
    require(len(rows)==138 and set(poms)==set(reviewers),'all137 source owners and exact three POM guards')
    common=proofs['batch']['currentBatchAuxiliaryJarHashes'];deps=raw['begin']['dependencyJarHashes']
    require(common==wq['additionalSdkAuxiliaryJarHashes'] and len(common)==4
      and not(set(common)&set(sdk.EXTRA)) and deps==sdk.DEPENDENCIES=={**common,**sdk.EXTRA}==c['additionalSdkAuxiliaryJarHashes']
      and all(host.sha(Path(p))==h for p,h in deps.items()),'exact SDK4 plus API2 bindings')
    inbox.verify_inputs();preflight=json.loads(inbox.PREFLIGHT.read_bytes())
    protocol={k.removeprefix('protocol:'):v for k,v in actual.items() if k.startswith('protocol:')}
    require(len(protocol)==176 and protocol==preflight['allSelectedClassSha256']
      and c['productionDependencyJarHashes']=={inbox.PROTOCOL_PATH:inbox.PROTOCOL_SHA},'all176 normal protocol bytes equal executed dependency, not old coverage')
    arch=proofs['architecture'];require(host.sha(architecture.SOURCE)==arch['toolSourceSha256']
      and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA,'exact static architecture tool/library')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT;classes=SLOT/'classes';classes.mkdir()
    receipt,_=steps.step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(receipt['actualExit']==0,'audit compile0')
    receipt,stdout=steps.step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
      'ModuleDependencyAudit',*[r+'='+str(jars[r]) for r in architecture.MODULES]])
    result=architecture.parse(stdout);require(receipt['actualExit']==0 and result['physical']==1791 and len(result['rules'])==5
      and not result['findings'] and all(v==0 for v in result['rules'].values()),'all1791/five rules zero')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),jars=raw['jars'],allPhysicalClassCount=1791,oldPhysicalUnchanged=1669,
      currentApi=dict(source=c['source'],tests=174,suites=21,physicalClasses=api,counters=c['counters'],actualCrcMismatch=0,actualSessions=1,currentSourceExecutionAccepted=True),
      historicalBatch=historical(batch),historicalWeb=historical(web),newSourceDelta=rows,reviewedPomChanges=poms,currentNormalCompileSdkJarHashes=deps,
      unmeasuredProductionDependencyJarHashes=c['productionDependencyJarHashes'],protocolDependencyPhysicalBytesMatched=176,protocolDependencyCoverageTransferred=False,
      architecture=dict(result=result,receipt=receipt),targetClassLoadOrInitialization=False,coverageUnion=False,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,testsExecutedByPost=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1791,currentApi=38,historicalBatch=65,historicalWeb=19,sources=138,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()



