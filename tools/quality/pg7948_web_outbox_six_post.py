"""True current Web77 versus historical Batch261/API162, every normal physical Main byte and five rules."""
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
import pg7942_web_outbox_six_compile as compilation
import pg7944_web_outbox_host as execution
import pg7362_api_pool_observation_host as sdk
from batch_metric_pom_contract import verify_batch_core_pom
from host_tool_invocation import capture,verify
from pg7750_media_stream_six_post_v2 import historical

SLOT=host.W/'pg7948-web-outbox-six-post-v1'
OUT=host.BASE/'PG7948-web-outbox-six-post-v1'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not SLOT.exists() and not OUT.exists(),'new-only exact role-aware physical post')
    proofs={};pins={}
    for key,path,digest in (
      ('original','PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      ('currentWeb','PG7946-web-outbox-post-v1/manifest.json',None),
      ('history','PG7820-restart-metric-six-post-v1/manifest.json','517a658dff9a99eed436382515768fdb4cb4413d18552087c445bf5e9448ad27'),
      ('apiHistory','PG7918-mq-event-six-post-v1/manifest.json','db5a55e3d177bb06a9499fa05591c9c463bf70ec1e026990eb3f83a60a5664e8'),
      ('architecture','PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original public witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    normal=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes());snapshot=compilation.SLOT/'snapshot'
    inputs=normal['begin']['inputHashes'];current=proofs['currentWeb'];batch=proofs['history']['currentBatch'];api=proofs['apiHistory']['currentApi']
    require(normal['source']==current['source']==compilation.SOURCE and normal['actualExit']==normal['terminal']['actualExit']==0
      and normal['testsExecuted']==0 and normal['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY'
      and current['actualExit']==0 and current['tests']==77 and current['suites']==10 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and len(current['physicalClasses'])==19 and len(current['executableClasses'])==18
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'genuine current77/18 and normal compile not PT/source alias')
    require(all(host.sha(snapshot/p)==h for p,h in inputs.items()),'all frozen normal Main/Test/POM bytes')
    require(batch['source']=='3751f2150898ddd0ff939571f99e13c888e17653' and batch['tests']==261 and batch['suites']==34
      and len(batch['physicalClasses'])==65 and batch['actualCrcMismatch']==0 and batch['actualSessions']==1
      and api['source']=='23b74be401690ecb0f0007a66869c4ea2a699b02' and api['tests']==162 and api['suites']==20
      and len(api['physicalClasses'])==35 and api['actualCrcMismatch']==0 and api['actualSessions']==1,'exact historical role witnesses, never current tests')
    baseline=proofs['original']['allPhysicalMainSha256'];web={'web:'+p:h for p,h in current['physicalClasses'].items()}
    require(len(baseline)==1669,'all original1669 retained')
    expected=dict(baseline)
    for role,domain in (('web',web),('batch',batch['physicalClasses']),('api',api['physicalClasses'])):
        require(not(set(expected)&set(domain)) and all(p.startswith(role+':dev/codex/schubert/nk/'+role+'/monitoring/') for p in domain),
          'disjoint actual physical namespaces/owners, no alias')
        expected.update(domain)
    actual={};jars={};require(set(normal['jars'])==set(architecture.MODULES),'all six normal artifacts')
    for role,item in normal['jars'].items():
        file=Path(item['path']);require(host.sha(file)==item['sha256'],'exact normal Jar bytes');jars[role]=file
        with zipfile.ZipFile(file) as archive:
            for entry in archive.namelist():
                if not entry.endswith('.class'):continue
                key=role+':'+entry;require(key not in actual,'unique actual physical owner')
                actual[key]=hashlib.sha256(archive.read(entry)).hexdigest()
    require(actual==expected and len(actual)==1788,'every normal physical byte incl debug matches original/current/historical domains')
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes());deps=raw['begin']['dependencyHashes']
    require(raw['source']==compilation.SOURCE and raw['actualExit']==0 and raw['begin']['compileManifestSha256']==host.sha(compilation.SLOT/'manifest.safe.json')
      and all(deps.get(item['path'])==item['sha256'] for item in normal['jars'].values()),'actual original Web JVM loads all current reactor Jars, not stale M2 internal artifact')
    require(not any('/m2/repository/dev/codex/schubert/' in p for p in deps),'no cached internal snapshot in actual runtime bindings')
    sdk_pins=normal['begin']['dependencyJarHashes']
    require(sdk_pins==sdk.DEPENDENCIES and len(current['additionalSdkAuxiliaryJarHashes'])==4
      and all(sdk_pins.get(p)==deps.get(p)==h and host.sha(Path(p))==h for p,h in current['additionalSdkAuxiliaryJarHashes'].items()),
      'current four SDK bytes and normal API-only two stay separate, exact actual/runtime/static bindings')
    parts=subprocess.check_output(['git','diff','--name-status','-z',proofs['original']['productionSource'],compilation.SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'complete source grammar');rows=[];poms={}
    reviewers={'src/schubert-nk-api/pom.xml':verify_batch_core_pom,'src/schubert-nk-batch/pom.xml':verify_batch_core_pom,'src/schubert-nk-web/pom.xml':web_pom.verify_core_pom}
    extras={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':'WBS-C02',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':'WBS-C06'}
    for i in range(0,len(parts),2):
        status,path=parts[i].decode(),parts[i+1].decode()
        allowed=path.startswith(tuple('src/schubert-nk-'+role+'/src/'+kind+suffix for role in ('batch','web','api') for kind,suffix in (
          ('main/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/resources/','monitoring/'))))
        if status=='M':
            require(path in reviewers and path not in poms,'only three declared POM dependency changes')
            before=subprocess.check_output(['git','show',proofs['original']['productionSource']+':'+path],cwd=host.ROOT)
            poms[path]=reviewers[path](before,(snapshot/path).read_bytes())
        else:require(status=='A' and (allowed or path in extras),'no original Main/DDL/config/oracle mutation')
        rows.append(dict(path=path,status=status,sha256=inputs[path],owner=extras.get(path,'WBS-P018-09'),
          sharedReference='WBS-C07' if allowed or path in poms else None,sharedAdditionalCostPp=0))
    require(len(rows)==135 and set(poms)==set(reviewers),'all135 source owners and three complete semantic POM guards')
    prior=proofs['architecture'];require(host.sha(architecture.SOURCE)==prior['toolSourceSha256']
      and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA,'official unchanged architecture tool/library bytes')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT;classes=SLOT/'classes';classes.mkdir()
    compiled,_=steps.step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(compiled['actualExit']==0,'necessary static helper normal compile zero')
    checked,stdout=steps.step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
      'ModuleDependencyAudit',*[role+'='+str(jars[role]) for role in architecture.MODULES]])
    result=architecture.parse(stdout);require(checked['actualExit']==0 and result['physical']==1788 and len(result['rules'])==5
      and not result['findings'] and all(v==0 for v in result['rules'].values()),'all current Main/five architecture rules zero')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),jars=normal['jars'],allPhysicalClassCount=1788,oldPhysicalUnchanged=1669,
      currentWeb=dict(source=current['source'],tests=77,suites=10,physicalClasses=web,counters=current['counters'],actualCrcMismatch=0,actualSessions=1,currentSourceExecutionAccepted=True),
      historicalBatch=historical(batch),
      historicalApi=historical(api),
      newSourceDelta=rows,reviewedPomChanges=poms,currentNormalCompileSdkJarHashes=sdk_pins,currentWebAuxiliaryJarHashes=current['additionalSdkAuxiliaryJarHashes'],
      originalRuntimeDependencyJarHashes=deps,architecture=dict(result=result,receipt=checked),targetClassLoadOrInitialization=False,
      coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,testsExecutedByPost=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1788,currentWeb=19,historicalBatch=65,historicalApi=35,sources=135,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
