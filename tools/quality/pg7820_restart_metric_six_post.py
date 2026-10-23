"""Explicit current Batch261 versus historical API130/Web51; all1766 actual Main bytes and rules."""
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
import pg7818_restart_metric_six_compile as compilation
import pg7362_api_pool_observation_host as sdk
from batch_metric_pom_contract import verify_batch_core_pom
from host_tool_invocation import capture,verify
from pg7750_media_stream_six_post_v2 import historical

SLOT=host.W/'pg7820-restart-metric-six-post-v1'
OUT=host.BASE/'PG7820-restart-metric-six-post-v1'
PINS={
 'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
 'currentBatch':('PG7816-restart-metric-post-v1/manifest.json',None),
 'historicalApi':('PG7696-mq-pressure-connection-six-post-v1/manifest.json','7599f4d6708a3a42137d719862aa9a40e8a0d7f315e75f044e73429074c475f2'),
 'historicalWeb':('PG7776-media-bytes-six-post-v1/manifest.json','1df8c04e27ca12da724ef28aced0e6ab4f6b34e400b34d7cf3f24a59508d644d'),
 'webQualification':('PG7774-media-bytes-post-v1/manifest.json','f9e8f54f29fe79b739802c520182b211e28d2aa89b450f35d43064198702dcdd'),
 'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not SLOT.exists() and not OUT.exists(),'new-only exact physical post')
    proofs={};pins={}
    for key,(name,digest) in PINS.items():
        path=host.BASE/name;actual=host.sha(path);require(digest is None or actual==digest,'exact original witness')
        proofs[key]=json.loads(path.read_bytes());pins[key]=dict(path=name,sha256=actual)
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes());snapshot=compilation.SLOT/'snapshot';inputs=raw['begin']['inputHashes']
    current=proofs['currentBatch'];api=proofs['historicalApi']['currentApi'];web=dict(proofs['historicalWeb']['currentWeb']);webq=proofs['webQualification']
    require(raw['source']==current['source']==compilation.SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
      and raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY'
      and current['tests']==261 and current['suites']==34 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and len(current['physicalClasses'])==66 and len(current['executableClasses'])==65
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'genuine current Batch253 and normal compile, no Test/source alias')
    require(all(host.sha(snapshot/p)==h for p,h in inputs.items()),'all frozen input bytes')
    require(api['source']=='153b3f3825d470bf15f7e5462e7b0beae199f76e' and api['tests']==130 and api['suites']==16
      and api['actualCrcMismatch']==0 and api['actualSessions']==1 and len(api['physicalClasses'])==26,'exact historical API130 not new execution')
    require(webq['source']==web['source']=='082429175a7c64abd86c8dccca2f8f9be97fdc4a' and webq['tests']==web['tests']==51
      and webq['actualCrcMismatch']==0 and webq['actualSessions']==1
      and {'web:'+p:h for p,h in webq['physicalClasses'].items()}==web['physicalClasses'],'exact historical Web51 bytes and original execution witness')
    baseline=proofs['original']['allPhysicalMainSha256'];batch={'batch:'+p:h for p,h in current['physicalClasses'].items()}
    dependency_key='batch:dev/codex/schubert/nk/batch/repository/BatchStep.class'
    dependency_digest=batch.pop(dependency_key)
    require(dependency_digest==baseline[dependency_key] and len(batch)==65
      and all(p.startswith('batch:dev/codex/schubert/nk/batch/monitoring/') for p in batch),
      'one explicitly measured original dependency already in1669, never double counted as additional physical')
    dependency_name=dependency_key.split(':',1)[1].removesuffix('.class')
    dependency_counters=current['executableClasses'][dependency_name]['counters']
    monitoring_counts={kind:dict(missed=sum(v['counters'][kind]['missed'] for name,v in current['executableClasses'].items() if name!=dependency_name),
      covered=sum(v['counters'][kind]['covered'] for name,v in current['executableClasses'].items() if name!=dependency_name)) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    require(len(baseline)==1669,'all original physical inputs retained')
    expected=dict(baseline)
    for role,domain in (('batch',batch),('api',api['physicalClasses']),('web',web['physicalClasses'])):
        require(not(set(expected)&set(domain)) and all(p.startswith(role+':dev/codex/schubert/nk/'+role+'/monitoring/') for p in domain),
          'disjoint true role namespaces, no historical alias')
        expected.update(domain)
    actual={};jars={};require(set(raw['jars'])==set(architecture.MODULES),'all six normal Jars')
    for role,row in raw['jars'].items():
        file=Path(row['path']);require(host.sha(file)==row['sha256'],'original normal Jar hash');jars[role]=file
        with zipfile.ZipFile(file) as jar:
            for entry in jar.namelist():
                if entry.endswith('.class'):
                    key=role+':'+entry;require(key not in actual,'unique actual class owner')
                    actual[key]=hashlib.sha256(jar.read(entry)).hexdigest()
    require(actual==expected and len(actual)==1774,'every actual Main byte incl debug, original1669 unchanged/current64/historical40')
    parts=subprocess.check_output(['git','diff','--name-status','-z',proofs['original']['productionSource'],compilation.SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'complete change grammar');rows=[];poms={}
    reviewers={'src/schubert-nk-api/pom.xml':verify_batch_core_pom,'src/schubert-nk-batch/pom.xml':verify_batch_core_pom,'src/schubert-nk-web/pom.xml':web_pom.verify_core_pom}
    extras={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':'WBS-C02',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':'WBS-C06'}
    for i in range(0,len(parts),2):
        status,path=parts[i].decode(),parts[i+1].decode()
        allowed=path.startswith(tuple('src/schubert-nk-'+role+'/src/'+kind+suffix for role in ('api','web','batch')
          for kind,suffix in (('main/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/resources/','monitoring/'))))
        if status=='M':
            require(path in reviewers and path not in poms,'only approved three POM nodes modified')
            before=subprocess.check_output(['git','show',proofs['original']['productionSource']+':'+path],cwd=host.ROOT)
            poms[path]=reviewers[path](before,(snapshot/path).read_bytes())
        else:require(status=='A' and (allowed or path in extras),'no legacy source/DDL/config/oracle rewritten')
        rows.append(dict(path=path,status=status,sha256=inputs[path],owner=extras.get(path,'WBS-P018-09'),
          sharedReference='WBS-C07' if allowed or path in poms else None,sharedAdditionalCostPp=0))
    require(len(rows)==121 and set(poms)==set(reviewers),'all121 source owners and explicit POM semantics')
    common=current['additionalSdkAuxiliaryJarHashes'];deps=raw['begin']['dependencyJarHashes']
    require(common==webq['additionalSdkAuxiliaryJarHashes'] and len(common)==4 and not(set(common)&set(sdk.EXTRA))
      and deps==sdk.DEPENDENCIES=={**common,**sdk.EXTRA} and all(host.sha(Path(p))==h for p,h in deps.items()),'current Batch/Web SDK4 versus normal API-only2 explicit byte bindings')
    arch=proofs['architecture'];require(host.sha(architecture.SOURCE)==arch['toolSourceSha256']
      and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA,'exact official architecture tool/library pins')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT;classes=SLOT/'classes';classes.mkdir()
    compiled,_=steps.step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(compiled['actualExit']==0,'new source necessary static helper compile zero')
    receipt,stdout=steps.step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
      'ModuleDependencyAudit',*[r+'='+str(jars[r]) for r in architecture.MODULES]])
    result=architecture.parse(stdout);require(receipt['actualExit']==0 and result['physical']==1774
      and len(result['rules'])==5 and not result['findings'] and all(v==0 for v in result['rules'].values()),'all actual1774/five rules zero')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),jars=raw['jars'],allPhysicalClassCount=1774,oldPhysicalUnchanged=1669,
      currentBatch=dict(source=current['source'],tests=261,suites=34,physicalClasses=batch,counters=monitoring_counts,
        qualifiedPostCountersIncludingOriginalDependency=current['counters'],actualCrcMismatch=0,actualSessions=1,currentSourceExecutionAccepted=True),
      originalCurrentDependency=dict(source=current['source'],physicalClasses={dependency_key:dependency_digest},
        counters=dependency_counters,crc64=current['executableClasses'][dependency_name]['crc64'],sourcePath=current['explicitOriginalDependencySource'],
        sourceSha256=current['sourceFiles'][current['explicitOriginalDependencySource']],owner='WBS-P017-02',
        currentSourceExecutionAccepted=True,alreadyInOriginal1669=True,additionalPhysicalCount=0,additionalBudgetPp=0),
      historicalApi=historical(api),
      historicalWeb=historical(web),
      newSourceDelta=rows,reviewedPomChanges=poms,currentNormalCompileSdkJarHashes=deps,currentBatchAuxiliaryJarHashes=common,apiOnlyAuxiliaryJarHashes=sdk.EXTRA,
      architecture=dict(result=result,receipt=receipt),targetClassLoadOrInitialization=False,coverageUnion=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,testsExecutedByPost=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1774,currentBatch=65,historicalApi=26,historicalWeb=14,sources=121,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
