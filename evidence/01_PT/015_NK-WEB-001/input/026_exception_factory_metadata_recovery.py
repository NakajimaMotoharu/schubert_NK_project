"""BUG2422: recover the one original Unit result; passive reports only, never rerun the Test."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as E
import pg9666_pagination_static as capture

R = Path(__file__).resolve().parents[4]
RUNS = R.parent/'pgpt-runs/PG379'
U = RUNS/'pg22220-exception-filter-factory-four-unit-v1'
O = RUNS/'pg22224-exception-factory-metadata-recovery-v1'
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p:json.loads(p.read_bytes())


def main():
    assert not O.exists()
    b = load(U/'begin.json')
    assert b['source'] == 'aa101fb7c3c8b53d5218ca6dd3bd8db2973eb493'
    assert b['normalSource'] == '7aed8eace7c844c2f79f2e39db766faf914890d5'
    terminal = load(U/'unit-exit.safe.json')
    assert terminal['actualExit'] == 0 and not terminal['timedOut']
    assert sha(U/'unit.stdout') == terminal['stdoutSha256'] and sha(U/'unit.stderr') == terminal['stderrSha256']
    before = {p.name:sha(p) for p in U.iterdir() if p.is_file()}
    normal_path = RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json'
    assert sha(normal_path) == b['normalManifestSha256'] == 'b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
    normal = load(normal_path)
    target = 'dev/codex/schubert/nk/web/security/WebAccessExceptionFilterFactory'
    O.mkdir()
    capture.SLOT = O
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        assert {n for n in jar.namelist() if n == target+'.class' or n.startswith(target+'$')} == {target+'.class'}
        p = O/'component'/(target+'.class')
        p.parent.mkdir(parents=True)
        p.write_bytes(jar.read(target+'.class'))
    java = R.parent/'toolchain/jdk-25.0.4/bin/java'
    cli = R.parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar'
    commands = {
      'coverage':['report',str(U/'jacoco.exec'),'--classfiles',str(O/'component'),'--xml',str(O/'coverage.xml')],
      'classinfo':['classinfo',str(O/'component')],
      'execinfo':['execinfo',str(U/'jacoco.exec')],
      'web-methods':['report',str(U/'jacoco.exec'),'--classfiles',normal['jars']['web']['path'],'--xml',str(O/'all-web-methods.xml')],
    }
    stages = {key:capture.step(key,[str(java),'-jar',str(cli),*args],R) for key,args in commands.items()}
    assert all(v['actualExit'] == 0 and not v['timedOut'] for v in stages.values())
    cases = []
    for path in sorted((U/'xml').glob('TEST-*.xml')):
        for t in E.parse(path).getroot().findall('testcase'):
            assert not t.findall('failure') and not t.findall('error') and not t.findall('skipped')
            cases.append(dict(classname=t.get('classname'),name=t.get('name')))
    assert len(cases) == len({(v['classname'],v['name']) for v in cases}) == 4
    assert {p.name:sha(p) for p in U.iterdir() if p.is_file()} == before
    root = E.parse(O/'coverage.xml').getroot()
    counters = {v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in root.findall('counter')}
    assert 'BRANCH' not in counters and all(v['missed'] == 0 for v in counters.values())
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(),actualExit=0,
                  source=b['source'],productionCoreMain=b['normalSource'],begin=b,
                  originalUnitTerminal=terminal,originalCollectorWrapperExit=1,
                  originalFilesUnmodified=before,normalManifestSha256=sha(normal_path),
                  metadataStages=stages,tests=4,failures=0,errors=0,skipped=0,cases=cases,
                  physical={target:sha(p)},counters=counters,branchStatus='NATURAL_ZERO_BRANCH',branchRatio=None,
                  productTestsReexecuted=0,originalUnitRuns=1,noOldExecUnion=True,
                  recoveryCommand=[sys.executable,'-B',str(Path(__file__).relative_to(R))],
                  scriptSha256=sha(Path(__file__)),formalUpdated=False,newAcceptance=0)
    (O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,originalUnitTests=4,productTestsReexecuted=0,counters=counters)))


if __name__ == '__main__':
    main()
