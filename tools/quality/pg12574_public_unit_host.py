"""Whole13 public Unit text assertions with no Product JARs or directive execution."""
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

SOURCE='2efcd4ac8e1b7681fdba0862f7392bbbba5d3f68'
NORMAL_SHA='fe361f6c8fb14008feb760c5b0437f7fc68777a776eb39ca7febc8ec49a27c1a'
OUT=data.BASE/'PG12574-public-unit-host-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12574-public-unit-host-v1'
PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
COUNTS=dict(ArtemisServiceUnitTest=4,CleanupServiceUnitTest=4,SupplementaryUnitTemplateTest=5)
PUBLIC_NAMES=['artemis.service','schubert-nk-cleanup.service.template','schubert-nk-expiry-cleanup.service.template','schubert-nk-backup.service.template','schubert-nk-bootstrap-admin.service.template','caddy.service.d/schubert-nk-startup-policy.conf','caddy.service.d/schubert-nk-stop-policy.conf']


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12572-public-unit-six-compile-v1/manifest.json',NORMAL_SHA)
    p=data.read_checked(data.BASE/'PG12570-public-unit-plan-v1/manifest.json','5ec7235434a5c8ce0c379da9decc85975dd2db1e7c60a2252e56eb6f121ae9e4')
    assert n['source']==SOURCE and n['actualExit']==n['testsExecuted']==0 and p['actualExit']==0 and p['metadataNegativeVectors']==29
    hashes=n['begin']['inputHashes'];snapshot=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    assert {r['path'] for r in p['sourceChanges']}=={PREFIX+name+'.java' for name in COUNTS} and all(hashes[r['path']]==r['sha256'] for r in p['sourceChanges'])
    assert all(data.sha((data.ROOT/path).read_bytes())==data.sha((snapshot/path).read_bytes())==digest for path,digest in hashes.items())
    tc=data.ROOT.parent/'toolchain';cwd=snapshot/'src/schubert-nk-batch';testdir=cwd/'target/test-classes'
    libraries=[x for x in (cwd/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep) if any('/'+namespace+'/' in x for namespace in ['org/junit','org/apiguardian','org/opentest4j'])]
    launcher=tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    assert data.sha(launcher.read_bytes())=='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    libs=list(dict.fromkeys([*libraries,str(launcher)]));assert libs and not set(libs)&{v['path'] for v in n['jars'].values()}
    assert all(x.startswith(str(tc/'m2/repository')+'/') and x.endswith('.jar') for x in libs)
    deps={x:data.sha(Path(x).read_bytes()) for x in libs};helper=data.ROOT/'tools/quality/architecture/PublicUnitTextJunitLauncher.java';helpertext=helper.read_text()
    assert 'EXPECTED_TESTS = 13;' in helpertext and 'EXPECTED_SUITES = 3;' in helpertext and 'selectPackage(' not in helpertext
    cases=[]
    for name,count in COUNTS.items():
        path=PREFIX+name+'.java';text=(snapshot/path).read_text()
        assert not any(w in text for w in ['@Before','@After','@ExtendWith','@TempDir','@Disabled','java.net.','java.sql.','ProcessBuilder','Runtime.getRuntime','Class.forName','ServiceLoader','System.getenv','setAccessible'])
        assert not re.search(r'^import dev\.codex\.',text,re.M)
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text);assert len(methods)==len(set(methods))==count
        for method in methods:
            binary='dev.codex.schubert.nk.batch.platform.'+name;assert binary+'#'+method in helpertext
            cases.append(dict(className=binary,method=method,path=path,sourceSha256=hashes[path]))
    resources=[]
    for name in PUBLIC_NAMES:
        path='src/deployment/systemd/'+name;f=snapshot/path
        assert f.is_file() and not f.is_symlink() and data.sha(f.read_bytes())==hashes[path]
        row=dict(path=path,sha256=hashes[path],readOnlyText=True)
        if name in PUBLIC_NAMES[3:]:
            out=testdir/'systemd'/name;assert data.sha(out.read_bytes())==hashes[path]
            locations=[str(testdir)]
            for library in libs:
                with zipfile.ZipFile(library) as jar:assert 'systemd/'+name not in jar.namelist()
            row.update(resourcePath='systemd/'+name,classPathDefinition=locations)
        resources.append(row)
    physical={str(x):data.sha(x.read_bytes()) for x in testdir.rglob('*.class')};hh=data.sha(helper.read_bytes())
    os.umask(0o077);SLOT.mkdir();reader=SLOT/'launcher';reader.mkdir();testcwd=SLOT/'test-cwd';testcwd.mkdir();catalog=SLOT/'methods.tsv'
    with catalog.open('x') as f:f.write(''.join(x['className']+'\t'+x['method']+'\n' for x in cases))
    entries=[str(reader),str(testdir),*libs];assert len(entries)==len(set(entries)) and not set(entries)&{v['path'] for v in n['jars'].values()}
    cp=os.pathsep.join(entries);begin=dict(source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,sourceInputHashes=hashes,dependencyHashes=deps,physicalTestFiles=physical,helperPath=str(helper),helperSha256=hh,cases=cases,expectedMethods=13,expectedSuites=3,normalSnapshot=str(snapshot),testCwd=str(testcwd),classpath=cp,classPathEntries=entries,productJarsInExecutionClasspath=[],publicResources=resources,repositoryProperty=str(snapshot),judgement='PT_DEFAULT_PUBLIC_FROZEN_TEXT_ONLY_NO_DIRECTIVE_TARGET_ACCESS')
    data.write(SLOT/'begin.safe.json',begin);steps.SLOT=SLOT
    stages=[steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    actual=[];xmls={};code=stages[0]['actualExit']
    if code==0 and not stages[0]['timedOut']:
        command=[str(tc/'jdk-25.0.4/bin/java'),'-Xmx384m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-Dnk.pt.repository='+str(snapshot),'-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('public-unit-text-jp',command,testcwd,timeout=240))
        for f in (SLOT/'xml').glob('TEST-*.xml'):
            node=ET.parse(f).getroot();xmls[f.name]=data.sha(f.read_bytes());actual.extend(dict(classname=r.get('classname'),name=r.get('name'),nonPass=[x.tag for x in r]) for r in node.findall('testcase'))
        passed=stages[-1]['actualExit']==0 and not stages[-1]['timedOut'] and len(xmls)==3 and len(actual)==13 and Counter((x['classname'],x['name']) for x in actual)==Counter((x['className'],x['method']) for x in cases) and not any(x['nonPass'] for x in actual)
        code=0 if passed else stages[-1]['actualExit'] or 1
    else:code=code or 1
    assert not list(testcwd.iterdir()) and data.sha(helper.read_bytes())==hh
    assert all(data.sha(Path(path).read_bytes())==digest for path,digest in {**deps,**physical}.items())
    assert all(data.sha((snapshot/path).read_bytes())==data.sha((data.ROOT/path).read_bytes())==digest for path,digest in hashes.items())
    verify(invocation);value=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,observedTestExecutions=len(actual),classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()) if (SLOT/'classload-metadata.log').exists() else None,execSha256=None,mainCoverage='NOT_APPLICABLE_CONFIGURATION',oldExecUnion=False,newAccepted=0,whole451Accepted=False,actualSecretCount=None)
    data.write(SLOT/'manifest.safe.json',value);OUT.mkdir();data.write(OUT/'manifest.json',value)
    for f in (SLOT/'xml').glob('*'):
        with (OUT/f.name).open('xb') as stream:stream.write(f.read_bytes())
    print(json.dumps(dict(actualExit=code,observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))));raise SystemExit(code)


if __name__=='__main__':main()
