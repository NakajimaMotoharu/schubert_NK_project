"""Immutable public inputs for old normal-host class provenance, never target/private data."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as common

ROOT=common.ROOT;BASE=common.BASE;SOURCE=common.SOURCE
ARTIFACT_SOURCE='e196d0816c8a4920696d4f601f8b4cf97e9e8b48'
NORMAL=ROOT.parent/'pgpt-runs/PG379/pg8122-web-pool-six-compile-v1/snapshot'
NORMAL_SHA='75ca9dd88ce045dc0acdbdd878e9382a30584a1da34fb8d37bc04d2ca4d4a53b'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1940_G07OldHostDigest_公開artifact根拠仕様.md'
SPEC_SHA='a1e9309a96fa90ad8afd5a41e174004b7c2c21287fb02cd3cff3124c7be1eb31'

def inputs():
    assert common.sha(SPEC.read_bytes())==SPEC_SHA
    v=common.inputs()
    prior=common.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/manifest.json',
      '458970306a06b661c558c67f25b5769308fffb91d2c7d8603f996084a70de2ff')
    post=common.read_checked(BASE/'PG9566-g07-host-main-class-provenance-post-v1/manifest.json',
      '8ad5591f0f152f44a9efb0e87a38d3eb8a6c844a7dadb3ecb50934c0747a929b')
    assert post['actualExit']==prior['actualExit']==0 and prior['remainingUnclassified']==post['remainingUnclassified']==4550
    updates=common.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/updates.json',prior['updatesSha256'])
    registry=common.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/public-main-class-proofs.json',prior['publicClassProofsSha256'])
    done=Counter(map(common.key,updates));remaining=[]
    for row in v['pending']:
        k=common.key(row)
        if done[k]:done[k]-=1
        else:remaining.append(row)
    assert len(remaining)==4550 and sum(done.values())==0
    for row in registry:v['oldProofs'].setdefault(row['sha256'],row)
    normal=common.read_checked(BASE/'PG8122-web-pool-six-compile-v1/manifest.json',NORMAL_SHA)
    assert normal['actualExit']==0 and normal['source']==normal['begin']['source']==ARTIFACT_SOURCE
    hashes={p:h for p,h in normal['begin']['inputHashes'].items() if '/src/main/java/' in p and p.endswith('.java')}
    assert len(hashes)==922 and set(normal['jars'])=={'api','batch','bootstrap','protocol','storage','web'}
    v.update(pending=remaining,normal=normal,sourceHashes=hashes)
    return v

def jar(module,entry):
    path=Path(entry['path'])
    assert path.resolve()==path and not path.is_symlink() and path.is_file() and path.suffix=='.jar'
    assert path.parent==NORMAL/('src/schubert-nk-'+module)/'target'
    assert common.sha(path.read_bytes())==entry['sha256']
    return path
