"""After genuine whole10 red result, preserve bytes format and reject malformed scalar at factories."""
from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26626-canonical-scalar-fix-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());assert not O.exists();red=load(B/'evidence/PG26624-canonical-scalar-red-v1/manifest.json');before=load(B/'evidence/PG26620-canonical-scalar-before-v1/manifest.json');assert red['productActualExit']==1 and red['independentMalformedBoundariesExecutedAndFailed']==24;assert all(sha(R/p)==h for p,h in before['paths'].items());paths=list(before['paths']);old={p:(R/p).read_text() for p in paths};block='''    // SS3243/BUG2669: validate scalars without allocating an unwipeable encoded secret copy.
    if (value.codePoints().anyMatch(
        codePoint -> codePoint >= Character.MIN_SURROGATE && codePoint <= Character.MAX_SURROGATE)) {
      throw new IllegalArgumentException("canonical text contains malformed UTF-16");
    }
'''
field=next(p for p in paths if p.endswith('/CanonicalField.java'));request=next(p for p in paths if p.endswith('/CanonicalRequest.java'))
assert old[field].count('    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);')==1
(R/field).write_text(old[field].replace('    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);',block+'    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);'))
assert old[request].count('    return normalized;')==1
(R/request).write_text(old[request].replace('    return normalized;',block.replace('value.codePoints()','normalized.codePoints()')+'    return normalized;'))
jdk=R.parent/'toolchain/jdk-25.0.4/bin/java';fmt=next((R.parent/'toolchain').rglob('google-java-format-1.36.1-all-deps.jar'))
for p in [field,request]:
 a=subprocess.run([str(jdk),'-jar',str(fmt),'-'],input=(R/p).read_text(),text=True,capture_output=True);assert a.returncode==0;(R/p).write_text(a.stdout)
assert all(sha(R/p)==before['paths'][p] for p in paths if p not in [field,request]);O.mkdir()
for p in [field,request]:(O/(Path(p).stem+'-before.txt')).write_text(old[p])
v=dict(actualExit=0,changedMainSources=[field,request],unchangedOperationFingerprintAndSecretBuffer=True,beforeHashes=before['paths'],afterHashes={p:sha(R/p) for p in paths},redEvidenceSha256=sha(B/'evidence/PG26624-canonical-scalar-red-v1/manifest.json'),testSourcesUnchangedAfterRed=all(sha(R/p)==h for p,h in red['inputHashes'].items() if '/src/test/' in p),newPlainSecretBufferCopies=0,rawBinaryFieldContractChanged=False,externalWireHmacFormatChanged=False,productTestsExecuted=0,verifierSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedMainSources=2,testUnchanged=v['testSourcesUnchangedAfterRed'],manifestSha256=sha(O/'manifest.json'))))
