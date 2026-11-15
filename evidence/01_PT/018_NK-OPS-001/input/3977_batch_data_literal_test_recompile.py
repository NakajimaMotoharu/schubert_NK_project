"""BUG3082 fixed literal representation; recompile Tests only, retain exact same-group Root Main."""
from pathlib import Path
import hashlib,json,shutil,subprocess
import pg9666_pagination_static as c
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379/pg35022-batch-data8-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'evidence/PG35020-batch-data8-source-v1/manifest.json';mp=b/'evidence/PG35022-batch-data8-prepare-v1/manifest.json';src=ld(cp);m=ld(mp);p=r/src['testSources'][-1]['path'];old=p.read_text();constant='  private static final String EXPECTED_CLEAN_BATCH_RUN = "CLEAN_BATCH_RUN";\n';assert old.count('"CLEAN_BATCH_RUN"')==5
# One BatchStep catalog cell and four CleanupKind parent cells share the fixture's own literal.
p.write_text(old.replace('"CLEAN_BATCH_RUN"','EXPECTED_CLEAN_BATCH_RUN').replace('  private static final String UNKNOWN',constant+'  private static final String UNKNOWN'))
subprocess.run([str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30)
current=p.read_text();assert current.replace(constant,'').replace('EXPECTED_CLEAN_BATCH_RUN','"CLEAN_BATCH_RUN"')==old
for path in m['apiMainSources']+m['apiTestSources'][:2]:assert sha(r/path)==m['inputHashes'][path]
assert {n:sha(w/'target/classes'/n) for n in m['mainClassHashes']}==m['mainClassHashes']
src['inputHashes'][str(p.relative_to(r))]=sha(p);src['originalSourceEvidence']=ref(cp);src['fixedLiteralInverseByteExact']=True;sourceout=b/'evidence/PG35028-batch-data8-source-v2';sourceout.mkdir();(sourceout/'manifest.json').open('x').write(json.dumps(src,ensure_ascii=False,indent=2)+'\n')
o=b/'evidence/PG35023-batch-data8-test-recompile-v1';o.mkdir();c.SLOT=o
for filename in ['nullaway-compile.stdout','nullaway-compile.stderr']:shutil.copyfile(mp.parent/filename,o/filename)
stage=c.step('test-compile',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(w/'target/classes')+':'+':'.join(m['dependencies']),'-d',str(w/'test-classes'),*[str(r/n) for n in m['apiTestSources']]],r);assert stage['actualExit']==0 and not stage['timedOut']
m['stages']['test-compile']=stage;m['inputHashes'][str(p.relative_to(r))]=sha(p);m['testClassHashes']={str(p.relative_to(w/'test-classes')):sha(p) for p in (w/'test-classes').rglob('*.class')};m['sameGroupOriginalRootCompile']=ref(mp);m['MainBinaryReusedSinceFirstPrepareInSameGroup']=True;m['MainSourceAndBinaryUnchangedAfterFixtureStyleFix']=True
(o/'manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,originalMainRootRecompiled=False,testsRecompiled=8,MainSourcesUnchanged=10,independentExpectedExpandedByteExact=True)))
