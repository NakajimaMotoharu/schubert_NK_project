"""Pinned current29/89 read-only source binding; original native Tests never compiled/invoked."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def current():
 p=B/'evidence/PG22858-storage-if13-independent-v1/manifest.json';assert sha(p)=='3a9cb56a6e67d699f74bfa4da69f19ed16d9b418e101eb617035cd493233403d';m=load(p);assert m['actualExit']==0;c=m['currentStorage29'];h=c['currentInputHashes'];raw=c['allCurrentRaw'];assert len(h)==29 and len(raw)==89 and len(c['reviewedFindings'])==8
 for n,v in h.items():
  assert n.startswith('src/schubert-nk-storage/src/test/java/') and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/n)==v
 key=lambda v:tuple(v[k] for k in ['path','rule','beginline','begincolumn','endline','endcolumn']);assert len(set(map(key,raw)))==89
 return dict(path=str(p.relative_to(R)),sha256=sha(p)),raw,h,c['reviewedFindings']
