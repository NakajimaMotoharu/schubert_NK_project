"""Whole20 existing pure public claim Tests, no real authority/native/DB operations."""
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

SOURCE='917f2e755d4912e522b9893e55aa272fd8e80934'
NORMAL_SHA='9444de936bee333dcc73a34419b26213a423a4ef02ea8be5e984d3612b12b629'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12644-run-session-host-v1'
OUT=data.BASE/'PG12644-run-session-host-v1'
COUNTS=dict(InspectorRunEnvironmentTest=4,SessionOperationTokenV2Test=5)


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12642-run-session-six-compile-v1/manifest.json',NORMAL_SHA)
    plan=data.read_checked(data.BASE/'PG12641-run-session-plan-v2/manifest.json','63f14299fff1e3e3ed7c267affe50aaf7e83986cb80923be5af0270f32251ec4')
    assert __import__('subprocess').check_output(['git','rev-parse',n['source']],cwd=data.ROOT,text=True).strip()==SOURCE and n['actualExit']==n['testsExecuted']==0 and plan['metadataNegativeVectors']==13 and plan['totalReferences']==16
    hashes=n['begin']['inputHashes'];snapshot=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==digest for p,digest in hashes.items())
    paths=[r['path'] for r in plan['sourceChanges']];assert len(paths)==2 and all(hashes[r['path']]==r['sha256'] for r in plan['sourceChanges'])
    eligibility_paths=['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/InspectorRunEnvironment.java', 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRun.java', 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionAttributeCodec.java', 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionAttributes.java', 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java', 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionOperationToken.java', 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionAttributeException.java', 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/SavedRequestTarget.java', 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java', 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java', 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/WireEnum.java']
    eligibility={p:hashes[p] for p in eligibility_paths}
    helper=data.ROOT/'tools/quality/architecture/RunSessionJunitLauncher.java';helpertext=helper.read_text()
    assert 'EXPECTED_TESTS = 9;' in helpertext and 'EXPECTED_SUITES = 2;' in helpertext
    assert not any(w in helpertext for w in ['Class.forName','selectPackage(','scanClasspath'])
    cases=[]
    for p in paths:
        text=(snapshot/p).read_text()
        assert not any(w in text for w in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.nio.file','java.net.','java.sql.','ProcessBuilder','System.getenv','System.getProperty','getConnection(','setAccessible','parentsGuard(','ChildStartupContext','LinuxMonotonicClock','RootServiceLauncher','TemporaryInfrastructureException','WebStartupException'])
        assert not re.search(r'(?<![\w$])Files\.|\bServiceConfigFiles\.(?:production|read)\s*\(',text)
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text);assert len(methods)==len(set(methods))==COUNTS[Path(p).stem]
        binary=re.search(r'package ([\w.]+);',text)[1]+'.'+Path(p).stem
        for method in methods:
            assert binary+'#'+method in helpertext;cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    tc=data.ROOT.parent/'toolchain';modules=[snapshot/('src/schubert-nk-'+r) for r in ['batch','web']];testdirs=[m/'target/test-classes' for m in modules]
    libraries=list(dict.fromkeys(x for m in modules for x in (m/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep) if not Path(x).name.endswith('-tests.jar')))
    jars={k:v['path'] for k,v in n['jars'].items()};assert len(jars)==len(set(jars.values()))==6
    launcher=tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    assert data.sha(launcher.read_bytes())=='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    deps={str(p):data.sha(Path(p).read_bytes()) for p in [*jars.values(),*libraries,launcher,agent]}
    physical={str(p):data.sha(p.read_bytes()) for testdir in testdirs for p in testdir.rglob('*.class')};hh=data.sha(helper.read_bytes())
    os.umask(0o077);SLOT.mkdir();testcwd=SLOT/'test-cwd';testcwd.mkdir();reader=SLOT/'launcher';reader.mkdir();catalog=SLOT/'methods.tsv'
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
    cp=os.pathsep.join(entries);begin=dict(source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,sourceInputHashes=hashes,dependencyHashes=deps,physicalTestFiles=physical,helperPath=str(helper),helperSha256=hh,cases=cases,expectedMethods=9,expectedSuites=2,normalSnapshot=str(snapshot),testCwd=str(testcwd),moduleJars=jars,classpath=cp,eligibilityClosureSourceHashes=eligibility,requiredClassDefinitions=definitions,judgement='PT_DEFAULT_TWO_EXISTING_WHOLE_MEMORY_RUN_BYTES_AND_SESSION_JSON_ONLY',heldTestsNotExtracted=True,normalSourceLiteral=n['source'],normalSourceResolved=SOURCE,actualVmRootNativeDatabasePermitted=False)
    data.write(SLOT/'begin.safe.json',begin);steps.SLOT=SLOT
    stages=[steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    actual=[];xmls={};session='PG12644-RUNSESSION-JP';code=stages[0]['actualExit']
    if code==0 and not stages[0]['timedOut']:
        command=[str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,'-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('run-session-jp',command,testcwd,timeout=240))
        for f in (SLOT/'xml').glob('TEST-*.xml'):
            node=ET.parse(f).getroot();xmls[f.name]=data.sha(f.read_bytes());actual.extend(dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in node.findall('testcase'))
        passed=stages[-1]['actualExit']==0 and not stages[-1]['timedOut'] and len(xmls)==2 and len(actual)==9 and Counter((r['classname'],r['name']) for r in actual)==Counter((r['className'],r['method']) for r in cases) and not any(r['nonPass'] for r in actual)
        code=0 if passed else stages[-1]['actualExit'] or 1
    else:code=code or 1
    assert not list(testcwd.iterdir()) and data.sha(helper.read_bytes())==hh
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==digest for p,digest in hashes.items())
    verify(invocation);value=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,sessionId=session,observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()) if (SLOT/'classload-metadata.log').exists() else None,oldExecUnion=False,coveragePendingIndependentPost=True,whole451Accepted=False,newAccepted=0,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value);OUT.mkdir();data.write(OUT/'manifest.json',value)
    for f in (SLOT/'xml').glob('*'):
        with (OUT/f.name).open('xb') as stream:stream.write(f.read_bytes())
    print(json.dumps(dict(actualExit=code,observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))));raise SystemExit(code)


if __name__=='__main__':main()
