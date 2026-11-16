"""Preserve the second style result, ticket missing format after rename, then format only that test."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';l=r/'documents/900_OTHER/910_台帳';a=l/'915_障害表.md';y=l/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'^## BUG-?(\d{3,4})(?!\d)',a.read_text(),re.M)))==3119
assert max(map(int,re.findall(r'^## YKT-?(\d{3,4})(?!\d)',y.read_text(),re.M)))==2591
with a.open('a') as o:o.write('\n## BUG3120\n発見PT/2026-11-16、低/中、4375 Test rename工具のformat工程欠落。期待最小改名後にGJFを適用、実際PG36402 naming/Checkstyle全合格だがformat165のみ1。製品0・元TestをPG36429へ保存し修正前OPEN。YKT2592/451。GJF skip-reflowing-long-stringsを新Test一つへ適用しliteral/token一致を独立確認、全Root規則と必要18PTで検証、Main/期待変更0。\n')
with y.open('a') as o:o.write('\n## YKT2592\n元BUG3120、対象4375の改名結果/新Test全体。改名後の標準formatterを適用し全literalと非空白tokenを比較、他168sourceはbyte不変で非該当。新profileに固定しRoot静的/実18PT確認前OPEN、元失敗36402保持。\n')
t=r/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/ProtocolAggregateValueContractTest.java';old=t.read_text();e=b/'evidence/PG36429-protocol-aggregate-format-recovery-v1';e.mkdir();(e/'ProtocolAggregateValueContractTest.java.txt').write_text(old)
subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(t)],check=True,timeout=30)
new=t.read_text();tokens=lambda s:re.findall(r'"(?:\\.|[^"\\])*"|\S',s);assert tokens(old)==tokens(new)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));mp=e/'manifest.json';mp.open('x').write(json.dumps(dict(actualExit=0,originalFormatExit=1,bug='BUG3120',ykt='YKT2592',oldFixture=ref(e/'ProtocolAggregateValueContractTest.java.txt'),newFixture=ref(t),literalAndNonWhitespaceTokensExact=True,mainChanged=0,productExecutions=0),indent=2)+'\n')
c=json.loads((b/'input/4376_protocol_aggregate_profile_v2.json').read_text());c.update(id='PG36440-PROTOCOL-AGGREGATE-SEVEN-VALUES-18-V3',slots={k:str((b/('evidence/PG'+str(n)+'-protocol-aggregate-'+k+'-v3')).relative_to(r)) for k,n in [('prestyle',36432),('prepare',36434),('static',36436),('preflight',36438),('unit',36440),('post',36442)]},privateDirs=dict(prepare='pg36434-protocol-aggregate-values-v3',unit='pg36440-protocol-aggregate-values-v3'));c['closureProofs'].append(ref(mp));(b/'input/4380_protocol_aggregate_profile_v3.json').open('x').write(json.dumps(c,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tokensExact=True,newTests=4,mainChanged=0)))
