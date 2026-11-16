"""Recover existing successful analyzer output only; preserve the failed 159-target wrapper guard."""
from pathlib import Path
import datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';l=r/'documents/900_OTHER/910_台帳';a=l/'915_障害表.md';y=l/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'^## BUG-?(\d{3,4})(?!\d)',a.read_text(),re.M)))==3120
assert max(map(int,re.findall(r'^## YKT-?(\d{3,4})(?!\d)',y.read_text(),re.M)))==2592
with a.open('a') as o:o.write('\n## BUG3121\n発見PT/2026-11-16、低/中、4384 raw分析wrapper。期待target七class、実際元wholemodule159target固定guardを残して解析成功後停止。PG36444 analyzer真正0/全stdout保持、製品18 FES0だが品質未受入。YKT2593/451。全classfile/Java tool/PTを再実行せず保存stdout/元postを別4385で照合・欠落manifestだけ回収する。修正前OPEN。\n\n## BUG3122\n発見PT/2026-11-16、低/中、集約七値新fixtureと必要原14のclosure。期待当七classは既知FieldDefinition switch一件以外の値API/境界網羅、実際当18のrawはCommonHeader等14getter未hit及びWireMessage三比較分岐不足。前全145では当getter等は既hitのため製品不具合でなく選択fixture不足、当18を全品質へ昇格0。YKT2594/BUG3111/SS322323354/451。元source/run/不足rawを保持し、固定独立component getter期待とWireMessage長三要素の個別不一致/欠落を追補する。期待変更0、次source同18必要再試験で確認、修正前OPEN。\n')
with y.open('a') as o:o.write('\n## YKT2593\n元BUG3121、対象4384 target159固定値/派生4374/4378未使用draftは歴史のみ。保存analyzer stdoutで実七targetと176class/CRC/Code/counterを独立照合、wrapper修正のため製品やJava分析を再演しない。元guard失敗保持、回収前OPEN。\n\n## YKT2594\n元BUG3122、対象七class全getter/constructor比較と新Test/原14whole closure。現在18で既hit部分は再利用で済ませず変更fixtureの同source18を必要再実行し、14getterとWireMessage三比較が同runでhitしたことを確認する。FieldDefinition既知一branch/四map/globalは本件対象外でOPEN。検索だけclose0、元失敗品質は保持。\n')
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));rawdir=b/'evidence/PG36444-protocol-aggregate-unfiltered-v3';postp=b/'evidence/PG36443-protocol-aggregate-post-join-v3/manifest.json';post=ld(postp);exitp=rawdir/'analysis-exit.json';assert ld(exitp)['actualExit']==0
classes={};methods=[]
for line in (rawdir/'analysis.stdout').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':
  row=dict(name=f[1],id=f[2],dataPresent=f[3]=='true',probes=int(f[4]),access=int(f[5]),counters={});assert f[1] not in classes;classes[f[1]]=row;start=6
 else:
  assert f[0]=='METHOD';row=dict(className=f[1],name=f[2],descriptor=f[3],access=int(f[4]),counters={});methods.append(row);start=5
 for value in f[start:]:
  key,missed,hit=value.split(':');row['counters'][key]=dict(missed=int(missed),covered=int(hit))
assert len(classes)==176 and {n:v['id'] for n,v in classes.items()}==post['classIds']
assert all(sum(v['counters']['METHOD'].values())==post['actualJvmCodeMethodCounts'][n] for n,v in classes.items())
targets=set(post['declaredTargets']);assert len(targets)==7
counter={k:dict(missed=sum(classes[n]['counters'][k]['missed'] for n in targets),covered=sum(classes[n]['counters'][k]['covered'] for n in targets)) for k in next(iter(classes.values()))['counters']}
missing=[m for m in methods if m['className'] in targets and m['counters']['METHOD']['missed']];assert len(missing)==14
branches=[m for m in methods if m['className'] in targets and m['counters']['BRANCH']['missed']];assert sum(m['counters']['BRANCH']['missed'] for m in branches)==4
old=ld(b/'evidence/PG36284-ssc445-registry-unfiltered-v2/manifest.json');prior=[m for m in old['missedCodeMethods'] if m['className'] in targets];assert len(prior)==17
for oldm in prior:
 hit=[m for m in methods if (m['className'],m['name'],m['descriptor'])==(oldm['className'],oldm['name'],oldm['descriptor'])];assert len(hit)==1 and hit[0]['counters']['METHOD']['covered']==1
out=b/'evidence/PG36446-protocol-aggregate-raw-recovered-v3';out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain=post['productionCoreMain'],actualUnitSource=post['source'],post=ref(postp),originalAnalyzerStdout=ref(rawdir/'analysis.stdout'),originalAnalyzerExit=ref(exitp),classes=classes,methods=methods,physicalClassHashes=post['physicalClassHashes'],targetCounters=counter,targetMissingMethods=missing,targetMissingBranches=branches,previous17MissingMethodsNowHit=prior,targetRawFour100=False,whole451Accepted=False,applicationTestsExecuted=0,analyzerReexecuted=False,classfilesReadOrDefined=0,formalUpdated=False);(out/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,previous17NowHit=True,missingGetterMethods=14,missingBranches=4,analyzerReexecuted=False)))
