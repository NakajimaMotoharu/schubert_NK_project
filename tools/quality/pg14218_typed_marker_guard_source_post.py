"""Independent new-source compile/source/binary post; never execute Product or old PT."""
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PIN='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
OUT=data.BASE/'PG14218-typed-marker-guard-source-post-v1'

def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    new=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',PIN)
    old=data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    proof=data.read_checked(data.BASE/'PG14210-typed-marker-guard-after-v1/manifest.json','48f245609e4cb19b754fbcd12a0e92435de5c122c6356269fd1e144483bc18ee')
    assert new['source']==SOURCE and new['actualExit']==new['testsExecuted']==new['terminal']['actualExit']==0
    assert old['source']==proof['baselineSource']=='0061d178cda80c2ce3926290619c64db125dbcfc'
    assert proof['staticConformance'] is True and proof['typedSiteCount']==22 and proof['metadataNegativeVectors']==16
    a=old['begin']['inputHashes'];b=new['begin']['inputHashes']
    assert a.keys()==b.keys()
    changed={p for p in b if a[p]!=b[p]}
    assert changed==set(proof['changedProductionPaths']) and len(changed)==3
    snapshot=Path(next(iter(new['jars'].values()))['path']).parents[3]
    # Exact known six-compile location, no unrelated snapshots or runtime paths.
    expected=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    assert snapshot==expected and data.sha((expected.parent/'manifest.safe.json').read_bytes())==PIN
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in b.items())
    assert all(b[p]==h for p,h in proof['observedHashes'].items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT)==b''
    assert new['begin']['source']==SOURCE and '-DskipTests=true' in new['begin']['command']
    assert not list(snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'))
    x,y=jar_classes(old),jar_classes(new)
    assert x.keys()==y.keys() and len(y)==1843
    closure=set()
    for p in changed:
        stem=p.split('/src/main/java/')[1][:-5]
        closure.update(k for k in y if k[0]=='api' and (k[1]==stem+'.class' or k[1].startswith(stem+'$')))
        assert ('api',stem+'.class') in {k for k in y if x[k]!=y[k]}
    diff={k for k in y if x[k]!=y[k]}
    assert diff and diff<=closure
    old_tests,new_tests=test_classes(old),test_classes(new)
    assert old_tests==new_tests and len(new_tests)==1978
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=PIN,baselineSource=old['source'],guardProofSha256='48f245609e4cb19b754fbcd12a0e92435de5c122c6356269fd1e144483bc18ee',candidateSourceHashes=proof['observedHashes'],changedInputPaths=sorted(changed),mainPhysical=1843,testPhysical=1978,allTestBytesUnchanged=True,changedMainPhysical=sorted(diff),allowedSourceClosure=sorted(closure),otherMainBytesUnchanged=1843-len(diff),rawStatic=None,rawStaticGateExit=None,pmdCheckstyleCurrentSource='NOT_YET_MEASURED',productTestsExecuted=0,coverage=None,oldProductResultTransferred=False,dynamicPtStatus='HOLD_NOT_EXECUTED',newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
