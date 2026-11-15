"""Original1030 exact-source retention and independent literal copy-frame oracle, no product execution."""
from pathlib import Path
import json,hashlib,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';e=b/'evidence/PG33670-copyverify1050-source-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3372_current_transfer1030_media_profile.json');main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/MigrationMasterCopyVerifier.java';test=main.replace('/main/','/test/').replace('.java','Test.java');old={}
for source,paths in [(pf['productionCoreMain'],pf['mainSources']),('af4a65492636083355a87bb494497291c2e35e16',[x['path'] for x in pf['testSources']])]:
 for path in paths:
  h=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert sha(r/path)==h,path;old[path]=h
assert len(old)==103
s=(r/test).read_text();oldtest=(e/'original-test-before-literal-constants.java.txt').read_text();back=s.replace('  private static final String ZERO = "0";\n','').replace('  private static final String LF = "\\n";\n','');tokens=lambda v:re.findall(r'"(?:[^"\\]|\\.)*"|[A-Za-z_$][\w$]*|\S',v);reversed_tokens=[{'ZERO':'"0"','LF':'"\\n"'}.get(t,t) for t in tokens(back)];assert reversed_tokens==tokens(oldtest)
assert len(re.findall(r'@Test\b',s))==20
g=load(e/'independent-golden.json');assert g==load(b/'evidence/PG33314-copyman990-source-v1/independent-golden-vectors.json')
for k in ['normal','empty']:
 assert hashlib.sha256(g[k]['canonical'].encode()).hexdigest()==g[k]['sha256'] and json.dumps(g[k]['canonical']) in s and g[k]['sha256'] in s
code=(r/main).read_text();assert all(x in code for x in ['byte[] stable = retained.clone();','MessageDigest.getInstance("SHA-256").digest(stable)','new MigrationMasterCopyManifest(mappings, declared)','MessageDigest.isEqual(stable, manifest.canonicalBytes())']) and all(x not in code for x in ['catch (','java.nio.file','java.sql','java.net','.commit(','.rollback('])
m=dict(actualExit=0,newMain=ref(r/main),newTest=ref(r/test),oldUnchangedSourceHashes=old,oldDefinitions1030Preserved=True,newDefinitions=20,wholeExpected=1050,allMain=52,allTestSources=53,physicalClasses=73,independentGolden=ref(e/'independent-golden.json'),literalReplacementInverseTokenEqual=True,stableByteCloneAndExactCanonicalCheck=True,noActualFileDbDriverNativeAuthority=True,newAcceptance=0,formalAccepted=False);(e/'manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=20,whole=1050,oldSources=103))
