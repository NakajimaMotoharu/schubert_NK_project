"""Pinned current29/88 source metadata only; no original Test evaluation."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
def current():
 p=B/'evidence/PG22904-storage-lock-wait-independent-v1/manifest.json';assert sha(p)=='c3013c52fbb0dd515cfdbb6e991f0117ec4ffbfcf9f770baf12540e704b121a9';m=load(p);assert m['actualExit']==0;c=m['currentStorage29'];assert len(c['currentInputHashes'])==29 and len(c['allCurrentRaw'])==88 and len(c['reviewedFindings'])==23
 for n,h in c['currentInputHashes'].items():assert n.startswith('src/schubert-nk-storage/src/test/java/') and not any(v in n for v in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) and sha(R/n)==h
 return dict(path=str(p.relative_to(R)),sha256=sha(p)),c['allCurrentRaw'],c['currentInputHashes'],c['reviewedFindings']
