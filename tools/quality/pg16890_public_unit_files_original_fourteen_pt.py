"""Four original whole Unit-file suites fourteen: seven public copies, no Production Main jars or services."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SESSION='PG16890-PUBLIC-UNIT-FILES-ORIGINAL-FOURTEEN'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg16890-public-unit-files-original-fourteen-pt-v1'
OUT=data.BASE/'PG16890-public-unit-files-original-fourteen-pt-v1'
PLAN=data.BASE/'PG16889-public-unit-files-fresh-review-binding-v1'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
PACKAGE='dev.codex.schubert.nk.batch.platform.'
COUNTS={'RootServiceUnitTest':2,'ArtemisServiceUnitTest':4,'CleanupServiceUnitTest':4,'MorningServiceUnitTest':4}
PINS={'RootServiceUnitTest':'f327a536753f6dde4e40fba119e71c3c7bc136d1c1f5ffebf2208ecd6dcd99a1','ArtemisServiceUnitTest':'f4d4eef17d290f851464f1aeb4dccf68e8ec12b030cf65817c6c2c5ced7d7172','CleanupServiceUnitTest':'3674f41176365d39b58023774d24ea2d028536ea012991f6d55a16f71c048a1c','MorningServiceUnitTest':'dcde5c5aa5707bbb8fcf52cb2345d7aeece3acc75662420fd5064b6857491dde'}
TESTS={n:data.ROOT/('src/schubert-nk-batch/src/test/java/'+PACKAGE.replace('.','/')+n+'.java') for n in COUNTS}
RESOURCES={n:'src/deployment/systemd/'+n for n in ['schubert-nk-api.service.template','schubert-nk-web.service.template','artemis.service','schubert-nk-cleanup.service.template','schubert-nk-expiry-cleanup.service.template','schubert-nk-morning-controller.service.template','schubert-nk-morning.target.template']}
RUNTIME=('PG16605-application-unit-original-five-pt-v2','c4129cc8f24413764004a2422e0a153bb2341fd43641d4a08dcaa80cca0a0e2f')
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists() and not PLAN.exists(),'new-only, no original replay')
    normal,pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=COMPILE/'snapshot'
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'current compile-only')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'same frozen normal inputs')
    methods={};reviewed={}
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(data.ROOT))
        require(data.sha(path.read_bytes())==hashes[relative]==PINS[name],'original whole Test bytes')
        methods[name]=re.findall(r'@Test\s+void\s+(\w+)\(',text)
        require(len(methods[name])==len(set(methods[name]))==text.count('@Test')==COUNTS[name],'all original whole methods')
        require(not any(t in text for t in ['@Before','@After','@TempDir','ProcessBuilder','DriverManager','Runtime.getRuntime','Class.forName','new Thread','Executors.','Files.write','Files.new','getenv(']),'public string reads/assertions only')
        reviewed[relative]=PINS[name]
    runtime=data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1]);b=runtime['begin']
    external=b['classpathEntries'][1:];deps=b['dependencyHashes'];excluded={row['path'] for row in normal['jars'].values()}
    require(runtime['actualExit']==0 and runtime['source']==SOURCE and len(external)==len(set(external)) and set(external)==set(deps) and not set(external)&excluded and all(p.endswith('.jar') and data.sha(Path(p).read_bytes())==deps[p] for p in external),'qualified external-only runtime, Main jars excluded')
    agent=b['jacocoAgent'];require(data.sha(Path(agent['path']).read_bytes())==agent['sha256'],'fixed separate agent')
    helper=data.ROOT/'tools/quality/architecture/PublicUnitFilesFourteenCurrentJunitLauncher.java';reporter=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    require(proof['actualExit']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(reporter.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','qualified reporter')
    old=data.read_checked(data.BASE/'PG16880-current2454-caddy-readiness-registry-v1/manifest.json','bc6ef9046abb3f7963afc36303c8d61f5f6324de0ed13a6b497f3046744af5df')
    require(not {PACKAGE+n for n in COUNTS}&set(old['suiteNames']),'no already referenced original suite')
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_FOUR_ORIGINAL_WHOLE_UNIT_FILE_SUITES_PUBLIC_COPY_ONLY',reviewedWholeTestInputs=reviewed,reviewedPublicFileInputs={p:hashes[p] for p in RESOURCES.values()},originalWholeSuites=COUNTS,productionMainClasspathEntries=0,actualManagerServiceActions=0,credentialTargetsAccessed=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir();candidate=SLOT/'candidate';testcwd=candidate/'src/schubert-nk-batch';testcwd.mkdir(parents=True);copies={};inputs={}
    for name,path in RESOURCES.items():
        blob=(snapshot/path).read_bytes();require(data.sha(blob)==hashes[path],'exact public template bytes')
        target=candidate/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);copies[str(target)]=hashes[path];inputs[path]=hashes[path]
    entries=[str(classes),*external];cp=os.pathsep.join(entries)
    begin=dict(source=SOURCE,invocation=invocation,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),normalManifestSha256=pin,sourceHashes=hashes,publicResourceInputs=inputs,publicResourceCopies=copies,publicFileDefinitions={p:str(candidate/p) for p in inputs},repositoryProperty=str(candidate),testWorkingDirectory=str(testcwd),classpathDefinitions={},classpathEntries=entries,excludedProductionMainJars=sorted(excluded),dependencyHashes=deps,testSourceHashes={str(p):data.sha(p.read_bytes()) for p in [*TESTS.values(),helper,reporter]},selectedMethods=methods,selectedSuites=COUNTS,runtimeLibraryReference=list(RUNTIME),jacocoAgent=agent,actualManagerServiceActions=0,priorProductResultsTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,staticReviewBindingSha256=data.sha((PLAN/'manifest.json').read_bytes()))
    data.write(SLOT/'begin.safe.json',begin);runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin'
    stages=[runner.step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*map(str,TESTS.values()),str(helper),str(reporter)],SLOT,timeout=180)]
    if stages[0]['actualExit']==0 and not stages[0]['timedOut']:
        stages.append(runner.step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Dnk.pt.repository='+str(candidate),'-javaagent:'+agent['path']+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION,'-cp',cp,helper.stem,str(SLOT/'xml')],testcwd,timeout=180))
    cases=[];xmls={};suites={}
    for path in (SLOT/'xml').glob('TEST-*.xml'):
        root=ET.parse(path).getroot();xmls[path.name]=data.sha(path.read_bytes());suites[root.get('name')]={k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for c in root.findall('testcase'):cases.append(dict(classname=c.get('classname'),name=c.get('name'),result='PASS' if not list(c) else 'NOT_PASS'))
    expected={(PACKAGE+n,m) for n,ms in methods.items() for m in ms}
    passed=len(stages)==2 and all(v['actualExit']==0 and not v['timedOut'] for v in stages) and len(cases)==14 and {(v['classname'],v['name']) for v in cases}==expected and all(v['result']=='PASS' for v in cases) and suites=={PACKAGE+n:dict(tests=c,failures=0,errors=0,skipped=0) for n,c in COUNTS.items()}
    require({str(p.relative_to(candidate)) for p in candidate.rglob('*') if p.is_file()}==set(inputs) and all(data.sha(Path(p).read_bytes())==h for p,h in copies.items()) and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'closed seven copies and all source unchanged')
    own_env={}
    if len(stages)==2:
        with (SLOT/'selected-junit.stdout').open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):k,v=line.strip().split('=',1);require(k not in own_env,'unique original env');own_env[k]=v
        require(len(own_env)==4,'actual own JVM environment')
    verify(invocation);result=dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,tests=len(cases),suites=suites,cases=cases,xmlHashes=xmls,execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,sessionIdentity=SESSION,reportedEnvironment=own_env,sourceChanged=False,newTestIds=0,newAccepted=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,productResultsTransferred=False,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result);OUT.mkdir();data.write(OUT/'manifest.json',result)
    for name in xmls:shutil.copyfile(SLOT/'xml'/name,OUT/name)
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=len(cases),suites=len(suites))));raise SystemExit(result['actualExit'])
if __name__=='__main__':main()
