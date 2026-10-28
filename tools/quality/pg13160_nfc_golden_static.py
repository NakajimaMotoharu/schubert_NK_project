"""Rebind exact preflight static source bytes, then current six SpotBugs, no Product PT replay."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE = 'b11fe71bd20e244dd10c83bd339f8345a0c1f085'
NORMAL_SHA = '4c1f5352b5d048cda761851d3482fd74983b3ec885ed839d91f987bca60be0d9'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13160-nfc-golden-static-v1'
OUT = data.BASE/'PG13160-nfc-golden-static-v1'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13156-nfc-golden-six-compile-v1/manifest.json',NORMAL_SHA)
    p = data.read_checked(data.BASE/'PG13152-nfc-golden-preflight-v1/manifest.json','c7a2ac738655f537cc227ee88b16d89e163ef618c6698ba03ac0d5487f25c34e')
    assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert len(p['candidateSourceHashes']) == 5 and all(n['begin']['inputHashes'][path] == sha == data.sha((data.ROOT/path).read_bytes()) for path,sha in p['candidateSourceHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert all(row['findings'] == row['processingErrors'] == 0 for row in p['reports'].values())
    assert all(data.sha((data.BASE/'PG13152-nfc-golden-preflight-v1'/(name+'.xml')).read_bytes()) == row['sha256'] for name,row in p['reports'].items())
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in p['toolAndRuleHashes'].items())
    jars = {item['path']:item['sha256'] for item in n['jars'].values()};assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in jars.items())
    snapshot = Path(n['jars']['protocol']['path']).parents[3];SLOT.mkdir();runner.SLOT = SLOT
    mvn = runner.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    stage = runner.step('spotbugs-six',[str(mvn),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(runner.TC/'m2/repository'),'-pl',','.join('src/schubert-nk-'+r for r in ['protocol','storage','bootstrap','api','web','batch']),'-am','-DskipTests=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],snapshot,timeout=600)
    assert stage['actualExit'] == 0 and not stage['timedOut']
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in jars.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes=p['candidateSourceHashes'],normalManifestSha256=NORMAL_SHA,
        preflightManifestSha256='c7a2ac738655f537cc227ee88b16d89e163ef618c6698ba03ac0d5487f25c34e',
        sourceHashRebindingOnly=True,pmdCheckstyleReexecuted=False,rawStatic=0,staticGateExit=0,
        spotbugsSixExit=0,stages=[stage],jarsUnchanged=jars,productTestsExecuted=0,coverage=None,
        suppressionsAdded=False,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
