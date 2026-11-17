"""Correct the validator's import-order assumption, retaining exact non-import Java tokens."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text())
old=b/'evidence/PG37212-monitor-lock4-format-v1';assert sorted(p.name for p in old.iterdir())==['BatchMetricRecorder.java.stderr','BatchMetricRecorder.java.stdout']
sp=b/'evidence/PG37210-monitor-lock4-source-v1/manifest.json';p=ld(sp)
assert all(sha(r/x['path'])==x['afterSha256'] for x in p['mainChanges'])
ledger=r/'documents/900_OTHER/910_台帳';bug=ledger/'915_障害表.md';horizontal=ledger/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'\bBUG-?(\d{3,4})(?!\d)',bug.read_text())))==3161
assert max(map(int,re.findall(r'\bYKT-?(\d{3,4})(?!\d)',horizontal.read_text())))==2630
with bug.open('a') as f:f.write('\n\n## BUG3162 PG 2026-11-17 formatter検証のimport順序仮定\n\n対象4643/PG37212。重要度低/優先中。期待GJFによる正規import整列を許容し、非importの全literal/tokenとimport集合を保持。実際は先頭Mainの正常GJF stdout/exit0を収集後、import再配列をtoken変更と誤判定してAssertionError。Main書戻し前で全三候補hash不変、原42Test不変、製品実行0。元stdout/stderrを保存し、元compound shellの最終git diffはexit0、Python別終了値は独立未収集とする。修正前起票、import集合重複なしの一致と非import全token一致の二重検証へ限定是正。修正/再試験未確定、YKT2631、状態OPEN。\n')
with horizontal.open('a') as f:f.write('\n\n## YKT2631 BUG3162 四formatter入力\n\n対象三Mainと新MonitoringLockContractTest、原因import整列を意味変更と誤認。全四入力でimport集合一致/重複0とimport以外全Java token/literal一致、stderr/exit先保存を確認する。元PG37212正常formatterと検証失敗を保持。現場修正に合わせ上位規則やMain期待を変更しない。状態OPEN。\n')
(old/'failure.safe.json').open('x').write(json.dumps(dict(outerCompoundExit=0,pythonSeparateExit=None,pythonTerminal='AssertionError before first write',formatterChildExit=0,formatterStdoutSha256=sha(old/'BatchMetricRecorder.java.stdout'),formatterStderrSha256=sha(old/'BatchMetricRecorder.java.stderr'),allMainCandidatesUnchanged=True,productTestsExecuted=0),indent=2)+'\n')
pattern=r'(?m)^import\s+(?:static\s+)?[\w.]+;\s*\n'
def tokens(text):
 imports=re.findall(pattern,text);assert len(imports)==len(set(s.strip() for s in imports))
 return sorted(s.strip() for s in imports),[t for t,_ in lexical(re.sub(pattern,'',text))]
paths=[x['path'] for x in p['mainChanges']]+['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/MonitoringLockContractTest.java']
out=b/'evidence/PG37214-monitor-lock4-format-v2';assert not out.exists();out.mkdir();rows=[]
for n in paths:
 src=r/n;raw=src.read_bytes();name=src.name
 command=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--assume-filename',name,'-']
 result=subprocess.run(command,input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
 (out/(name+'.stdout')).write_bytes(result.stdout);(out/(name+'.stderr')).write_bytes(result.stderr)
 assert result.returncode==0 and tokens(raw.decode())==tokens(result.stdout.decode())
 src.write_bytes(result.stdout);rows.append(dict(path=n,beforeFormatSha256=hashlib.sha256(raw).hexdigest(),afterFormatSha256=sha(src),actualExit=result.returncode,command=command,importsExactSetAndNonImportAllTokensExact=True))
assert all(sha(r/n)==h for n,h in p['originalTestSourceHashes'].items())
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourcePatch=dict(path=str(sp.relative_to(r)),sha256=sha(sp)),files=rows,originalTestSourceCount=len(p['originalTestSourceHashes']),originalTestSourcesUnchanged=True,newTests=6,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,formatted=len(rows),newTests=6,productTests=0)))
