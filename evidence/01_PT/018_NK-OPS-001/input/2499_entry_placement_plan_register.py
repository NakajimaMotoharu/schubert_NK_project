"""Price/register missing entry-file placement; original prices, acceptance and held operations unchanged."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO';q=d/'600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/ScenarioEntryPlacementMap.java';test=main.replace('/main/','/test/').replace('.java','Test.java');assert not (r/main).exists() and not (r/test).exists();spec=r/'evidence/01_PT/019_NK-MIG-001/015_Entryとfile移行参照・順序接続の独立十二仕様.md';assert not spec.exists();spec.write_text('''# Entryとfile移行参照・順序接続：独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT005/FUN004、UI223§3.2/4/5・UI254§4、SS331/V002/V004・SS343§10。Entry global順とfile/game順の各部品だけではentry所属file・entry_index/FK宣言を接続できないため、新ScenarioEntryPlacementMapを製造する。元ID/順序/DDLを変更せず、実Current game/entry_index抽出・DB完全性/ロード成功は別条件。

入力は承認済みScenarioFileMigrationMap、ScenarioEntryMigrationMap及びPlacement(gameId,currentFileId,currentEntryId,entryIndex)のList。game1/2・entryIndex>=0、signed source IDを保存。両map/List/要素null拒否、入力件数はEntry対応件数と完全一致。currentEntryIdを一度だけ、対応済みfile/game・entryだけを許可し、targetFileId+entryIndex重複を拒否する。異なるfileの同indexは可。未知を補完/0/先頭へ送らない。これらは入力宣言の整合であり、実DB/game/FK/全99661件を証明しない。

PlacedEntryはcurrentEntryId,targetEntryId,displayOrder,gameId,targetFileId,entryIndex、targetEntry/file/orderは既N12、game1/2・index>=0をconstructorで保護。global rowsはEntry対応のdisplayOrder昇順、entriesForFile(game,sourceFile)は既知fileの行をentryIndex昇順に返す。既知空fileは空List、未知fileは拒否。global lookupはcurrentEntryIdのみ。入力/保存ListMapは明示不変copy、返却byteは毎回別所有、公開record/aggregate診断は固定redaction。内部FilePositionは非公開で診断/ログへ出さない。

canonical ASCII/LFはNKMIGENTRYPLACEMENT1 LFに続き currentEntryId TAB targetEntryId TAB displayOrder TAB gameId TAB targetFileId TAB entryIndex LF。空はheaderだけで移行完了ではない。Expectedは下記手書きtuple/byte、Production sort/encoder/record constructorで生成しない。

PT-MIG-PLACE001..012:
001 手書きgolden: global entry2→900/order1/game1/file500/index7、10→100/order2/game1/file800/index3、30→50/order3/game2/file600/index0。file source20→500、10→800とgame2 source10→600。file並びとentry全体順を混同しない。
002 同file内index0/IntegerMAXの順はglobal entry順と逆でも0→MAX。減算比較しない。
003 unknown file・別game sourcefileの参照拒否、既知別game同file sourceを分離。
004 unknown global source entry拒否。
005 currentEntryId重複、file/index重複を個別拒否、別file同index可。
006 入力件数不足/余剰拒否、空map/headerと既知空fileの空List、未知file拒否。
007 game上下境界をPlacement/PlacedEntry/entriesForFileで拒否。
008 entryIndex負拒否・0/MAX許容、PlacedEntryのtarget/order/file N12下限上限とその外を個別検査。
009 null両map/List/要素、unknownlookup・固定診断/cause/suppressed無し。
010 元mutable入力/返却List/返却byteの所有分離。
011 source signed端/0と入力再順序、target再採番逆転に独立したglobal tuple/order。
012 owned8worker64task、Future各5秒/finallyshutdownNow-await10assert、独立byte/lookup/file順。

新Main/Placement/PlacedEntry/privateFilePosition全4physicalと既Entry3/File4の完全source closureを通常検証し、新componentとsupportを明示分離。既存whole12を確認目的で再演せず、新接続whole12だけを実行。新Main四counterとscope全counter/未実行support/既定generated filterを独立postで区別し、旧execを合算しない。実DB/Current/RootVM/native/鍵/Unit/Go/全451/ITSTは未受入。

不足追加1.2/3.6/7.2: 詳細.1/.3/.6＋製造/whole12定義.6/1.8/3.6を一群.7/2.1/4.2 cap5、normal.5/1.5/3 cap4。元費用/SV上限/群開始見積りを保持、専有実費/token不明null。
''')
p=d/'481_PGPT詳細WBS.json';v=ld(p);o=next(x for x in v['tasks'] if x['id']=='WBS-P019-03');assert main not in o['ownedArtifacts'];o['ownedArtifacts'].append(main);o['evidencePlan']['candidateTestFiles'].append(test);o['evidencePlan']['plannedEntryPlacementSSC345']=dict(state='REGISTERED_NOT_PRESENT',spec=ref(spec),actualRuntimeQualification=False);wr(p,v)
p=d/'485_WBS網羅性・受入対応.json';v=ld(p);assert not any(x['path']==main for x in v['artifacts']);v['artifacts'].append(dict(kind='JAVA',path=main,owner='WBS-P019-03',costOwner='WBS-P019-03',sha256=None,acceptance='NOT_RUN',state='REGISTERED_PLANNED_NOT_PRESENT',relatedSsc='SSC-345',testIds='PT-MIG-PLACE001..012',historicalPath=None));wr(p,v);p=d/'486_WBS現行実績.json';v=ld(p);v['inventorySha256']=sha(d/'485_WBS網羅性・受入対応.json');v['plannedEntryPlacementSSC345']=dict(path=main,sourceCreated=False,newAcceptance=0,normalTestsExecuted=0);wr(p,v)
old=q/'1682_WBS65予実・Scenariofile順新十二通常後版435.json';f=ld(old);est=dict(low=1.2,base=3.6,high=7.2)
for k,value in est.items():
 for key in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[key][k]=round(f[key][k]+value,3)
f.update(previousForecast=ref(old),revision='436-MISSING_ENTRY_FILE_PLACEMENT_COMPONENT_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='P01903_MISSING_ENTRY_FILE_PLACEMENT_COMPONENT',estimate=est,reason='Existing Entry globalorder/File pergameorder do not connect entry_index/current file references; implement one composing component, not duplicate sort or DB authority.'));br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp']);fp=q/'1685_WBS65予実・Entryfile参照接続部品追加版436.json';assert not fp.exists();wr(fp,f)
c=ld(i/'2490_scenario_file_source_start.json');c.update(groupId='PGPT-WBS65-SSC345-ENTRY-FILE-PLACEMENT-DETAIL-AND-MANUFACTURE-20261114',recordPath=str((q/'1686_WBS65Entryfile参照接続製造開始.json').relative_to(r)),scope='MissingEntry-to-file/entryIndex/reference composition only, detail .1/.3/.6 plusmanufacturewhole12 .6/1.8/3.6 = .7/2.1/4.2cap5. Registerowner first; SSC345design-onlymain BEFOREcode; thenpurecomponentreuseEntry/File maps. NoactualDB/CurrentRootVMnativekeyUnitoperations. Alreadypricednormal.5/1.5/3 remains.',oracleRefs=[ref(spec),ref(b/'evidence/PG30368-scenario-file-order12-independent-source-trace-join-v1/manifest.json')],implementationArtifactPaths=[main],implementationCanonicalPlans=[ref(d/'481_PGPT詳細WBS.json'),ref(d/'484_WBSコスト枠・細分化.json')],source='e65e5e8bb546457e1a90e8ff7520cb4ca9e36eab',run='PG30390-ENTRY-FILE-PLACEMENT-MANUFACTURE',estimate=dict(low=.7,base=2.1,high=4.2),capPp=5,workIds=['P01903_SSC345_ENTRY_FILE_PLACEMENT_DETAIL_AND_SOURCE_WHOLE12'],forecastRef=ref(fp),nextCommand='PublishSSC345internalSS343/ledger detail-onlymain first, thennewregisteredMain/Test whole12 with literal entryIndex/file/globalgoldens. SourceGJF/CS/inventory/Gitfix beforealreadypricednormalall11physicalclosure/new4target. No oldwhole12confirmationreplay, noactualDBRootVMnativekeyUnit. Continuepastordinarydetail/source/group/report.');wr(i/'2500_entry_placement_start.json',c);print(json.dumps(dict(actualExit=0,newComponent=main,estimate=est,manufactureGroup=c['estimate'],remaining=f['revisedRemainingPp'])))
