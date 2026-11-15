"""Reuse same-group exact Main compile; fresh whole27 Test compile after BUG3019 fixture repair."""
from pathlib import Path
import hashlib,json,shutil
import pgpt_closed_host_profile as policy
import pg9666_pagination_static as capture
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';runs=r.parent/'pgpt-runs/PG379';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
op=b/'evidence/PG33784-ssc420-encrypt27-prepare-v1/manifest.json';old=ld(op);origin=runs/'pg33784-ssc420-encrypt27-v1';work=runs/'pg33785-ssc420-encrypt27-fixed-test-v1';out=b/'evidence/PG33785-ssc420-encrypt27-fixed-prepare-v1';assert not out.exists() and not work.exists()
changed='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogPayloadCodecTest.java';assert all(sha(r/n)==h for n,h in old['inputHashes'].items() if n!=changed)
assert sha(r/changed)!=old['inputHashes'][changed] and old['stages']['nullaway-compile']['actualExit']==0
meta=ld(b/'evidence/PG33786-ssc420-encrypt27-static-v1/BUG3019-original-site.json');text=(r/changed).read_text();start=text.index('    try {\n      EncryptedWebLogPayload encrypted');end=text.index('    } finally {',start);wrapped=text[start+len('    try {\n'):end];inverse='\n'.join(line[2:] for line in wrapped.rstrip('\n').splitlines());assert inverse==meta['oldSegment']
# All names are admitted before the first class payload read/hash/copy.
for n in old['physicalClassHashes']:policy.relative_name(n)
assert {n:sha(origin/'component'/n) for n in old['physicalClassHashes']}==old['physicalClassHashes']
work.mkdir();out.mkdir();(work/'component').mkdir();(work/'target/classes').mkdir(parents=True);(work/'test-classes').mkdir()
for n,h in old['physicalClassHashes'].items():
 dest=work/'component'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/'component'/n,dest);assert sha(dest)==h
for n,h in old['mainClassHashes'].items():
 dest=work/'target/classes'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/'target/classes'/n,dest);assert sha(dest)==h
shutil.copyfile(origin/'pom.xml',work/'pom.xml')
for n in old['apiMainSources']:
 dest=work/'src/main/java'/n.split('/src/main/java/')[1];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/n,dest)
for stream in ['stdout','stderr']:shutil.copyfile(op.parent/('nullaway-compile.'+stream),out/('nullaway-compile.'+stream))
shutil.copyfile(op.parent/'nullaway-compile-exit.safe.json',out/'nullaway-compile-exit.safe.json')
inputs=dict(old['inputHashes']);inputs[changed]=sha(r/changed);capture.SLOT=out;stage=capture.step('test-compile',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(work/'target/classes')+':'+':'.join(old['dependencies']),'-d',str(work/'test-classes'),*[str(r/n) for n in old['apiTestSources']]],r);assert stage['actualExit']==0 and not stage['timedOut']
for path in (work/'test-classes').rglob('*.class'):policy.relative_name(str(path.relative_to(work/'test-classes')))
v=dict(old);v.update(inputHashes=inputs,testClassHashes={str(p.relative_to(work/'test-classes')):sha(p) for p in (work/'test-classes').rglob('*.class')},stages=dict(old['stages'],**{'test-compile':stage}),reusedSameGroupFreshMainCompile=ref(op),rootCompileRepeated=False,mainSourceByteExact=True,bug3019AllOldAssertionsInverseExact=True,MainSafeClosureRebuilt=False)
(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,whole27Compiled=True,mainCompilationRepeated=False,oldAssertionsInverseExact=True)))
