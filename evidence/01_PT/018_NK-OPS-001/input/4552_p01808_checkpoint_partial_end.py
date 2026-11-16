"""Return true16 and exact unresolved conditions; no partial-row or original-parent credit."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import digest,end_fields
from source_evidence_binding import bind
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
start=load(d/'046_P01808現Checkpoint通常15群開始.json');pp=b/'evidence/PG36998-checkpoint16-scope-return-v1/manifest.json';p=load(pp)
assert p['actualExit']==0 and p['success']==16 and p['changedCatalogRawAllMiss0']
q=load(Path(sys.argv[1]));now=datetime.datetime.now(datetime.timezone.utc).isoformat();bound=end_fields(start['quota'],q,digest(q),now,p['terminalAtUTC'],8)
assert not any(x['groupId']==start['groupId'] and x.get('groupBoundary')=='END' for x in map(json.loads,metrics.EVENTS.read_text().splitlines()))
nxt=('Continue independent priority C02: inspect all14 owned deployment Unit/drop-in paths and original SupplementaryUnitTemplateTest5/public resources and exact old1553/1555 proofs before any new execution. Determine source/resource/independent golden applicability, execute only genuinely missing ordinary text contract tests. No service/VM/Root/intent/native/DB/key operations. P01808 remains partial: compiler capture default requires PG and active-native methods/branch plus StopHold/PrivateFile remain held; F02/F03 and QA056 end dependencies persist. Preserve current16 and do not repeat it for confirmation.')
values=dict(bound,source=p['sourceCore'],actualUnitSource=p['actualUnitSource'],run=p['run'],groupBoundary='END',
    wbsLeafIds=start['values']['wbsLeafIds'],workCategory='SELECTED_TEST',workAttributionKind='ORIGINAL_PLAN',
    managementWorkIds=['A2-28.01'],estimateAtGroupStartPp=start['values']['estimateAtGroupStartPp'],groupCapPp=8,
    sourceEvidenceBinding=bind([(pp,sha(pp))],p['sourceCore']),completedOriginalRowPricePp=0,remainingOriginalRowPricePp=3.9,
    addedPricePp=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,
    criterionReductions=['P01808.01/.02 current Checkpoint changed source: prior12 success inapplicable; actual whole16/FESnotrun0 plus8target CRC and no forbidden native init/probe now established',
      'BUG2803 three changed fatal catalogs: parameterized constructor/string/data all raw32line3method18branch147instruction hit, literal Error identity and normal fixed IO verified',
      'P01808 ordinary point/closing: Point.valueOf and five previously missing capture branches covered; whole target still7line3method2branch38instruction missing',
      'P01808.03 remaining explicit: source/native/fullstream qualification and end dependencies unclosed, no historical14/current16 arithmetic union'],
    technicalMeasurementDelta=dict(currentTests=16,newDefinitions=4,failed=0,errors=0,skipped=0,notRun=0,
      targetRaw=p['targetRaw'],qualifiedChangedCatalogs=3,all280HelperCountersRetained=True,old14Replayed=0,
      normalClosingAdditionalBranchHits=5,remainingNativeBranches=1,remainingCompilerDefaultBranch=1),
    bugsLocallyClosed=['BUG2803','BUG3141','BUG3142','BUG3143'],bugsOpen=['BUG2804','BUG3144'],
    horizontalClosed=['YKT2610','YKT2611','YKT2612'],horizontalOpen=['YKT2359','YKT2399','YKT2613'],nextCommand=nxt)
event=metrics.append(start['groupId'],'CHECKPOINT',values);target=d/'048_P01808通常16部分返却・残条件.json'
summary=('Core01c3b1a3/Unit1cd9e93c/PG36994当16全成功/FESnotrun0、36996独立同exec/全280physical/CRC-init/ConsoleXML検証0。新三fatalcatalogはraw32L3M18B147I全hitでBUG2803当三口限定CLOSED、その他static Main一site/Test三site適用未分類0・Root/全Bootstrap200SB0。新Closing/enumで旧15のraw9L4M7B51I missから当16の7L3M2B38I missへ不足比較、exec合算0。残はnative正常default ctor/二lambda/open activeとcompiler MatchException default一branch、native採取・StopHold7・PrivateFile7等HOLDを実行/合格へ代替0。元14の五physicalと三Test sourceは同一、変更helper再資格を条件に参照し確認再演0。Test表現三site/cleanup説明/Console parserの失敗を保存し是正・同source16で確認。元A2-28.01開始1.5/3.9/7.7 cap8、行未完/価格消化0・追加0・全残1094.336pp不変。P01808三子/全9条件とF02F03終了依存未成立、正式1964/53・元190新規0・工数null。')
target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,values=values,quota=q,proof=ref(pp),remainingDetailBasePp='1094.336',summary=summary),ensure_ascii=False,indent=2)+'\n')
l=r/'documents/900_OTHER/910_台帳'
with (l/'915_障害表.md').open('a') as f:
    for ident in ['BUG2803','BUG3141','BUG3142','BUG3143']:f.write('\n2026-11-17 '+ident+' 当provider三catalog又は当fixture/metadata対象を限定CLOSED。'+summary+' 証跡PG36998 SHA256 '+sha(pp)+'、PG fix75d0cacb4f/Core'+p['sourceCore']+'、Test修正Unit'+p['actualUnitSource']+'。完了2026-11-17。\n')
    f.write('\n2026-11-17 BUG3144 ordinary CLOSING/Point.valueOf不足は当16で是正、implicit compiler default1branchとnative active1branch/3methodが残るため全体OPENを維持。PG36996/36998。\n')
with (l/'916_横展開管理台帳.md').open('a') as f:
    for ident in ['YKT2610','YKT2611','YKT2612']:f.write('\n2026-11-17 '+ident+' 当fixture/元原本/metadata対象の是正と全対象非該当根拠・同16/負例により限定CLOSED。'+summary+' 証跡PG36998 SHA256 '+sha(pp)+'、修正Unit'+p['actualUnitSource']+'、関連input/ledgerのGit履歴。\n')
    f.write('\n2026-11-17 YKT2359 BUG2803当三catalogは固定Error cause/suppressed/SQL-nextと非fatal循環の独立fixtureで同一fatal/通常秘匿IOを確認し限定是正済。global YKT2359/2399/2613、実native/privatefile/sourcequalificationと親はOPEN。三catalog raw32L3M18B147I miss0、他default native/generate branchを除外/合格化せずPG36998へ返却。\n')
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
    p2=r/'documents/400_PGPT/450_品質'/name;title,body=p2.read_text().split('\n',1);p2.write_text(title+'\n\n## WBS66 P01808現Checkpoint通常16・具体残2branch '+now+'\n\n'+summary+' own unit/post/scope-return全真正terminal0、known own job残0・foreign/VM/aru未照会UNKNOWN、fresh残'+str(q['primary']['remainingPercent'])+'・共有差'+str(bound['observedSharedPp'])+'、event '+event+'。次: '+nxt+'\n'+body)
s=r.parent/'PMO/pgpt-completion-stage-20261102'
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
    p2=s/name;v=load(p2);v.update(lastEventId=event,ordinaryActiveGroup=None,ordinaryGroupNotYetClosed=False,currentQuota=q,productionCoreMain=p['sourceCore'],actualUnitSource=p['actualUnitSource'],latestWbs66Record=ref(target),nextCommand=nxt,mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=bound['newImplementationAllowedByQuota']);v['currentManufacturingBoundary']=dict(source=p['sourceCore'],unit=p['actualUnitSource'],run=p['run'],ownJobState='TRUE_TERMINAL0_16_POST_RAW',foreignHostVmDbState='UNQUERIED_UNKNOWN',scope='PUBLIC_CHECKPOINT16_PARTIAL_NATIVE_COMPILER_GAPS',evidence=ref(pp),whole451Accepted=False,newAcceptance=0);p2.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(b/'4463_P01808通常16実行結果・不足引渡し.md').open('x').write('# P018-08 通常16実結果と不足\n\n'+summary+'\n\n証跡 '+str(pp.relative_to(r))+' SHA256 '+sha(pp)+'。元15と当16のsource/exec/XMLを分離し、旧14のtarget byte一致を新16へ算術加算しない。全command/時刻/環境/出力hashは36994/36996。旧Unit15のConsole case-label誤記は元XMLで訂正し、失敗/skipは一件も成功へ変換していない。\n')
print(json.dumps(dict(actualExit=0,event=event,tests=16,catalogsQualified=3,newOriginalAcceptance=0,originalRowCompletedPp=0,observedSharedPp=bound['observedSharedPp'])))
