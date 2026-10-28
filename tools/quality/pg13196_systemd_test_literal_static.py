"""Rebind exact Test preflight and check six current normal Main artifacts with SpotBugs, PT0."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE = '41359340de234b8bea7578d957bcbf4df6ab951f'
NORMAL_SHA = '6c6809515a4ae056dad337e44b5ffd8e26b617e0292e88df7082b3ddcddea1b9'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13196-systemd-test-literal-static-v1'
OUT = data.BASE/'PG13196-systemd-test-literal-static-v1'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13194-systemd-test-literal-six-compile-v1/manifest.json',NORMAL_SHA)
    p = data.read_checked(data.BASE/'PG13192-systemd-test-literal-preflight-v1/manifest.json','1a7db1f6a6db5b41a8c61119b98825cd1cce173fa6eab50c050f91557e6066f1')
    assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert p['rawStatic'] == 19 and p['rawStaticGateExit'] == 1 and len(p['removedFindingIds']) == 21
    assert all(n['begin']['inputHashes'][path] == sha == data.sha((data.ROOT/path).read_bytes()) for path,sha in p['candidateSourceHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert all(data.sha((data.BASE/'PG13192-systemd-test-literal-preflight-v1'/(name+'.xml')).read_bytes()) == sha for name,sha in p['reports'].items())
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in {**p['toolAndRuleHashes'],**p['dependencyHashes']}.items())
    jars = {item['path']:item['sha256'] for item in n['jars'].values()};assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in jars.items())
    snapshot = Path(n['jars']['bootstrap']['path']).parents[3];SLOT.mkdir();runner.SLOT = SLOT
    mvn = runner.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    stage = runner.step('spotbugs-six',[str(mvn),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(runner.TC/'m2/repository'),'-pl',','.join('src/schubert-nk-'+r for r in ['protocol','storage','bootstrap','api','web','batch']),'-am','-DskipTests=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],snapshot,timeout=600)
    assert stage['actualExit'] == 0 and not stage['timedOut']
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in jars.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sourceHashes=p['candidateSourceHashes'],normalManifestSha256=NORMAL_SHA,
        preflightManifestSha256='1a7db1f6a6db5b41a8c61119b98825cd1cce173fa6eab50c050f91557e6066f1',sourceHashRebindingOnly=True,pmdCheckstyleReexecuted=False,
        rawStatic=19,rawStaticGateExit=1,spotbugsSixExit=0,stages=[stage],jarsUnchanged=jars,productTestsExecuted=0,coverage=None,
        dynamicPtStatus='NOT_EXECUTED_HOLD',suppressionsAdded=False,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
