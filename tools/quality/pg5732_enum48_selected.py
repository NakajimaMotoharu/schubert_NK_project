"""Five finite local enum catalog fixtures; compile/static six modules, no operational entry point."""
import hashlib
import json
import os
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT,TC,sha,utc,test_names

SLOT='pg5732-enum48-selected-v2'
MODULES=('protocol','storage','bootstrap','api','web','batch')
PACKAGE='dev.codex.schubert.nk.'
CASES={
 'protocol':{'protocol.codec.PayloadGoldenVectorTest'},
 'storage':{'storage.EnumValueCatalogCompatibilityTest'},
 'bootstrap':{'api.file.EnumValueCatalogCompatibilityTest'},
 'api':{'api.security.EnumValueCatalogCompatibilityTest'},
 'web':{'web.media.HttpByteRangeParserTest'},
 'batch':{'batch.platform.EnumValueCatalogCompatibilityTest','batch.repository.EnumValueCatalogCompatibilityTest'}}
TARGETS={
 'storage':['storage/ServiceCredentialId'],
 'bootstrap':['api/file/AesCredentialFile','bootstrap/SystemManagerObservation$Service'],
 'api':['api/messaging/config/ArtemisConnectionFactoryProvider$ConsumerProfile','api/messaging/outbound/OutboxDestination','api/security/LoginAttemptKind'],
 'batch':['batch/platform/ApplicationUnit','batch/platform/MaintenanceUnit','batch/platform/BackupUnitStartClient$Target','batch/platform/InspectorUnitSnapshot$Target','batch/platform/RootStartupContext$Service','batch/repository/BatchStep','batch/repository/CleanupKind','batch/repository/MaintenanceCompletion$Outcome']}


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean source first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    os.umask(0o077);out=ROOT.parent/'pgpt-runs/PG379'/SLOT;out.mkdir(mode=0o700)
    archive=out/'source.tar'
    with archive.open('xb')as f:subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization','tools/quality/static'],cwd=ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
    snapshot=out/'source';snapshot.mkdir()
    with tarfile.open(archive)as f:f.extractall(snapshot,filter='data')
    expected={}
    for module,classes in CASES.items():
        for cls in classes:
            name=PACKAGE+cls;path=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java')
            names=test_names(path)
            count=3 if module=='protocol'else 4 if module=='web'else 1
            if len(names)!=count:raise ValueError('explicit independent catalog/dependency cases')
            expected[name]=names
    if set(CASES)!=set(MODULES)or sum(map(len,expected.values()))!=12 or len(expected)!=7:raise ValueError('all six module NoTests guards retained')
    inputs={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.rglob('*')if p.is_file()}
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'),PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'],MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out))
    base=[str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-B','-o','-ntp','-Dmaven.repo.local='+str(TC/'m2/repository'),'-pl',','.join('src/schubert-nk-'+m for m in MODULES)]
    commands=[base+['spotless:check'],base+['-Dtest='+','.join(sorted(expected)),'-Dsurefire.failIfNoSpecifiedTests=false','package','org.jacoco:jacoco-maven-plugin:0.8.15:report','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]
    started=utc()
    with(out/'begin.safe.json').open('x')as f:json.dump({'source':head,'archiveSha256':sha(archive),'startedUTC':started,'commands':commands,'expected':{k:sorted(v)for k,v in expected.items()},'expectedTests':12,'vmActions':0,'replayAllowed':False},f,sort_keys=True)
    exits=[]
    for i,command in enumerate(commands,1):
        with(out/f'phase-{i}.private.log').open('xb')as f:
            p=subprocess.Popen(command,cwd=snapshot,env=env,stdout=f,stderr=f,umask=0o027);proc=Path('/proc')/str(p.pid)
            with(out/f'phase-{i}.owner.safe.json').open('x')as m:json.dump({'pid':p.pid,'ticks':int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()},m,sort_keys=True)
            exits.append(p.wait());f.flush();os.fsync(f.fileno())
        if exits[-1]:break
    actual={};problems=[];xmls={};static={};coverage={};physical={}
    for module in MODULES:
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for path in(target/'surefire-reports').glob('TEST-*.xml'):
            tree=ET.parse(path).getroot();name=tree.get('name')
            if name in actual:raise ValueError('no duplicate suites')
            actual[name]=set();xmls[name]={'module':module,'sha256':sha(path)}
            for case in tree.findall('testcase'):
                method=case.get('name','').removesuffix('()')
                if method in actual[name]:raise ValueError('no duplicate cases')
                actual[name].add(method)
                if any(x.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for x in case.iter()):problems.append([name,method])
        report=target/'spotbugsXml.xml'
        if report.exists():static[module]=len(ET.parse(report).getroot().findall('BugInstance'))
        report=target/'site/jacoco/jacoco.xml'
        if report.exists():coverage[module]={'sha256':sha(report),'classes':{c.get('name'):{k.get('type'):{'covered':int(k.get('covered')),'missed':int(k.get('missed'))}for k in c.findall('counter')}for c in ET.parse(report).getroot().findall('package/class')}}
        physical.update({module+':'+p.relative_to(target/'classes').as_posix():sha(p)for p in(target/'classes').rglob('*.class')})
    fixed=all(sha(snapshot/p)==h for p,h in inputs.items())
    target_counters={}
    for module,classes in TARGETS.items():
        for name in classes:
            counters=coverage.get(module,{}).get('classes',{}).get('dev/codex/schubert/nk/'+name,{})
            target_counters[module+':'+name]={k:counters.get(k,{'covered':0,'missed':0})for k in('LINE','METHOD','CLASS','BRANCH')}
    target100=len(target_counters)==14 and all(all(c[k]['missed']==0 and c[k]['covered']>0 for k in('LINE','METHOD','CLASS'))and c['BRANCH']['missed']==0 for c in target_counters.values())
    done=exits==[0,0]and actual==expected and not problems and fixed and len(physical)==1664 and set(static)==set(MODULES)and not any(static.values())
    done=done and target100
    value={'actualExit':next((v for v in exits if v),0),'source':head,'startedUTC':started,'completedUTC':utc(),'phaseExits':exits,'sourceFixed':fixed,'archiveSha256':sha(archive),'tests':sum(map(len,actual.values())),'suites':len(actual),'exactInventory':actual==expected,'failedOrSkipped':problems,'staticIssues':static,'coverage':coverage,'xmlHashes':xmls,'allPhysicalMainSha256':physical,'targetCounters':target_counters,'targetFour100':target100,'selectedQualified':done,'formalAccepted':False,'fullRegressionPending':True,'fullCoverageClaimed':False,'vmActions':0,'ptAlternativeCompleted':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in('coverage','xmlHashes','allPhysicalMainSha256')},sort_keys=True))
    return 0 if done else 1


if __name__=='__main__':raise SystemExit(main())
