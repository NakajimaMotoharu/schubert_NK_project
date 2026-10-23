"""Whole physical inventory; current HTTP qualification and historical byte witnesses stay separate."""
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
import pg7100_web_http_six_compile as compile_stage
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7102-web-http-six-post-v1'
OUT=host.BASE/'PG7102-web-http-six-post-v1'
PINS={
 'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
 'batchHistory':('PG7090-registry-missing-six-post-v1/manifest.json','63949a081586eb21c52e790267c74e4069633b30bcc5b2d3752290e5910c645a'),
 'currentHttp':('PG7096-web-http-metric-post-v1/manifest.json','cbcb5c9821ccbcf05d9f73701e252c2a8a833773d6d3ca2614620a33f8c3d01a'),
 'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists(),'new-only public physical post')
    os.umask(0o077);SLOT.mkdir(exist_ok=True);steps.SLOT=SLOT
    raw=json.loads((compile_stage.SLOT/'manifest.safe.json').read_bytes())
    require(raw['source']==compile_stage.SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
            and raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY',
            'original current-source compile-only terminal, never PT pass')
    snapshot=compile_stage.SLOT/'snapshot'
    require(all(host.sha(snapshot/p)==h for p,h in raw['begin']['inputHashes'].items()),'all immutable compile inputs exact')
    witnesses={}
    for name,(path,digest) in PINS.items():
        require(host.sha(host.BASE/path)==digest,'all original witness hashes pinned')
        witnesses[name]=json.loads((host.BASE/path).read_bytes())
    old=witnesses['original'];batch=witnesses['batchHistory'];http=witnesses['currentHttp']
    require(old['productionSource']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
      and batch['source']=='71c6be37c1a0038314b66565b1188d6488bc7c8d'
      and http['source']==compile_stage.SOURCE and http['tests']==6
      and http['actualCrcMismatch']==0 and http['actualSessions']==1,'distinct genuine source domains, HTTP actually current')
    baseline=old['allPhysicalMainSha256'];prior=batch['newPhysicalClasses']
    current={'web:'+path:digest for path,digest in http['physicalClasses'].items()}
    require(len(baseline)==1669 and len(prior)==20 and len(current)==7
      and not (set(baseline)&set(prior) or set(baseline)&set(current) or set(prior)&set(current)),
      'all three physical domains are exact and disjoint')
    physical={};jars={}
    require(set(raw['jars'])==set(compile_stage.stage.ROLES),'all six original actual Jars')
    for role,item in raw['jars'].items():
        path=Path(item['path']);require(host.sha(path)==item['sha256'],'actual current Jar hash')
        jars[role]=path
        with zipfile.ZipFile(path) as jar:
            for entry in jar.namelist():
                if entry.endswith('.class'):
                    key=role+':'+entry
                    require(key not in physical,'unique physical module/class')
                    physical[key]=hashlib.sha256(jar.read(entry)).hexdigest()
    require(physical=={**baseline,**prior,**current} and len(physical)==1696,
            'old1669 and historical batch20 byte-identical, all seven current HTTP physical classes exact')
    parts=subprocess.check_output(['git','diff','--name-status','-z',old['productionSource'],compile_stage.SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'complete added-source grammar')
    extras={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':'WBS-C02',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':'WBS-C06'}
    source_delta=[]
    for i in range(0,len(parts),2):
        status,path=parts[i].decode(),parts[i+1].decode()
        allowed=path.startswith(tuple('src/schubert-nk-'+role+'/src/'+kind+suffix
          for role in ('batch','web') for kind,suffix in (
          ('main/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),
          ('test/java/','dev/codex/schubert/nk/'+role+'/monitoring/'),('test/resources/','monitoring/'))))
        require(status=='A' and (allowed or path in extras),'only declared pure monitoring/source-test additions')
        source_delta.append(dict(path=path,sha256=host.sha(snapshot/path),owner=extras.get(path,'WBS-P018-09'),
          sharedReference='WBS-C07' if allowed else None,sharedAdditionalCostPp=0))
    require(len(source_delta)==29,'all29 additions, no old Main/POM/config/DDL changed')
    previous_arch=witnesses['architecture']
    require(host.sha(architecture.SOURCE)==previous_arch['toolSourceSha256']
      and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA,
      'unchanged official architecture helper and pinned dependencies')
    classes=SLOT/'classes';classes.mkdir(exist_ok=True)
    receipt,_=steps.step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(receipt['actualExit']==0,'static helper compile zero')
    receipt,text=steps.step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
      'ModuleDependencyAudit',*[role+'='+str(jars[role]) for role in architecture.MODULES]])
    result=architecture.parse(text)
    require(receipt['actualExit']==0 and result['physical']==1696 and not result['findings']
      and all(v==0 for v in result['rules'].values()),'all1696 fresh physical classes/five rules zero')
    value=dict(actualExit=0,source=compile_stage.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      invocation=invocation,compileManifestSha256=host.sha(compile_stage.SLOT/'manifest.safe.json'),witnesses=PINS,
      jars=raw['jars'],allPhysicalClassCount=1696,oldPhysicalUnchanged=1669,
      historicalBatch=dict(source=batch['source'],physicalClasses=prior,byteIdentityOnly=True,
        currentSourceExecutionAccepted=False,coverageNotTransferred=True),
      currentHttp=dict(source=http['source'],tests=6,physicalClasses=current,counters=http['counters'],
        actualCrcMismatch=0,actualSessions=1),newSourceDelta=source_delta,
      architecture=dict(result=result,receipt=receipt),targetClassesLoadedOrInitialized=False,
      testsExecutedByPost=0,actualVmActions=0,actualDatabaseActions=0,
      original4222Repeated=False,batch73Repeated=False,common44Repeated=False,coverageUnion=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1696,oldUnchanged=1669,historicalBatchOnly=20,
      currentHttp=7,architecture=result['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
