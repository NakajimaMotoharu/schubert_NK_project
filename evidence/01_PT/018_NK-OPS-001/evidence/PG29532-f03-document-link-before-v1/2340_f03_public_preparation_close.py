"""Credit exactly canonical F03/1 after public inventory, not /2/fullgate or product PT."""
from pathlib import Path
from decimal import Decimal
import csv,datetime,hashlib,json,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';S=R.parent/'PMO/pgpt-completion-stage-20261102'
sys.path.insert(0,str(R/'tools/quality'));from pgpt_wbs_canonical_progress import validated_snapshot
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));load=lambda p:json.loads(p.read_text())
def write(p,x):
 assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
start=load(B/'input/2338_f03_stage1_start.json');mp=B/'evidence/PG29526-f03-public-six-module-preparation-v1/manifest.json';m=load(mp)
assert m['actualExit']==0 and m['completedOriginalPreparationWorkIds']==['WBS-F03/1'] and m['newProductTestsExecuted']==m['newAcceptance']==0 and len(m['missingConditions'])==5
inv=load(R/m['sourceInventory']['path']);assert sha(R/m['sourceInventory']['path'])==m['sourceInventory']['sha256'];assert len(inv['heldTestNames'])==2 and all(x['sha256'] is None for x in inv['heldTestNames']);assert inv['binaryReadStatCompileLoadCount']==0 and inv['physicalMainDenominator'] is None
assert len(m['moduleInventory'])==6 and sum(x['mainJavaSourceFiles']+x['testJavaHashedFiles'] for x in m['moduleInventory'])==len(inv['publicJavaSha256'])==1957
assert all(not x['wholeCurrentModuleQualityAccepted'] and x['physicalMainClasses'] is None for x in m['moduleInventory'])
assert not m['allSixCurrentStaticQualified'] and not m['formalUpdated'] and m['actualEnvironmentOperations']==m['actual4BinaryOperations']==m['root2BodyOperations']==m['protected2ToolOperations']==0
old=R/load(S/'checkpoint.json')['currentWbs65Forecast']['path'];f=load(old);assert ref(old)==start['forecastRef'];work='WBS-F03/1';assert work not in f['completedPlanWorkIds'] and 'WBS-F03/2' not in f['completedPlanWorkIds']
plan=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv';rows=list(csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t'));row=next(x for x in rows if x['実行ID']==work);assert row==m['rowCriterion']
for k,col in [('low','低位pp'),('base','標準pp'),('high','高位pp')]:
 x=Decimal(row[col]);assert x==Decimal(str(start['estimate'][k]))
 f['completedPlanPriceSumPp'][k]=float(Decimal(str(f['completedPlanPriceSumPp'][k]))+x)
 for name in ['remainingOriginalPlanPricePp','revisedRemainingPp']:f[name][k]=float(Decimal(str(f[name][k]))-x)
f['previousForecast']=ref(old);f['revision']='381-F03_PUBLIC_SIX_MODULE_SCOPE_PREPARATION';f['atJST']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();f['completedPlanWorkIds'].append(work)
# Preserve existing legacy reference: it was not previous canonical completion.
assert work in f['completedPreparationWorkIds']
if 'WBS-F03' not in f['partiallyCompletedPlanWorkIds']:f['partiallyCompletedPlanWorkIds'].append('WBS-F03')
for key in ['canonicalSchedulePricePrefixBasePp','startedRowPriceSumBasePp']:f[key]=round(f[key]+start['estimate']['base'],3)
description='F03/1は625行原判定どおり公開規約・Root7reactor中Production6/Tool1・POM/rules・Main967/Test992名中HOLD2除外の公開1957Java hash・不足5条件を保存。物理class分母はnull、歴史1643/1843を流用しない。現RootJSpecify1.0.1は421 PG316の収束承認と整合、451初期1.0.0記述と時点を分離。PG29478のfresh155限定資格を参照し新PT0、全6静的/実環境/Root2/actual4.class/QA051 finalを未受入/HOLD維持。空owned監査でなく原/1の公開範囲criterionだけ、原/2/元190新0/正式1964-53/工数null。原費用1.5/4/8のみ完了、実費/新追加費としない。'
f['remainingPriceAccountingNote']=description;f['canonical625Progress']=validated_snapshot(rows,f,dict(path=str(plan),sha256=sha(plan)));assert f['canonical625Progress']['uniqueCompletedRows']==151
tech=dict(kind='F03_STAGE1_PUBLIC_QUALITY_SCOPE_INVENTORY_ONLY',evidence=ref(mp),productionModules=6,characterizationToolModules=1,mainJavaSourceFiles=sum(x['mainJavaSourceFiles'] for x in m['moduleInventory']),testJavaNamedFiles=sum(x['testJavaNamedFiles'] for x in m['moduleInventory']),heldTestNames=2,publicJavaHashedFiles=1957,currentPhysicalMainDenominator=None,productTestsExecuted=0,newAcceptance=0,allSixCurrentStaticQualified=False,effortCompletionRate=None)
f['latestGroupTechnicalResult']=tech;fp=D/'1539_WBS65予実・六module公開品質範囲後版381.json';write(fp,f)
nextcmd='ProceedactualP00304/05/06/07 originalpublicsourcecontracts after625owner/price and source/HOLDread. PreferpermittedwholeoriginalnormalPT if independentclosure/finiteworker ready; no Root/VM/native/DB/key/actual4.class orRoot2 body access. Do not rerun155 or oldsuccess; Main8b539105 unchanged. Canonical151/625 (/1=123 /2=10 standalone18) isrecordedworkrowcount noteffort% orformalcriteriafreshreacceptance. Freshquota atboundary; nextusage21:40:08JST.'
c=dict(groupId=start['groupId'],recordPath=str((D/'1540_WBS65F03六module公開品質準備結果.json').relative_to(R)),manifestPath=str(mp.relative_to(R)),manifestSha256=sha(mp),terminalAtUTC=m['atJST'],run='PG29526',workIds=[work],outcome=m['endingStatus'],technical=tech,forecastRef=ref(fp),nextCommand=nextcmd,checkpointText=description+' 正本151/625行、版381残'+str(f['revisedRemainingPp'])+'未較正。')
write(B/'input/2340_f03_stage1_close.json',c)
md=D/'1541_F03六module規約・公開対象・残HOLD対応.md';assert not md.exists();lines=['# F03/1 公開品質範囲と不足条件','','当source '+m['source']+' / rule入力と範囲は[PG29526](../../../..'+'/../'+str(mp.relative_to(R))+')。原WBS-F03/1だけ完了、F03/2は未受入。','',description,'','|Module|Main Java source|Test named / hash|物理class分母|','|---|---:|---:|---|']
for x in m['moduleInventory']:lines.append('|'+x['module'].split('-')[-1]+'|'+str(x['mainJavaSourceFiles'])+'|'+str(x['testJavaNamedFiles'])+' / '+str(x['testJavaHashedFiles'])+'|未認証|')
lines += ['','Source数は物理class数やcoverage分母ではない。java textのみ、2 held Testは名前だけ。','']
for x in m['missingConditions']:lines += ['- '+x['id']+' '+x['status']+' / '+x['scope']+': '+x['condition']+' '+x['reason'],'']
lines += ['`python3 -B evidence/01_PT/018_NK-OPS-001/input/2339_f03_public_quality_inventory.py` 終了0。新規製品PT/coverageなし、静的解析を実行したとは記録しない。独立チェックは原criteria/固定module数/構成XMLと公開範囲counter・hashの照合で、production methodで期待値を生成しない。',''];md.write_text('\n'.join(lines))
# use absolute repo-local links for exact independent manifest in primary PT documents.
program=B
for name in ['001_NK-OPS-001_検査起動wrapper・unit単体テスト仕様書.md','002_NK-OPS-001_検査起動wrapper・unit実行結果.md']:
 p=program/name;p.write_text(p.read_text()+'\n\nWBS-F03/1公開品質scope/不足条件: [PG29526](evidence/PG29526-f03-public-six-module-preparation-v1/manifest.json)、[対応表](../../../documents/400_PGPT/470_PMO/600_通常PGPT_20261106/1541_F03六module規約・公開対象・残HOLD対応.md)。原/1のみ、新PT/coverage/全F03/正式認定0。\n')
p=R/'documents/900_OTHER/910_台帳/915_障害表.md';p.write_text(p.read_text()+'\n\nBUG2837限定完了（2026-11-13）：元2338/receiptとValueErrorをPG29528へ保全、oracleXMLをconfigurationInputRefsへ分離しguard不変更。freshreceiptでevent5135開始成立、PG29526公開対象inventory actualExit0でPOM hash/6module/原/1条件・不足を独立照合、製品PT0。再現は元XML入力の拡張子拒否、是正はmd/json oracleだけという既schemaを保つ。状態CLOSED（当管理callerのみ）、修正commitは本群publicationへ結ぶ。\n')
p=R/'documents/900_OTHER/910_台帳/916_横展開管理台帳.md';p.write_text(p.read_text()+'\n\nYKT2402追記（BUG2837）：schema対象oracle参照と構成XML入力を別fieldへ固定し、元PG29528拒否を保全。2338 callerだけPOM混入を是正、既1100/build_context guardは非該当で不変更、以前正常producerの再演0。PG29526がPOM別hashと規約md/json hashを検証し終了0、依存発行は真正開始0を確認してから実施。metadata限定で製品PT/全Tool品質へ加算しない。\n')
print(json.dumps(dict(closeConfig=str((B/'input/2340_f03_stage1_close.json').relative_to(R)),remaining=f['revisedRemainingPp'],canonical=f['canonical625Progress']['uniqueCompletedRows'],tech=tech),ensure_ascii=False))
