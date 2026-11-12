"""BUG2712: finite lifetime for the two owned ordinary crypto Test pools, assertion inverse checked."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=R/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/revocation/RevocationPayloadCodecTest.java';sha=lambda b:hashlib.sha256(b).hexdigest();old=p.read_text();assert old.encode()==subprocess.check_output(['git','show','334c66d8e1a5955392e7797ed90603dbc81de0b7:'+str(p.relative_to(R))]);changes=[]
def change(before,after):
 global old
 assert old.count(before)==1;changes.append(dict(before=before,after=after));old=old.replace(before,after)
change('    try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {','    var pool = Executors.newVirtualThreadPerTaskExecutor();\n    try {')
change('    } finally {\n      codec.close();\n      codec.close();','    } finally {\n      pool.shutdownNow();\n      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {\n        throw new AssertionError("PUBLIC crypto worker termination unconfirmed");\n      }\n      codec.close();\n      codec.close();')
change('    try (var pool = Executors.newFixedThreadPool(2)) {','    var pool = Executors.newFixedThreadPool(2);\n    try {')
change('    } finally {\n      release.countDown();\n      codec.close();','    } finally {\n      release.countDown();\n      pool.shutdownNow();\n      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {\n        throw new AssertionError("PUBLIC crypto worker termination unconfirmed");\n      }\n      codec.close();')
p.write_text(old);inverse=old
for row in reversed(changes):assert inverse.count(row['after'])==1;inverse=inverse.replace(row['after'],row['before'])
assert inverse.encode()==subprocess.check_output(['git','show','334c66d8e1a5955392e7797ed90603dbc81de0b7:'+str(p.relative_to(R))]);O=B/'evidence/PG27534-revocation-crypto-finite-source-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,path=str(p.relative_to(R)),oldSha256=sha(inverse.encode()),newSha256=sha(p.read_bytes()),changes=changes,originalAllAssertionsInverseExact=True,ownedPools=2,productTestsExecuted=0,bug='BUG-2712');(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,oldSha256=v['oldSha256'],newSha256=v['newSha256'])))
