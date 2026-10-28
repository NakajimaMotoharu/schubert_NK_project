"""Bind unchanged preflight source bytes to new normal build; six SpotBugs PT0, no PMD replay."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE = '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3'
NORMAL_SHA = 'ef0c374ffb76d88402c3a19c70999c9f644bdbdecb0252c747b7f1544521d823'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13136-main-literal-static-v1'
OUT = data.BASE/'PG13136-main-literal-static-v1'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13134-main-literal-six-compile-v1/manifest.json',NORMAL_SHA)
    p = data.read_checked(data.BASE/'PG13132-main-literal-preflight-v1/manifest.json','4367bdd95cd9f8f503855250edb1b9104ad2bd2edf146018912596973ed8f9c0')
    assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(n['begin']['inputHashes'][path] == sha == data.sha((data.ROOT/path).read_bytes()) for path,sha in p['candidateSourceHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert p['rawStatic'] == 14 and p['rawStaticGateExit'] == 1
    assert all(data.sha((data.BASE/'PG13132-main-literal-preflight-v1'/(name+'.xml')).read_bytes()) == sha for name,sha in p['reports'].items())
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in p['toolAndRuleHashes'].items())
    deps = {item['path']:item['sha256'] for item in n['jars'].values()}
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in deps.items())
    snapshot = Path(n['jars']['api']['path']).parents[3]
    SLOT.mkdir();runner.SLOT = SLOT;mvn = runner.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    stage = runner.step('spotbugs-six',[str(mvn),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(runner.TC/'m2/repository'),'-pl',','.join('src/schubert-nk-'+r for r in ['protocol','storage','bootstrap','api','web','batch']),'-am','-DskipTests=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],snapshot,timeout=600)
    assert stage['actualExit'] == 0 and not stage['timedOut']
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in deps.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes=p['candidateSourceHashes'],normalManifestSha256=NORMAL_SHA,
        preflightManifestSha256='4367bdd95cd9f8f503855250edb1b9104ad2bd2edf146018912596973ed8f9c0',
        sourceHashRebindingOnly=True,pmdCheckstyleReexecuted=False,rawStatic=14,rawStaticGateExit=1,
        spotbugsSixExit=0,stages=[stage],jarsUnchanged=deps,productTestsExecuted=0,coverage=None,
        dynamicPtStatus='NOT_EXECUTED_HOLD',suppressionsAdded=False,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
