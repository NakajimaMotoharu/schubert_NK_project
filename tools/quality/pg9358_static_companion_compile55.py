"""Fresh bounded test-source compilation only; processors/plugins/runtime test execution absent."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
TC=ROOT.parent/'toolchain'
NORMAL=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9358-static-companion-compile55-v1'
OUT=BASE/'PG9358-static-companion-compile55-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
ENV={'PATH':str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def tree(directory):
    return {str(path.relative_to(directory)):sha(path.read_bytes()) for path in sorted(directory.rglob('*')) if path.is_file()}
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())

def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    status_manifest=BASE/'PG9344-direct-companion-ast-v1/manifest.json'
    assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(status_manifest.read_bytes())=='6a8bea332ad27bccd567949395166f4cef2334bc9770063c3a7ed0d0f405c5d0'
    normal=json.loads(normal_path.read_bytes());primary=json.loads(status_manifest.read_bytes())
    assert normal['source']==primary['source']==SOURCE and normal['actualExit']==primary['actualExit']==0
    status_file=status_manifest.parent/'source-statuses.json';assert sha(status_file.read_bytes())==primary['statusesSha256']
    selected=[row for row in json.loads(status_file.read_bytes()) if row['status']=='NO_TYPED_TARGET_REFERENCE'];assert len(selected)==55
    hashes=normal['begin']['inputHashes'];snapshot=NORMAL/'snapshot'
    assert all(sha((ROOT/path).read_bytes())==sha((snapshot/path).read_bytes())==value for path,value in hashes.items())
    jars=[];jar_hashes={};main_names=set()
    for role,row in normal['jars'].items():
        path=Path(row['path']);assert sha(path.read_bytes())==row['sha256']
        jars.append(path);jar_hashes[str(path)]=row['sha256']
        with zipfile.ZipFile(path) as archive:
            names={name.removesuffix('.class') for name in archive.namelist() if name.endswith('.class')}
            assert not ((main_names & names)-{'module-info'});main_names.update(names)
    assert len(normal['jars'])==6
    external=set();cp_hashes={};test_directories={};source_roots=[]
    for role in normal['jars']:
        module=snapshot/('src/schubert-nk-'+role)
        cp_file=module/'target/pgpt-test-classpath.txt';cp_hashes[str(cp_file)]=sha(cp_file.read_bytes())
        for item in cp_file.read_text().strip().split(os.pathsep):
            path=Path(item)
            if '/dev/codex/schubert/' not in item and item.startswith(str(TC/'m2/repository')+'/'):
                assert path.is_file() and path.suffix=='.jar';external.add(path)
        test_dir=module/'target/test-classes';assert test_dir.is_dir()
        assert not (test_dir/'META-INF/services/com.sun.source.util.Plugin').exists()
        original=tree(test_dir);test_directories[str(test_dir)]=dict(treeSha256=digest(original),fileCount=len(original))
        collisions={name.removesuffix('.class') for name in original if name.endswith('.class')} & main_names
        assert all(name.endswith('/package-info') for name in collisions)
        source_roots.append(module/'src/test/java')
    inputs=[*jars,*sorted(external)]
    for path in inputs:
        assert path.is_file();jar_hashes[str(path)]=sha(path.read_bytes())
        with zipfile.ZipFile(path) as archive:
            assert 'META-INF/services/com.sun.source.util.Plugin' not in archive.namelist()
    for row in selected:
        main_internal=row['mainPath'].split('/src/main/java/',1)[1].removesuffix('.java')
        assert main_internal in main_names
        assert sha((ROOT/row['path']).read_bytes())==hashes[row['path']]==row['sha256']
        assert sha((ROOT/row['mainPath']).read_bytes())==hashes[row['mainPath']]==row['mainSha256']
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir()
    classpath=os.pathsep.join([*[str(path) for path in inputs],*test_directories])
    command=[str(TC/'jdk-25.0.4/bin/javac'),'-J-Xmx768m','--release','25','-proc:none','-implicit:none','-Xlint:all','-Werror',
      '-cp',classpath,'-sourcepath',os.pathsep.join(str(path) for path in source_roots),'-d',str(classes),
      *[str(ROOT/row['path']) for row in selected]]
    begin=dict(source=SOURCE,invocation=invocation,normalManifestSha256=sha(normal_path.read_bytes()),selected55SourceRows=selected,
      jarHashes=jar_hashes,borrowedFixtureClassDirectories=test_directories,classpathFileHashes=cp_hashes,
      compilerPluginServices=0,annotationProcessing=False,sourcepath=[str(path) for path in source_roots],
      implicitClassEmission=False,environment=ENV,command=command,startUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      targetRuntimeClassLoading=0,targetRuntimeInvocation=0,productTestsExecuted=0,actualVmActions=0,actualDatabaseActions=0)
    write(SLOT/'begin.safe.json',begin)
    with (SLOT/'compile.stdout').open('xb') as stdout,(SLOT/'compile.stderr').open('xb') as stderr:
        child=subprocess.Popen(command,cwd=SLOT,env=ENV,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True)
        write(SLOT/'compile-process.safe.json',dict(pid=child.pid,ownerPid=os.getpid(),command=command,startUTC=begin['startUTC'],cwd=str(SLOT)))
        timed_out=False
        try:code=child.wait(timeout=180)
        except subprocess.TimeoutExpired:timed_out=True;child.kill();code=child.wait(timeout=15)
    terminal=dict(actualExit=code,timedOut=timed_out,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      stdoutSha256=sha((SLOT/'compile.stdout').read_bytes()),stderrSha256=sha((SLOT/'compile.stderr').read_bytes()),rawLogsPublished=False)
    write(SLOT/'compile-exit.safe.json',terminal)
    assert all(sha(Path(path).read_bytes())==value for path,value in jar_hashes.items())
    assert all(digest(tree(Path(path)))==value['treeSha256'] for path,value in test_directories.items())
    assert all(sha((ROOT/path).read_bytes())==sha((snapshot/path).read_bytes())==value for path,value in hashes.items())
    fresh={str(path.relative_to(classes)):sha(path.read_bytes()) for path in sorted(classes.rglob('*.class'))}
    shadow={path.removesuffix('.class') for path in fresh} & main_names
    assert not shadow and (fresh or code!=0)
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=code,source=SOURCE,begin=begin,terminal=terminal,freshClassFiles=fresh,freshClassCount=len(fresh),
      selectedTestSourcesStaticallyCompiled=55 if code==0 else None,productionMainCompiled=0,targetRuntimeClassLoading=0,
      targetRuntimeInvocation=0,productTestsExecuted=0,actualNativeActions=0,coverage=None,newTestIds=0,newMain=0,
      formalUpdated=False,newAccepted=0,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None)
    write(SLOT/'manifest.safe.json',value);write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=code,staticSources=55,freshClasses=len(fresh),productTestsExecuted=0,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)

if __name__=='__main__':main()
