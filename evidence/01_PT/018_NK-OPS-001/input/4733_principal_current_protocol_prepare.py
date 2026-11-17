"""Bind current Protocol175 already compiled by originalRoot477; no source compilation or runtime."""
from pathlib import Path
import hashlib,json,zipfile,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=b/'evidence/PG37428-inventory-four-main-compile-v1/manifest.json';j=json.loads(p.read_text());assert j['actualExit']==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={n:h for n,h in j['inputHashes'].items() if n.startswith('src/schubert-nk-protocol/') or n=='pom.xml'};assert all(sha(r/n)==h for n,h in inputs.items());classes=j['physicalClassHashes']['protocol'];assert len(classes)==175 and not any(any(x in n for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']) for n in classes)
root=Path(j['cwd'])/'src/schubert-nk-protocol/target/classes';assert all(sha(root/n)==h for n,h in classes.items());work=r.parent/'pgpt-runs/PG379/pg37460-principal-current8-v1';out=b/'evidence/PG37460-principal-current-protocol175-v1';assert not out.exists() and not work.exists();out.mkdir();jar=out/'current-protocol175.jar'
with zipfile.ZipFile(jar,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for n in sorted(classes):
  info=zipfile.ZipInfo(n,(2026,11,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,(root/n).read_bytes())
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=j['sourceCore'],originalRootCompile=dict(path=str(p.relative_to(r)),sha256=sha(p)),jar=dict(path=str(jar),sha256=sha(jar)),inputHashes=inputs,physicalClassHashes=classes,newMainCompile=False,newTestsExecuted=0,heldFourClassfilesReadOrGenerated=0,oldExecUnion=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print('current Protocol175 saved')
