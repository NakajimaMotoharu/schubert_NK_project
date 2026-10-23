"""Fresh six-Jar byte/owner delta and ArchUnit; no target class loading or PT replay."""
import datetime
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg6960_archunit as architecture
import pg7030_monitoring_six_compile as compile_stage

SLOT = host.W/'pg7032-monitoring-six-artifact-post-v1'
OUT = host.BASE/'PG7032-monitoring-six-artifact-post-v1'
ORIGINAL = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
Q_SHA = '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'
COMPONENT_SHA = 'aeabd8ec58d30a538af72ca839a893418d83bb7fd5c43242b5b312e526ef58e7'
ARCH_SHA = '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'


def require(value, message):
    if not value:
        raise ValueError(message)


def step(name, command):
    begin = SLOT/(name+'-begin.safe.json')
    terminal = SLOT/(name+'-exit.safe.json')
    if terminal.exists():
        value=json.loads(terminal.read_bytes())
        require(value['command']==command and host.sha(SLOT/value['stdout'])==value['stdoutSha256'],
                'completed original static step hash/command only')
        return value,(SLOT/value['stdout']).read_text()
    require(not begin.exists(),'unknown unfinished step: preserve and observe, never restart')
    value=dict(command=command,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               stdout=name+'.stdout.safe.log',stderr=name+'.stderr.safe.log')
    host.write(begin,value)
    with (SLOT/value['stdout']).open('xb') as stdout,(SLOT/value['stderr']).open('xb') as stderr:
        child=subprocess.Popen(command,stdout=stdout,stderr=stderr,cwd=SLOT)
        host.write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,command=command,cwd=str(SLOT),
          startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        code=child.wait();stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
    value.update(actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 stdoutSha256=host.sha(SLOT/value['stdout']),stderrSha256=host.sha(SLOT/value['stderr']))
    host.write(terminal,value)
    return value,(SLOT/value['stdout']).read_text()


def main():
    os.umask(0o077)
    require(not OUT.exists(),'new-only post publication')
    SLOT.mkdir(exist_ok=True)
    raw = json.loads((compile_stage.SLOT/'manifest.safe.json').read_bytes())
    require(raw['actualExit']==0 and raw['terminal']['actualExit']==0 and raw['source']==compile_stage.SOURCE,
            'genuine fixed-source six-package terminal zero')
    require(raw['testsExecuted']==0 and raw['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY'
            and set(raw['jars'])==set(compile_stage.ROLES),'compile-only, all six original Jars')
    require(raw['terminal']['beginSha256']==host.sha(compile_stage.SLOT/'begin.safe.json'),
            'original compile begin hash')
    snapshot=compile_stage.SLOT/'snapshot'
    require(all(host.sha(snapshot/p)==h for p,h in raw['begin']['inputHashes'].items()),'fixed entire compile source')
    qp=host.BASE/'PG6930-current4222-cases/qualification.json'
    cp=host.BASE/'PG7028-monitoring-pipeline-post-v1/manifest.json'
    ap=host.BASE/'PG6960-archunit-static-v1/manifest.json'
    require(host.sha(qp)==Q_SHA and host.sha(cp)==COMPONENT_SHA and host.sha(ap)==ARCH_SHA,
            'all original qualification witnesses pinned')
    old=json.loads(qp.read_bytes());component=json.loads(cp.read_bytes());prior_arch=json.loads(ap.read_bytes())
    require(old['productionSource']==ORIGINAL and len(old['allPhysicalMainSha256'])==1669,'exact historical source/class inventory')
    require(component['source']==raw['source'] and component['tests']==48
            and component['actualCrcMismatch']==0 and component['actualSessions']==1,'genuine same-source pure48 qualification')
    physical={};jars={}
    for role,item in raw['jars'].items():
        path=Path(item['path'])
        require(host.sha(path)==item['sha256'],'actual current Jar hash')
        jars[role]=path
        with zipfile.ZipFile(path) as jar:
            for entry in jar.namelist():
                if not entry.endswith('.class'):
                    continue
                key=role+':'+entry
                require(key not in physical,'unique module/class inventory')
                physical[key]=hashlib.sha256(jar.read(entry)).hexdigest()
    baseline=old['allPhysicalMainSha256']
    require(set(baseline)<=set(physical) and all(physical[k]==v for k,v in baseline.items()),
            'all old1669 physical bytes preserved, debug mismatch is not ignored')
    added={k:v for k,v in physical.items() if k not in baseline}
    expected={'batch:'+k:v for k,v in component['physicalClasses'].items()}
    require(added==expected and len(added)==15 and len(physical)==1684,
            'exact same-source qualified14 executables plus one metadata class')
    parts=subprocess.check_output(['git','diff','--name-status','-z',ORIGINAL,raw['source'],'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    source_delta=[]
    require(len(parts)%2==0,'full source delta grammar')
    for index in range(0,len(parts),2):
        status=parts[index].decode();path=parts[index+1].decode()
        require(status=='A' and path.startswith((
          'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/',
          'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/',
          'src/schubert-nk-batch/src/test/resources/monitoring/')),'only exact public monitoring additions, no old source changed')
        source_delta.append(dict(path=path,sha256=host.sha(snapshot/path),owner='WBS-P018-09',
                                 sharedReference='WBS-C07',sharedAdditionalCostPp=0,acceptance='NOT_WHOLE_LEAF_ACCEPTED'))
    require(len(source_delta)==15,'eight Main sources/six tests/one independent TSV')
    require(host.sha(architecture.SOURCE)==prior_arch['toolSourceSha256']
            and host.sha(architecture.ARCH)==architecture.ARCH_SHA
            and host.sha(architecture.SLF)==architecture.SLF_SHA,'unchanged qualified architecture tool/dependencies')
    classes=SLOT/'tool-classes';classes.mkdir(exist_ok=True)
    receipt,_=step('audit-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(receipt['actualExit']==0,'static helper compile zero')
    receipt,text=step('audit-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
      'ModuleDependencyAudit',*[m+'='+str(jars[m]) for m in architecture.MODULES]])
    result=architecture.parse(text)
    require(receipt['actualExit']==0 and result['physical']==1684 and not result['findings']
            and all(v==0 for v in result['rules'].values()),'all fresh1684/all five rules zero')
    value=dict(actualExit=0,source=raw['source'],timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      command='python3 -B tools/quality/pg7032_monitoring_six_artifact_post.py',toolSha256=host.sha(Path(__file__)),
      compileManifestSha256=host.sha(compile_stage.SLOT/'manifest.safe.json'),
      originalWholeQualification=dict(path=str(qp.relative_to(host.ROOT)),sha256=Q_SHA,source=ORIGINAL,notRelabeledAsCurrentPass=True),
      currentComponentQualification=dict(path=str(cp.relative_to(host.ROOT)),sha256=COMPONENT_SHA,tests=48),
      jars=raw['jars'],physicalClassCount=1684,existingPhysicalClassCount=1669,existingChangedClassCount=0,
      newPhysicalClassCount=15,newExecutableClassCount=14,newMetadataClassCount=1,
      newPhysicalClasses=added,newSourceDelta=source_delta,componentClassHashesEqualFreshProductionJar=True,
      architecture=dict(result=result,receipt=receipt,toolSourceSha256=host.sha(architecture.SOURCE),
                        originalCanaryQualificationSha256=ARCH_SHA,canariesReplayed=False),
      testsExecutedByPost=0,targetsLoadedOrInitialized=False,actualVmActions=0,actualDatabaseActions=0,
      original4222Repeated=False,original44Repeated=False,whole451Accepted=False,
      fullRegressionStillRequiredForFormalAcceptance=True,formalUpdated=False,newAccepted=0,effortPercent=None)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=raw['source'],physical=1684,oldUnchanged=1669,
      newExecutable=14,newMetadata=1,architecture=result['rules'],
      manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
