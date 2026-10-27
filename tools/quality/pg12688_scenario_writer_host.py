"""Original whole8 writer/verifier Tests in a new owned TempDir; no existing storage/Root/native/DB."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps
from pg9906_user_query_oracle_source_post import jar_classes

SOURCE='e353b1f49a740a426031fdc199f7ce8b26081971'
NORMAL_SHA='20ef6bfc17fb7fdb9a7cab61c1d927bcb480ec36dffadbd0e5e7fc5c0ed23a9d'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12688-scenario-writer-host-v1'
OUT=data.BASE/'PG12688-scenario-writer-host-v1'
COUNTS=dict(ScenarioRecordStreamTest=5,TransferContentVerifierTest=3)


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12686-scenario-writer-six-compile-v1/manifest.json',NORMAL_SHA)
    plan=data.read_checked(data.BASE/'PG12684-scenario-writer-plan-v1/manifest.json','71ae38137584d347696953a2ae460d1bb825a05a97dd1cbbb37ac794b4f58075')
    assert __import__('subprocess').check_output(['git','rev-parse',n['source']],cwd=data.ROOT,text=True).strip()==SOURCE and n['actualExit']==n['testsExecuted']==0 and plan['metadataNegativeVectors']==16 and plan['typedConditionReferences']==4 and plan['finallyOwnerOnlyChange']
    hashes=n['begin']['inputHashes'];snapshot=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    previous=data.read_checked(data.BASE/'PG12666-transfer-verifier-six-compile-v1/manifest.json','138b454a9eb9d3d00f6ac2579d6f76b36afbc340b745375d53dfa8383bf59e10')
    assert jar_classes(previous)==jar_classes(n) and len(jar_classes(n))==1843
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==digest for p,digest in hashes.items())
    paths=[r['path'] for r in plan['sourceChanges']]+list(plan['companionSourceHashes']);assert len(paths)==2 and len(plan['sourceChanges'])==1 and all(hashes[r['path']]==r['sha256'] for r in plan['sourceChanges']) and all(hashes[p]==h for p,h in plan['companionSourceHashes'].items())
    eligibility=plan['eligibilityClosureSourceHashes'];assert len(eligibility)==56 and all(hashes[p]==h for p,h in eligibility.items())
    helper=data.ROOT/'tools/quality/architecture/ScenarioWriterJunitLauncher.java';helpertext=helper.read_text()
    assert 'EXPECTED_TESTS = 8;' in helpertext and 'EXPECTED_SUITES = 2;' in helpertext
    assert not any(w in helpertext for w in ['Class.forName','selectPackage(','scanClasspath'])
    cases=[]
    for p in paths:
        text=(snapshot/p).read_text()
        assert not any(w in text for w in ['@Before','@After','@ExtendWith','@Disabled','java.net.','java.sql.','ProcessBuilder','System.getenv','System.getProperty','getConnection(','setAccessible','parentsGuard(','ChildStartupContext','LinuxMonotonicClock','RootServiceLauncher','TemporaryInfrastructureException','WebStartupException'])
        assert text.count('@TempDir Path root;')==1
        if Path(p).stem=='TransferContentVerifierTest':
            assert text.count('Files.')==1 and text.count('FileChannel.open(')==1 and text.count('root.resolve(')==1
        else:
            assert text.count('Files.')==3 and text.count('FileChannel.open(')==5 and text.count('root.resolve(')==7
            assert 'Executors.newFixedThreadPool(8)' in text and 'i < 16' in text and 'result.get()' in text
        assert text.count('root.resolve("count-" + count)')==1
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text);assert len(methods)==len(set(methods))==COUNTS[Path(p).stem]
        binary=re.search(r'package ([\w.]+);',text)[1]+'.'+Path(p).stem
        for method in methods:
            assert binary+'#'+method in helpertext;cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    tc=data.ROOT.parent/'toolchain';modules=[snapshot/('src/schubert-nk-'+r) for r in ['api']];testdirs=[m/'target/test-classes' for m in modules]
    libraries=list(dict.fromkeys(x for m in modules for x in (m/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep) if not Path(x).name.endswith('-tests.jar')))
    jars={k:v['path'] for k,v in n['jars'].items()};assert len(jars)==len(set(jars.values()))==6
    launcher=tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    assert data.sha(launcher.read_bytes())=='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    deps={str(p):data.sha(Path(p).read_bytes()) for p in [*jars.values(),*libraries,launcher,agent]}
    physical={str(p):data.sha(p.read_bytes()) for testdir in testdirs for p in testdir.rglob('*.class')};hh=data.sha(helper.read_bytes())
    os.umask(0o077);SLOT.mkdir();testcwd=SLOT/'test-cwd';testcwd.mkdir();temp=SLOT/'owned-java-tmp';temp.mkdir();assert temp.stat().st_mode & 0o777==0o700 and not temp.is_symlink();reader=SLOT/'launcher';reader.mkdir();catalog=SLOT/'methods.tsv'
    temp_identity=dict(device=temp.stat().st_dev,inode=temp.stat().st_ino,mode=temp.stat().st_mode & 0o777)
    with catalog.open('x') as f:f.write(''.join(r['className']+'\t'+r['method']+'\n' for r in cases))
    entries=list(dict.fromkeys(map(str,[reader,*testdirs,*jars.values(),*libraries,launcher])));assert set(jars.values())<=set(entries)
    definitions={}
    for p in [*eligibility,*paths]:
        role=p.split('/')[1].removeprefix('schubert-nk-');target=p.split('/java/',1)[1][:-5]+'.class';locations=[]
        for entry in entries:
            path=Path(entry)
            if path.is_dir():
                if (path/target).is_file():locations.append(entry)
            elif path.suffix=='.jar':
                with zipfile.ZipFile(path) as jar:
                    if target in jar.namelist():locations.append(entry)
        expected_entry=jars[role] if '/src/main/' in p else str(snapshot/('src/schubert-nk-'+role+'/target/test-classes'))
        assert locations==[expected_entry];definitions[target]=locations
    cp=os.pathsep.join(entries);begin=dict(source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,sourceInputHashes=hashes,dependencyHashes=deps,physicalTestFiles=physical,helperPath=str(helper),helperSha256=hh,cases=cases,expectedMethods=8,expectedSuites=2,normalSnapshot=str(snapshot),testCwd=str(testcwd),ownedTempRoot=str(temp),ownedTempCleanupMode='ALWAYS',actualOwnedNewSyntheticFileIoOnly=True,moduleJars=jars,classpath=cp,eligibilityClosureSourceHashes=eligibility,requiredClassDefinitions=definitions,judgement='PT_DEFAULT_TWO_WHOLE_WRITER_VERIFIER_OWNED_TEMP_ONLY_NO_NATIVE',heldTestsNotExtracted=True,normalSourceLiteral=n['source'],normalSourceResolved=SOURCE,actualVmRootNativeDatabasePermitted=False)
    begin['ownedTempRootIdentity']=temp_identity
    data.write(SLOT/'begin.safe.json',begin);steps.SLOT=SLOT
    stages=[steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    actual=[];xmls={};session='PG12688-SCENARIOWRITER-JP';code=stages[0]['actualExit']
    if code==0 and not stages[0]['timedOut']:
        command=[str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Djava.io.tmpdir='+str(temp),'-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,'-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('scenario-writer-jp',command,testcwd,timeout=240))
        for f in (SLOT/'xml').glob('TEST-*.xml'):
            node=ET.parse(f).getroot();xmls[f.name]=data.sha(f.read_bytes());actual.extend(dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in node.findall('testcase'))
        passed=stages[-1]['actualExit']==0 and not stages[-1]['timedOut'] and len(xmls)==2 and len(actual)==8 and Counter((r['classname'],r['name']) for r in actual)==Counter((r['className'],r['method']) for r in cases) and not any(r['nonPass'] for r in actual)
        code=0 if passed else stages[-1]['actualExit'] or 1
    else:code=code or 1
    assert not list(testcwd.iterdir()) and not list(temp.iterdir()) and data.sha(helper.read_bytes())==hh
    assert not temp.is_symlink() and dict(device=temp.stat().st_dev,inode=temp.stat().st_ino,mode=temp.stat().st_mode & 0o777)==temp_identity
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==digest for p,digest in hashes.items())
    verify(invocation);value=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,sessionId=session,observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()) if (SLOT/'classload-metadata.log').exists() else None,oldExecUnion=False,ownedTempRootEmptyAfter=True,coveragePendingIndependentPost=True,whole451Accepted=False,newAccepted=0,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value);OUT.mkdir();data.write(OUT/'manifest.json',value)
    for f in (SLOT/'xml').glob('*'):
        with (OUT/f.name).open('xb') as stream:stream.write(f.read_bytes())
    print(json.dumps(dict(actualExit=code,observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))));raise SystemExit(code)


if __name__=='__main__':main()
