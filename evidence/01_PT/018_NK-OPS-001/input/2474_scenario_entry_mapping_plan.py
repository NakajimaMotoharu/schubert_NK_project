"""Price the missing preserved-order ID mapping artifact; no original data/DB/operations."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/ScenarioEntryMigrationMap.java';test=main.replace('/main/','/test/').replace('.java','Test.java');assert not (r/main).exists() and not (r/test).exists()
spec=r/'evidence/01_PT/019_NK-MIG-001/011_Scenario現行ID順移行対応・独立十二仕様.md';assert not spec.exists();spec.write_text('''# Scenario entry 現行ID順移行対応・独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT005/FUN004、UI223§3.2/254§4、SS331 script_entries/SS343§10。未実装artifactの新PG/PT。元IDを維持する必要はないが、現行script_entries.id昇順をdisplay_orderへ固定する。target ID順を採用しない。ファイル別entry_index、game/file順、音声link/pair/media順は別条件、当部品で閉じない。

予定Productionはbootstrap migration/ScenarioEntryMigrationMap、IdPair(currentId,targetId)、MappedEntry(currentId,targetId,displayOrder)。currentIdは既採取のsigned longを狭めず、targetIdは新identityの正long、source/target重複は拒否。source昇順へ1始まりdense displayOrderを割当、Listのint件数はSS331 N12上限内、公開MappedEntryのorderは1..999999999999を検証する。immutable List/Mapを明示copy、original入力/返却List/byteは別所有。lookupは既sourceのみ・未知を0へ補完しない。実DB存在や完全件数、FK、file/entry/game一致、DBロードを証明しない。

canonicalはNKMIGSCENARIOORDER1 LFの後、sourceId TAB targetId TAB displayOrder LF、source昇順ASCII正準decimal（sourceはsigned）だけ。入力再順序化/再採番後も同sourceから同tuple順、actualMasterアクセス/DB/移行/RootVMnative鍵Unit操作0。

| ID PT-MIG-ORDER | 独立期待値 |
|---|---|
|001| (10→100,2→900)から手書き2/900/1と10/100/2の全byte golden。target順と区別 |
|002| source LongMIN/負1/0/LongMAXのsigned比較、target正long上端、allaccessorsと固定redaction |
|003| source重複拒否、元list不変 |
|004| target重複拒否、source順とは別のbijection |
|005| IdPair/MappedEntryのtarget0/負値拒否、source値を勝手に変えない |
|006| MappedEntry order0/負/N12超拒否、1/N12許容 |
|007| list/null要素拒否、NPEcatch正常化0 |
|008| 元mutableList/返却List/返却byteへの変更が保存順・goldenに影響しない |
|009| 既source毎lookupの独立target/orderと未知source拒否、固定診断/cause/suppressed |
|010| 空mapはheaderのみ・lookup拒否、移行完了の証明ではない |
|011| sourceIDのgap/renumberedtargetに影響されないdense順位、再順序入力の同一byte |
|012| 所有8worker/64taskで固定goldenとlookup、Future各5秒/finallyshutdownNow-await10assert・未終端fail |

詳細SSC343を先行起票しdesign-only main公開、owner登録後PG。全3physical/JDKJSpecifyJUnitだけ。RootNullAway/lintWerror/PMD/CS/SB/formatと元全12固定source一回/別postのCRC初期化/全四counterを確認。期待は上表literalと算術から独立作成、production encoder/sortから生成0。失敗/未網羅は保持、手除外/抑制/旧exec合算なし。実行環境/source/branch/tool/command/exit/input/output/hashはmanifestへ。

追加不足価格 .8/2.4/4.8: 詳細 .1/.3/.6（上限1）、source/Test .4/1.2/2.4（上限3）、normal .3/.9/1.8（上限3）。original/2の全ETL/実master/FK/IDmapping/表示順/再実行criteria費用、S/V原枠は保持。actual費/token不明null、元190/全451/ITST未受入。
''')
old=next(d.glob('1662_*'));f=ld(old);est=dict(low=.8,base=2.4,high=4.8)
for k,v in est.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+v,3)
f.update(previousForecast=ref(old),revision='428-MISSING_SCENARIO_ENTRY_ID_ORDER_COMPONENT_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='P01903_MISSING_SCENARIO_ENTRY_ID_ORDER_COMPONENT',estimate=est,detail=dict(low=.1,base=.3,high=.6),sourceAndWhole12=dict(low=.4,base=1.2,high=2.4),normal=dict(low=.3,base=.9,high=1.8),reason='Existing ETL ID/display-order mapping artifact absent; asset inventory component intentionally does not implement ID mapping. Add separate pure data component needed by approvedUI223/254, preservefullETL andexistingoriginalestimate/acceptance.'))
br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp']);fp=d/'1664_WBS65予実・ScenarioID順対応部品追加版428.json';wr(fp,f)
c=ld(i/'2435_p01803_reader_tool_start.json') if (i/'2435_p01803_reader_tool_start.json').exists() else ld(i/'2454_p01903_three_original_start.json');c={k:c[k] for k in ['groupId','recordPath','category','kind','scope','oracleRefs','wbsLeafIds','source','run','estimate','capPp','workIds','forecastRef','nextCommand']};c.update(groupId='PGPT-WBS65-SSC343-SCENARIO-ID-ORDER-DETAIL-DESIGN-20261114',recordPath=str((d/'1665_WBS65ScenarioID順対応詳細開始.json').relative_to(r)),category='CONTRACT_AUDIT',kind='ADDITIONAL_FINDING',scope='MissingScenarioentryID/orderpureartifact detailonly .1/.3/.6cap1, fromUI2233.2/UI2544/SS34310/331 andcurrentV002 unchanged. RecordSSC343beforeformatdetail, safe signedsource/positiveuniqueTarget/denseSourceOrder/immutable dataonly, publishdesign-onlymain beforeanysource. No actualoriginalDB/RootVMnativekeysUnitdeploystart/stop/Go.',oracleRefs=[ref(spec),ref(b/'evidence/PG30234-migration-asset12-independent-source-trace-join-v1/manifest.json')],wbsLeafIds=['WBS-P019-03.02'],source='72449924b1b2f0b5624ae600ab687f77ccbfb8a6',run='PG30264-SCENARIO-ID-ORDER-DETAIL',estimate=dict(low=.1,base=.3,high=.6),capPp=1,workIds=['P01903_SSC343_SCENARIO_ID_ORDER_DETAIL'],forecastRef=ref(fp),nextCommand='RegisteractualnextSSC343beforeeditingSS343; internaldataformat only noRDUIchange/QA. CurrentId signedlongpreserved, uniquetargetpositive/denseorder sourceSort asapprovedUI223, literalrows/currentlookup/immutableprivateMapList beforePG. DesignonlysparsePR/main publish andconfirmremote. ThenregisteroneMainownerP01903 +pricealready source1.2/normal.9 beforemanufacturing/Test12; no realoriginalDB/RootVMnativekeyUnitoperations, do notstopatdesign/report.');wr(i/'2475_scenario_entry_mapping_detail_start.json',c);print(json.dumps(dict(actualExit=0,plannedMain=main,totalAdditional=est,remaining=f['revisedRemainingPp'])))
