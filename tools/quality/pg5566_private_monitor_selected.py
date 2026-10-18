"""Frozen caller-monitor red/green, all affected owners; no VM/full replay."""
import argparse
import hashlib
import json
import os
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pg5540_snapshot_scratch_selected import ROOT,TC,DEPENDENCIES,sha,utc,test_names

BASE='a19a9f7d940b4f9fba47e51bd9be675f4420401b'
OWNERS={
 'dev.codex.schubert.nk.batch.platform.BackupUnitStartClientTest':('batch',17),
 'dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClientTest':('batch',13),
 'dev.codex.schubert.nk.bootstrap.ServiceStartupAdmissionTest':('bootstrap',12),
 'dev.codex.schubert.nk.web.bootstrap.WebProcessLifetimeTest':('web',4)}
WEB='dev.codex.schubert.nk.web.bootstrap.WebProcessLifetimeTest'
CODEC='dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodecTest'
EXPECTED_CHANGES={
 'batch:dev/codex/schubert/nk/batch/platform/BackupUnitStartClient.class',
 'batch:dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Attempt.class',
 'batch:dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient.class',
 'batch:dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient$Attempt.class',
 'bootstrap:dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$ReadyOnce.class',
 'web:dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime.class'}


def physical_delta(prior,physical,phase):
    if set(prior)!=set(physical):raise ValueError('no missing/added physical Main allowed')
    changed={k for k in prior if prior[k]!=physical[k]}
    allowed={k for k in prior if any(k==owner+'.class'or k.startswith(owner+'$')for owner in(
        'batch:dev/codex/schubert/nk/batch/platform/BackupUnitStartClient',
        'batch:dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient',
        'bootstrap:dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission',
        'web:dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime'))}
    # Added lock/body lines also shift sibling nested-class LineNumberTable. Retain every raw
    # physical difference, and require independent debug-only qualification, never ignore it.
    okay=changed==set()if phase=='red'else EXPECTED_CHANGES<=changed<=allowed
    return changed,okay,sorted(changed-EXPECTED_CHANGES)


def inventory(snapshot,phase):
    specs={**DEPENDENCIES,CODEC:('api',7),**(OWNERS if phase=='green'else{WEB:OWNERS[WEB]})};expected={}
    for name,(module,count)in specs.items():
        path=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java')
        names=test_names(path)
        if len(names)!=count:raise ValueError('all declared independent owner/dependency cases '+name)
        expected[name]=names
    if sum(map(len,expected.values()))!=(71 if phase=='green'else 29):raise ValueError('exact selected scope required')
    return expected


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','green'));args=parser.parse_args()
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed input first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    reference=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5550-current3900-cases/qualification.json'
    if sha(reference)!='5914b32a415f39e6a17147bee326a619995f31fe1383f54282242c3c13b356be':raise ValueError('immutable original qualified a19 reference')
    before=json.loads(reference.read_bytes())
    if(before['productionSource'],before['tests'],before['mainClasses'])!=(BASE,3900,1664):raise ValueError('actual base source, never old296 native')
    os.umask(0o077);out=ROOT.parent/'pgpt-runs/PG379'/('pg5566-private-monitor-'+args.phase+'-v1');out.mkdir(mode=0o700)
    archive=out/'source.tar'
    with archive.open('xb')as f:subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
    snapshot=out/'source';snapshot.mkdir(mode=0o700)
    with tarfile.open(archive)as f:f.extractall(snapshot,filter='data')
    expected=inventory(snapshot,args.phase);built=('protocol','storage','bootstrap','api','web')+ (('batch',)if args.phase=='green'else())
    base=[str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-B','-o','-ntp','-Dmaven.repo.local='+str(TC/'m2/repository')]
    commands=[base+['-pl',','.join('src/schubert-nk-'+m for m in('protocol','storage','bootstrap','api','web','batch')),'spotless:check'],
        base+['-pl',','.join('src/schubert-nk-'+m for m in built),'-Dtest='+','.join(expected),'-Dsurefire.failIfNoSpecifiedTests=false',
            'package','org.jacoco:jacoco-maven-plugin:0.8.15:report','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]
    inputs={str(p.relative_to(snapshot)):sha(p)for p in snapshot.rglob('*')if p.is_file()}
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'),PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'],MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out))
    started=utc();phases=[]
    with(out/'start.safe.json').open('x')as f:json.dump({'sourceSnapshot':head,'branch':branch,'baseProductionSource':BASE,'phase':args.phase,'startedUTC':started,'commands':commands,'archiveSha256':sha(archive),'replayAllowed':False},f,sort_keys=True)
    for index,command in enumerate(commands,1):
        with(out/f'phase-{index}.private.log').open('xb')as log:
            child=subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=log,umask=0o027);proc=__import__('pathlib').Path('/proc')/str(child.pid)
            with(out/f'phase-{index}.owner.safe.json').open('x')as f:json.dump({'pid':child.pid,'ticks':int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()},f,sort_keys=True)
            code=child.wait();log.flush();os.fsync(log.fileno())
        phases.append(code)
        if code:break
    actual={};failed=[];errors=[];skipped=[];xmls={};expected_failure=False;static={};coverage={}
    for module in built:
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for path in(target/'surefire-reports').glob('TEST-*.xml'):
            tree=ET.parse(path).getroot();name=tree.get('name');xmls[name]=sha(path)
            if name in actual:raise ValueError('duplicate selected suite')
            actual[name]=set()
            for case in tree.findall('testcase'):
                method=case.get('name','').removesuffix('()')
                if method in actual[name]:raise ValueError('duplicate physical case')
                actual[name].add(method)
                for kind,rows in(('failure',failed),('error',errors),('skipped',skipped)):
                    if case.find(kind)is not None:rows.append([name,method])
                failure=case.find('failure')
                if failure is not None and name==WEB and method=='monitor004CallerLockCannotBlockConfirmedLifetimeClose':
                    expected_failure=failure.get('type')=='org.opentest4j.AssertionFailedError'and failure.get('message','').startswith('caller monitor must not control private owner state ==> expected: <true> but was: <false>')
                if any(n.tag in('flakyFailure','flakyError','rerunFailure','rerunError')for n in case.iter()):errors.append([name,method,'flaky/rerun'])
        report=target/'spotbugsXml.xml'
        if report.exists():static[module]=len(ET.parse(report).getroot().findall('BugInstance'))
        report=target/'site/jacoco/jacoco.xml'
        if report.exists():coverage[module]={c.get('name'):{v.get('type'):{'covered':int(v.get('covered')),'missed':int(v.get('missed'))}for v in c.findall('counter')}for c in ET.parse(report).getroot().findall('package/class')if module+':'+c.get('name')+'.class'in EXPECTED_CHANGES}
    physical={m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix():sha(p)for m in built for p in(snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    prior={k:v for k,v in before['allPhysicalMainSha256'].items()if k.split(':',1)[0]in built}
    changed,physical_ok,debug_pending=physical_delta(prior,physical,args.phase)
    fixed=all(sha(snapshot/name)==digest for name,digest in inputs.items())and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head and not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    red=fixed and physical_ok and actual==expected and phases==[0,1]and not errors and not skipped and failed==[[WEB,'monitor004CallerLockCannotBlockConfirmedLifetimeClose']]and expected_failure
    green=fixed and physical_ok and actual==expected and phases==[0,0]and not failed and not errors and not skipped and set(static)==set(built)and not any(static.values())
    value={'actualExit':next((v for v in phases if v),0),'sourceSnapshot':head,'branch':branch,'baseProductionSource':BASE,'phase':args.phase,'startedUTC':started,'completedUTC':utc(),
        'phaseExits':phases,'sourceFixed':fixed,'expectedCases':sum(map(len,expected.values())),'actualCases':sum(map(len,actual.values())),'suites':len(actual),
        'exactSelectedInventory':actual==expected,'failed':failed,'errors':errors,'skipped':skipped,'purposefulRedEstablished':red,'greenSelectedQualified':green,
        'staticBuiltModules':static,'targetCounters':coverage,'physicalMain':{'count':len(physical),'changed':sorted(changed),'declaredSourceDeltaQualified':physical_ok,
            'requiredCodeChangedClasses':sorted(EXPECTED_CHANGES)if args.phase=='green'else[],
            'additionalPhysicalClassesPendingDebugQualification':debug_pending,'sha256':physical},
        'xmlHashes':xmls,'commands':commands,'archiveSha256':sha(archive),'formalAccepted':False,'coverageWholeAccepted':False,'vmActions':0,'oldNativeImported':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in('physicalMain','commands','xmlHashes','targetCounters')},sort_keys=True))
    return value['actualExit']or(0 if red or green else 1)


if __name__=='__main__':raise SystemExit(main())
