"""API current8 vs historical Batch169/Web23: exact normal Jar domains and three POM nodes, no coverage union."""
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
import pg7480_api_outbox_connection_six_compile as compilation
import pg7362_api_pool_observation_host as sdk
from batch_metric_pom_contract import verify_batch_core_pom
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7306-api-async-metric-six-post-v1'
OUT=host.BASE/'PG7306-api-async-metric-six-post-v1'
CURRENT_TESTS=8
CURRENT_SUITES=1
CURRENT_PHYSICAL=4
PHYSICAL_COUNT=1726
SOURCE_DELTA_COUNT=65
EXTRA_CURRENT_AUXILIARY_JARS={}
PINS={
 'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
 'currentApi':('PG7302-api-async-metric-post-v1/manifest.json','246b450c115954b30a6246c71bda7e5a2b25273fea211e32d729eb9b1b0304fa'),
 'batchHistory':('PG7292-transfer-health-six-post-v1/manifest.json','47ce5233888b5518fd0dc683dfbf29b8429a75adbc3439c4825d581ad12202ce'),
 'webHistory':('PG7142-http-terminal-six-post-v1/manifest.json','e29b54744f769b519aec562f6e1bccbcf3535ab448439dd365efcaf07a900ff7'),
 'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
POM_REVIEWERS={
 'src/schubert-nk-web/pom.xml':web_pom.verify_core_pom,
 'src/schubert-nk-batch/pom.xml':verify_batch_core_pom,
 'src/schubert-nk-api/pom.xml':verify_batch_core_pom}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only exact multidomain post')
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes())
    require(raw['source']==compilation.SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
      and raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY','genuine original normal compile, not executed PT')
    snapshot=compilation.SLOT/'snapshot'
    require(all(host.sha(snapshot/p)==h for p,h in raw['begin']['inputHashes'].items()),'all fixed normal Main/Test/POM bytes')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original public proof pin');proofs[key]=json.loads(file.read_bytes())
    old=proofs['original'];current=proofs['currentApi'];batch=proofs['batchHistory']['currentBatch'];web=dict(proofs['webHistory']['currentWeb'])
    webq=proofs['webQualification']
    require(webq['source']==web['source'] and {'web:'+p:h for p,h in webq['physicalClasses'].items()}==web['physicalClasses'],'historical Web physical and actual qualification witness agree')
    web.update(actualCrcMismatch=webq['actualCrcMismatch'],actualSessions=webq['actualSessions'])
    require(old['productionSource']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
      and current['source']==compilation.SOURCE and current['tests']==CURRENT_TESTS and current['suites']==CURRENT_SUITES
      and current['actualCrcMismatch']==0 and current['actualSessions']==1,'current API actual exact source/count/session')
    require(batch['source']=='9d8e520376501de825f26f963d6914beb98b890c' and batch['tests']==176
      and web['source']=='6dbf7f17b369f4859517ef544e55cc5f09d61d8f' and web['tests']==27
      and batch['actualCrcMismatch']==web['actualCrcMismatch']==0 and batch['actualSessions']==web['actualSessions']==1,
      'exact historical domains only, not new-source execution')
    baseline=old['allPhysicalMainSha256'];api={'api:'+k:v for k,v in current['physicalClasses'].items()}
    require(len(baseline)==1669 and len(api)==CURRENT_PHYSICAL and len(batch['physicalClasses'])==43 and len(web['physicalClasses'])==10,
      'exact original1669/API/current and historical43/10 physical counts')
    domains=[('ORIGINAL_BYTE_IDENTITY',baseline),('HISTORICAL_BATCH_BYTE_ONLY',batch['physicalClasses']),
      ('HISTORICAL_WEB_BYTE_ONLY',web['physicalClasses']),('CURRENT_API_QUALIFIED',api)]
    expected={}
    for name,entries in domains:
        require(not (set(expected)&set(entries)),'all declared physical domains disjoint')
        if name!='ORIGINAL_BYTE_IDENTITY':
            role='api' if name=='CURRENT_API_QUALIFIED' else 'batch' if name=='HISTORICAL_BATCH_BYTE_ONLY' else 'web'
            require(all(k.startswith(role+':dev/codex/schubert/nk/'+role+'/monitoring/') for k in entries),'actual role/namespace owners, not aliases')
        expected.update(entries)
    require(len(expected)==PHYSICAL_COUNT,'exact union of physical bytes, never union of coverage')
    jars={};actual={};require(set(raw['jars'])==set(architecture.MODULES),'all six normal artifacts')
    for role,item in raw['jars'].items():
        file=Path(item['path']);require(host.sha(file)==item['sha256'],'original normal Jar bytes');jars[role]=file
        with zipfile.ZipFile(file) as jar:
            for entry in jar.namelist():
                if not entry.endswith('.class'):continue
                name=role+':'+entry;require(name not in actual,'unique actual physical class owner')
                actual[name]=hashlib.sha256(jar.read(entry)).hexdigest()
    require(actual==expected,'every physical byte including debug exact; original1669 unchanged/currentAPI verified/historical not executed')
    parts=subprocess.check_output(['git','diff','--name-status','-z',old['productionSource'],compilation.SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'full source delta grammar')
    extras={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':'WBS-C02',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':'WBS-C06'}
    rows=[];reviewed={}
    for i in range(0,len(parts),2):
        status,path=parts[i].decode(),parts[i+1].decode()
        allowed=path.startswith(tuple('src/schubert-nk-'+role+'/src/'+kind+suffix
          for role in ('batch','web','api') for kind,suffix in (
          ('main/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),
          ('test/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/resources/','monitoring/'))))
        if status=='M':
            require(path in POM_REVIEWERS and path not in reviewed,'only three explicitly declared POM dependency changes')
            before=subprocess.check_output(['git','show',old['productionSource']+':'+path],cwd=host.ROOT)
            reviewed[path]=POM_REVIEWERS[path](before,(snapshot/path).read_bytes())
        else:require(status=='A' and (allowed or path in extras),'no legacy Java/DDL/config/oracle modification')
        rows.append(dict(path=path,status=status,sha256=host.sha(snapshot/path),owner=extras.get(path,'WBS-P018-09'),
          sharedReference='WBS-C07' if allowed or path in reviewed else None,sharedAdditionalCostPp=0))
    require(len(rows)==SOURCE_DELTA_COUNT and set(reviewed)==set(POM_REVIEWERS),'all declared source owners and all three exact semantic guards')
    sdk=raw['begin']['dependencyJarHashes']
    common=proofs['batchHistory']['currentBatchAuxiliaryJarHashes']
    require(common==webq['additionalSdkAuxiliaryJarHashes'] and not(set(common)&set(EXTRA_CURRENT_AUXILIARY_JARS))
      and sdk=={**common,**EXTRA_CURRENT_AUXILIARY_JARS}==current['additionalSdkAuxiliaryJarHashes']
      and all(host.sha(Path(p))==h for p,h in sdk.items()),
      'same original four SDK bytes plus explicitly pinned current-only auxiliary inputs, not historical execution transfer')
    prior=proofs['architecture']
    require(host.sha(architecture.SOURCE)==prior['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA
      and host.sha(architecture.SLF)==architecture.SLF_SHA,'official unchanged architecture tool/library bytes')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT;classes=SLOT/'classes';classes.mkdir()
    receipt,_=steps.step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(receipt['actualExit']==0,'architecture helper normal compile zero')
    receipt,stdout=steps.step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
      'ModuleDependencyAudit',*[r+'='+str(jars[r]) for r in architecture.MODULES]])
    result=architecture.parse(stdout)
    require(receipt['actualExit']==0 and result['physical']==PHYSICAL_COUNT and not result['findings']
      and all(v==0 for v in result['rules'].values()),'all actual classes/five architecture rules zero')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      witnesses=PINS,compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),jars=raw['jars'],
      allPhysicalClassCount=PHYSICAL_COUNT,oldPhysicalUnchanged=1669,
      currentApi=dict(source=current['source'],tests=CURRENT_TESTS,suites=CURRENT_SUITES,physicalClasses=api,counters=current['counters'],
        actualCrcMismatch=0,actualSessions=1,currentSourceExecutionAccepted=True),
      historicalBatch=dict(source=batch['source'],tests=176,physicalClasses=batch['physicalClasses'],byteIdentityOnly=True,
        currentSourceExecutionAccepted=False,coverageNotTransferred=True),
      historicalWeb=dict(source=web['source'],tests=27,physicalClasses=web['physicalClasses'],byteIdentityOnly=True,
        currentSourceExecutionAccepted=False,coverageNotTransferred=True),newSourceDelta=rows,reviewedPomChanges=reviewed,
      currentNormalCompileSdkJarHashes=sdk,currentOnlyAuxiliaryJarHashes=EXTRA_CURRENT_AUXILIARY_JARS,
      architecture=dict(result=result,receipt=receipt),targetClassLoadOrInitialization=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,coverageUnion=False,
      original4222Replayed=False,original44Replayed=False,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=len(actual),currentApi=len(api),historicalBatchOnly=43,historicalWebOnly=10,
      sourceDeltas=len(rows),architecture=result['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))

SLOT=host.W/'pg7482-api-outbox-connection-six-post-v1'
OUT=host.BASE/'PG7482-api-outbox-connection-six-post-v1'
CURRENT_TESTS=98
CURRENT_SUITES=12
CURRENT_PHYSICAL=21
PHYSICAL_COUNT=1743
SOURCE_DELTA_COUNT=88
EXTRA_CURRENT_AUXILIARY_JARS=sdk.EXTRA
PINS=dict(PINS)
PINS['batchHistory']=('PG7426-batch-generated-byte-bridge-v1/manifest.json','5b00abaa2d709695bfafe0f593ee20dd9ccbdea521d6fd2ef8cf52e1551dd9d4')
PINS['webHistory']=('PG7442-web-generated-byte-trace-v1/manifest.json','976417dff5cf31223ebf5593a59581e95fe7321af9c144a68a18a8194e360041')
PINS['webQualification']=('PG7436-web-generated-post-v1/manifest.json','b41d9dcff2075a10b3192f9dde387b0f0e2e36473b83bea4a475aae4ef4cbe37')
if __name__=='__main__':
    path='PG7478-api-outbox-connection-post-v1/manifest.json'
    PINS['currentApi']=(path,host.sha(host.BASE/path))
    main()
