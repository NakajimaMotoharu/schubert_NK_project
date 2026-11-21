"""Qualify two Animation display owners with the configured root compiler and pinned local peers."""

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import subprocess
from tempfile import mkdtemp
import xml.etree.ElementTree as ET
from zipfile import ZipFile

parent = Path(__file__).with_name('5688_music_current_nullaway_delta.py')
spec = importlib.util.spec_from_file_location('root_compiler_receipt_helpers', parent)
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
h, tag, put = shared.h, shared.tag, shared.put
RUN = 'PG41520-f03-animation-display-nullaway-v2'


def main():
    start = h.read(next(h.PLAN.glob('1920_*')))
    source, core = start['values']['source'], start['values']['productionCoreMain']
    q = start['quota']
    age = datetime.now(timezone.utc) - datetime.fromisoformat(q['observedAtUTC'])
    assert q['ordinaryUsageAllowed'] and 0 <= age.total_seconds() <= 120
    assert all(w is None or w['remainingPercent'] > 10 for w in (q['primary'], q['secondary']))
    assert h.git('rev-parse','HEAD').decode().strip() == source
    earlier = h.evidence('41454')
    v = h.read(earlier)
    assert v['productionCoreMain'] == core and v['tests'] == 8
    previous = h.evidence('41504')
    peer = h.read(previous)
    assert peer['core'] == core and peer['compileScopeVerified']
    sources = {p: digest for p, digest in v['sourceInputs'].items() if '/main/java/' in p and
                p.rsplit('/',1)[-1] in ('AnimationListViewModel.java','AnimationMenuViewModel.java')}
    assert len(sources) == 2
    old_workspace = Path(peer['cwd'])
    previous_pom = Path(peer['normalizedTempPom']['path'])
    assert h.pin(previous_pom) == peer['normalizedTempPom']
    assert h.pin(Path('pom.xml'))['sha256'] == peer['rootCompilerSha256']
    for n, digest in peer['dependencies'].items():
        assert h.pin(Path(n))['sha256'] == digest
    held = ('TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException')
    candidate = Path(mkdtemp(prefix='pgpt-f03-anim-view-',dir='/dev/shm'))
    for path,digest in sources.items():
        t = Path(path)
        assert t.read_bytes() == h.git('show',f'{source}:{path}') and h.pin(t)['sha256'] == digest
        assert not any(n.encode() in t.read_bytes() for n in held)
        copy = candidate / 'src/main/java' / path.split('/main/java/',1)[1]
        copy.parent.mkdir(parents=True,exist_ok=True)
        copy.write_bytes(t.read_bytes())
    peers = ('dev/codex/schubert/nk/web/view/TopBarViewModel.class',
             'dev/codex/schubert/nk/web/session/SessionPrincipal.class',
             'dev/codex/schubert/nk/web/session/package-info.class')
    archive = candidate/'shared-display.jar'
    with ZipFile(archive,'x') as jar:
        for rel in peers:
            p = old_workspace/'target/classes'/rel
            assert h.pin(p)['sha256'] == peer['physical'][rel]
            assert not any(k in rel for k in held)
            jar.write(p,rel)
    pom = ET.parse(previous_pom)
    root = pom.getroot()
    root.find(tag('artifactId')).text = 'animation-current-source-scope'
    dep = put(root.find(tag('dependencies')), 'dependency')
    for key,value in (('groupId','dev.codex.schubert.quality.cached'),('artifactId','exact-display-shared'),
                      ('version','1'),('scope','system'),('systemPath',str(archive))):
        put(dep,key,value)
    ET.register_namespace('', shared.NS)
    output_pom = candidate / 'pom.xml'
    pom.write(output_pom, encoding='utf-8', xml_declaration=True)
    assert b'<project ' in output_pom.read_bytes()
    assert ET.parse(output_pom).getroot().findtext(tag('modelVersion')) == '4.0.0'
    old_command = peer['actualCommand']
    assert old_command[-2:] == ['-Dmaven.test.skip=true','compile']
    started = h.now()
    actual_home = h.ROOT.parent/'pgpt-runs/PG379'/RUN
    actual_home.mkdir(mode=0o700)
    pre = dict(source=source,core=core,run=RUN,sources=sources,selectedPeerClasses={k:peer['physical'][k] for k in peers},
               peerArtifact=h.pin(archive),underlyingCompiler=h.pin(previous_pom),priorUnit=h.pin(earlier),classpathBase=h.pin(previous),
               startUTC=started,argv=old_command,cwd=str(candidate))
    h.write(actual_home/'begin.json',pre)
    result = subprocess.run(old_command,cwd=candidate,env={**os.environ,'JAVA_HOME':str(h.JAVA.parent.parent)},
                            capture_output=True,timeout=100)
    for k,data in (('stdout',result.stdout),('stderr',result.stderr)):
        (actual_home/k).write_bytes(data)
    main = candidate/'target/classes'
    compiled = {p.relative_to(main).as_posix():h.pin(p)['sha256'] for p in main.rglob('*.class')}
    expected = {key+'.class' for key in v['counters'] if '/Animation' in key}
    same = {k: compiled[k]==v['compiledClasses'][k] for k in compiled.keys() & expected}
    attempted = result.returncode==0 and set(compiled)==expected and b'BUILD SUCCESS' in result.stdout
    out=h.OPS/RUN
    out.mkdir()
    h.write(out/'manifest.json',dict(**pre,actualExit=result.returncode,completedCompileGate=attempted,
       compilerFlags=['NullAway:ERROR','-Werror','-Xlint:all'],compiled=compiled,unitClassRawByteEquality=same,
       rawCoverageReapplied=False,ordinaryTestsStarted=0,formalAcceptanceId=None,whole451=False,
       stdout=h.pin(actual_home/'stdout'),stderr=h.pin(actual_home/'stderr'),terminalAtUTC=h.now()))
    print('exit',result.returncode,'new Main',len(sources),'physical',len(compiled),'buildVerified',attempted)


if __name__ == '__main__':
    main()
