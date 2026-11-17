"""Format only the new pure-codec invariant and its four-test source; retain every token/literal."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sp=b/'evidence/PG37270-record-codec-invariant-source-v1/manifest.json';s=ld(sp)
assert s['actualExit']==0 and sha(r/s['mainPath'])==s['mainAfterSha256'] and sha(r/s['testPath'])==s['testSha256']
out=b/'evidence/PG37272-record-codec-format-v1';assert not out.exists();out.mkdir();rows=[]
imports=r'(?m)^import\s+(?:static\s+)?[\w.]+;\s*\n'
def normalized(text):
 names=re.findall(imports,text);assert len(names)==len(set(n.strip() for n in names))
 return sorted(n.strip() for n in names),[t for t,_ in lexical(re.sub(imports,'',text))]
for name in [s['mainPath'],s['testPath']]:
 p=r/name;before=p.read_bytes();cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--assume-filename',p.name,'-'];run=subprocess.run(cmd,input=before,capture_output=True,timeout=60)
 (out/(p.name+'.stdout')).write_bytes(run.stdout);(out/(p.name+'.stderr')).write_bytes(run.stderr);assert run.returncode==0 and normalized(before.decode())==normalized(run.stdout.decode());p.write_bytes(run.stdout)
 rows.append(dict(path=name,beforeSha256=hashlib.sha256(before).hexdigest(),afterSha256=sha(p),command=cmd,actualExit=run.returncode,importsAndNonImportTokensExact=True))
tests={n:h for n,h in s['originalInputHashes'].items() if '/src/test/' in n};assert len(tests)==3 and all(sha(r/n)==h for n,h in tests.items())
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourcePatch=dict(path=str(sp.relative_to(r)),sha256=sha(sp)),files=rows,originalThreeWholeTestsUnchanged=tests,originalWholeCases=16,newWholeCases=4,expectedCases=20,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,formatted=2,originalTestSourcesUnchanged=3,expected20=True,productTests=0)))
