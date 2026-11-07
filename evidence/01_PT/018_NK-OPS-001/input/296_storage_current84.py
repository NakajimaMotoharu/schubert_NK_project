"""Pinned current storage29/84 source metadata, no original Test evaluation."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
def current():
 p=B/'evidence/PG22934-storage-four-resource-independent-v2/manifest.json';assert sha(p)=='34d8dd77101d5ba595ab2196f0706317c26b45bc929f92d880142068dcd6964c';m=load(p);assert m['actualExit']==0;c=m['currentStorage29'];assert len(c['currentInputHashes'])==29 and len(c['allCurrentRaw'])==84 and len(c['reviewedFindings'])==27
 for n,h in c['currentInputHashes'].items():assert n.startswith('src/schubert-nk-storage/src/test/java/') and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) and sha(R/n)==h
 return dict(path=str(p.relative_to(R)),sha256=sha(p)),c['allCurrentRaw'],c['currentInputHashes'],c['reviewedFindings']
