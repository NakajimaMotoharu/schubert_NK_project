"""Current Batch83 vs historical Web23, all normal Jar bytes and module ownership; no coverage union."""
import datetime
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg6960_archunit as architecture
import pg7032_monitoring_six_artifact_post as steps
import pg7102_web_http_six_post as pom_contract
import pg7156_filesystem_health_six_compile as compilation
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7158-filesystem-health-six-post-v1'
OUT=host.BASE/'PG7158-filesystem-health-six-post-v1'
CURRENT_TESTS=83
CURRENT_SUITES=12
CURRENT_PHYSICAL=22
PHYSICAL_COUNT=1701
SOURCE_DELTA_COUNT=37
POM_REVIEWERS={'src/schubert-nk-web/pom.xml':pom_contract.verify_core_pom}
PINS={
 'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
 'currentBatch':('PG7154-filesystem-health-post-v1/manifest.json','a86ed6ca91bc6df6d9bd886cf7b487a5253176a2f22b55c7b82b31657a5e110f'),
 'webHistory':('PG7142-http-terminal-six-post-v1/manifest.json','e29b54744f769b519aec562f6e1bccbcf3535ab448439dd365efcaf07a900ff7'),
 'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists(),'new-only physical post')
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes())
    require(raw['source']==compilation.SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
      and raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY','genuine normal compile, PT not run')
    snapshot=compilation.SLOT/'snapshot'
    require(all(host.sha(snapshot/p)==h for p,h in raw['begin']['inputHashes'].items()),'all fixed normal input bytes')
    witnesses={}
    for name,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'each exact original public witness')
        witnesses[name]=json.loads(file.read_bytes())
    old=witnesses['original'];current=witnesses['currentBatch'];history=witnesses['webHistory']
    require(old['productionSource']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
      and current['source']==compilation.SOURCE and current['tests']==CURRENT_TESTS and current['suites']==CURRENT_SUITES
      and current['actualCrcMismatch']==0 and current['actualSessions']==1,'current component exact source/session and historical baseline')
    base=old['allPhysicalMainSha256']
    batch={'batch:'+k:v for k,v in current['physicalClasses'].items()}
    web=history['currentHttp']['physicalClasses']
    require(history['source']=='19c777bf3dbe3ddd0286d4c356a00ca8a47c99c5'
      and history['currentHttp']['tests']==23 and len(base)==1669 and len(batch)==CURRENT_PHYSICAL and len(web)==10
      and all(k.startswith('web:') for k in web),'historical ten Web classes, never current Web execution')
    expected={**base,**batch,**web}
    require(len(expected)==PHYSICAL_COUNT,'all three ownership domains disjoint')
    physical={};jars={}
    require(set(raw['jars'])==set(architecture.MODULES),'all six actual normal Jars')
    for role,item in raw['jars'].items():
        path=Path(item['path']);require(host.sha(path)==item['sha256'],'original normal artifact bytes');jars[role]=path
        with zipfile.ZipFile(path) as jar:
            for entry in jar.namelist():
                if not entry.endswith('.class'):continue
                key=role+':'+entry;require(key not in physical,'unique actual physical owner')
                physical[key]=hashlib.sha256(jar.read(entry)).hexdigest()
    require(physical==expected,'all declared physical bytes exact, original1669 unchanged including debug, current/historical bytes joined')
    parts=subprocess.check_output(['git','diff','--name-status','-z',old['productionSource'],compilation.SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'exact source delta grammar')
    extras={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':'WBS-C02',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':'WBS-C06'}
    source_rows=[];reviewed_poms={}
    for index in range(0,len(parts),2):
        status,path=parts[index].decode(),parts[index+1].decode()
        allowed=path.startswith(tuple('src/schubert-nk-'+role+'/src/'+kind+suffix
          for role in ('batch','web') for kind,suffix in (
          ('main/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),
          ('test/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/resources/','monitoring/'))))
        if status=='M':
            require(path in POM_REVIEWERS and path not in reviewed_poms,'only exact explicitly declared POM semantic changes')
            before=subprocess.check_output(['git','show',old['productionSource']+':'+path],cwd=host.ROOT)
            reviewed_poms[path]=POM_REVIEWERS[path](before,(snapshot/path).read_bytes())
        else:require(status=='A' and (allowed or path in extras),'no undeclared legacy code/config/schema changes')
        source_rows.append(dict(path=path,status=status,sha256=host.sha(snapshot/path),owner=extras.get(path,'WBS-P018-09'),
             sharedReference='WBS-C07' if allowed or path in reviewed_poms else None,sharedAdditionalCostPp=0))
    require(len(source_rows)==SOURCE_DELTA_COUNT and set(reviewed_poms)==set(POM_REVIEWERS),
            'all declared additions and every exact reviewed POM change, no unspecified path')
    require(raw['begin']['dependencyJarHashes']==history['currentSdkJarHashes']
      and all(host.sha(Path(p))==h for p,h in raw['begin']['dependencyJarHashes'].items()),'unchanged actual SDK four jars, not a current Web execution claim')
    prior=witnesses['architecture']
    require(host.sha(architecture.SOURCE)==prior['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA
      and host.sha(architecture.SLF)==architecture.SLF_SHA,'official unchanged architecture tool bytes')
    os.umask(0o077);SLOT.mkdir(exist_ok=True);steps.SLOT=SLOT
    classes=SLOT/'classes';classes.mkdir(exist_ok=True)
    stage,_=steps.step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
       '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(stage['actualExit']==0,'architecture helper compile zero')
    stage,text=steps.step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
       'ModuleDependencyAudit',*[role+'='+str(jars[role]) for role in architecture.MODULES]])
    result=architecture.parse(text)
    require(stage['actualExit']==0 and result['physical']==PHYSICAL_COUNT and not result['findings']
      and all(v==0 for v in result['rules'].values()),'all actual physical classes/five rules zero')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=PINS,
      timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),
      jars=raw['jars'],allPhysicalClassCount=PHYSICAL_COUNT,oldPhysicalUnchanged=1669,
      currentBatch=dict(source=current['source'],tests=CURRENT_TESTS,suites=CURRENT_SUITES,physicalClasses=batch,counters=current['counters'],
                        actualCrcMismatch=0,actualSessions=1,currentSourceExecutionAccepted=True),
      historicalWeb=dict(source=history['source'],physicalClasses=web,byteIdentityOnly=True,currentSourceExecutionAccepted=False,
                         coverageNotTransferred=True),newSourceDelta=source_rows,
      reviewedWebPomChange=reviewed_poms['src/schubert-nk-web/pom.xml'],reviewedPomChanges=reviewed_poms,
      currentNormalCompileSdkJarHashes=raw['begin']['dependencyJarHashes'],architecture=dict(result=result,receipt=stage),
      targetClassLoadOrInitialization=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      original4222Replayed=False,original44Replayed=False,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=len(physical),currentBatch=len(batch),historicalWebOnly=len(web),sourceDeltas=len(source_rows),
      architecture=result['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
