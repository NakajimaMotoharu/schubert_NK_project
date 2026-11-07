"""Read pinned public diagnostics and current storage Test source hashes only, never execute a Test."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def checked(ref):
 n=ref['path'];assert n.startswith('evidence/') and '..' not in Path(n).parts and not Path(n).is_absolute();p=R/n;assert sha(p)==ref['sha256'];return load(p)
def current():
 p=B/'evidence/PG22834-storage-mode20-independent-v1/manifest.json';assert sha(p)=='56197f0b963ab9b9c2889c8eb1db87cef0b2a58bdce482fb5565bc46edacc0c1';mode=load(p);style=checked(mode['currentStorage29']['previousBinding']);raw=checked(style['rawOriginalManifest']);assert raw['actualExit']==style['actualExit']==mode['actualExit']==0
 items=[v for v in raw['reports']['pmd']['rawItems'] if v['path'] not in style['currentHashes']]+[v['current'] for v in style['currentStorage29']['retainedSourceRebindings']];assert len(items)==122;changed={v['path'] for v in mode['currentStorage29']['correctedSites']};assert len(changed)==8;items=[v for v in items if v['path'] not in changed]+[v['current'] for v in mode['currentStorage29']['retainedSourceRebindings']];assert len(items)==102
 hashes=mode['currentStorage29']['currentInputHashes'];assert len(hashes)==29
 for n,h in hashes.items():
  assert n.startswith('src/schubert-nk-storage/src/test/java/') and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/n)==h
 keys=[(v['path'],v['rule'],v['beginline'],v['begincolumn'],v['endline'],v['endcolumn']) for v in items];assert len(set(keys))==102
 return dict(path=str(p.relative_to(R)),sha256=sha(p)),items,hashes
