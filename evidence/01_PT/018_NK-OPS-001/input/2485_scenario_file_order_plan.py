"""Price missing per-game file order/navigation artifact, separate from entry mapping and ETL."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/ScenarioFileMigrationMap.java';assert not (r/main).exists();spec=r/'evidence/01_PT/019_NK-MIG-001/013_Scenariofileゲーム内順と前後対応・独立十二仕様.md';assert not spec.exists();spec.write_text('''# Scenario file ゲーム内順・前後対応：独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT005/FUN004、UI223§3.2/4/5（game/file表示順・前後navigation）・UI254§4、SS331/V002/V004・SS343§10。新Entry対応部品はglobal entry順だけなので、file/game順・前後は未実装。別artifactのPG/PTとして追加し、既Entry12の成功を再演しない。

予定ScenarioFileMigrationMap（bootstrap/migration）はFilePair(gameId,currentFileId,targetFileId)を受け、game1→2・各game内signed Current fileID数値昇順から各game1始まりdense displayOrderを作る。gameはV004固定NK game1/2（display_orderも1/2）へ解決済みの値で、Current gameからの実対応・DB完全性を証明しない。source keyはgame+currentFileId、targetIdは全gameで一意の1..N12。MappedFileもgame/target/orderのconstructor invariantを持つ。List/Mapは明示copyで不変、lookup/previous/nextの未知source・不正gameは安全固定例外。previous/nextはgames.display_orderとfile.displayOrderの全体順で隣のgameへも移る。端だけOptional.empty、未知を端と混同しない。

canonicalはNKMIGFILEORDER1 LF、game TAB currentFileId TAB targetFileId TAB displayOrder LF、game数値/source数値順ASCII。source signedを改変せず、targetの再採番大小や入力順から表示順を作らない。返却byteは別所有、各recordとaggregateの診断は固定redaction。

PT-MIG-FILEORDER001..012:
001 独立手書きgolden: game1(2→900/order1,10→100/order2)、game2(1→50/order1)。
002 各game source signed両端/0・game別同source分離・N12target上端。
003 同game/source重複拒否、別game同sourceは別keyの値。
004 target全game重複拒否。
005 game負/0/3/IntegerMAXをPair/MapRow/lookup/previous/nextで拒否。
006 target/order0・負・N12超/LongMAX拒否、1/N12許容。
007 null list/要素拒否。
008 mutable入力/返却List/返却byte改変からsnapshot保護。
009 同じsource IDのgame別lookupと未知拒否、固定cause/suppressed無し。
010 first/lastの空、game内隣接、game跨ぎ前後を独立tupleでassert。
011 empty headerと未知拒否、source gap/入力再順序でも各game順位固定。
012 owned8worker/64task Future各5秒・finallyshutdownNow-await10assert、返却byte独立/lookup/navigation。

全4physical（Main/FilePair/MappedFile/privateSourceKey）・JDKJSpecifyJUnitだけ。Source/owner/詳細SSC344を先行登録/公開、GJF/RootNullAway/lintWerror/PMDCS-SB・個別適用性、固定source whole12一回/独立4CRC-init-四counterを確認。expectedをProduction sort/encoderから作らない。失敗/未網羅は保持・除外/抑制/旧exec合算0。実DB/sourceGame/FK・master262file/各file entry順/全量ETL・RootVMnative鍵Unit/Go/全451/ITSTは別未受入。

追加不足価格1/3/6: 詳細.1/.3/.6cap1、source+whole12定義.5/1.5/3cap3、normal.4/1.2/2.4cap3。元/2 fullETL費用とS/V原上限を保持し、専有実費/token不明null。
''')
old=next(d.glob('1672_*'));f=ld(old);est=dict(low=1,base=3,high=6)
for k,v in est.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+v,3)
f.update(previousForecast=ref(old),revision='432-MISSING_SCENARIO_FILE_GAME_ORDER_NAVIGATION_COMPONENT_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='P01903_MISSING_SCENARIO_FILE_GAME_ORDER_COMPONENT',estimate=est,detail=dict(low=.1,base=.3,high=.6),sourceAndWhole12=dict(low=.5,base=1.5,high=3),normal=dict(low=.4,base=1.2,high=2.4),reason='Entryglobalorder component intentionally excludes per-game file order/navigation; approvedUI223 requires independent file artifact not yet implemented. Source game mapping/fullETL/endings remain originalunaccepted, no oldsuccess replay.'))
br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp']);fp=d/'1674_WBS65予実・Scenariofileゲーム順対応部品追加版432.json';wr(fp,f)
c=ld(i/'2475_scenario_entry_mapping_detail_start.json');c.update(groupId='PGPT-WBS65-SSC344-SCENARIO-FILE-GAME-ORDER-DETAIL-20261114',recordPath=str((d/'1675_WBS65Scenariofileゲーム順詳細開始.json').relative_to(r)),scope='Missingper-gamefileID/order/navigationdetailonly .1/.3/.6cap1; sourcegame+signedfileID keys, targetN12uniqueglobal, game1/2fixedV004displayorder, densepergame/sourceorder andglobalpreviousnext. ExistingEntryhelperdoesnotcoverfile. SSC344beforeinternalformat/mainpublish, includeSSC343limitedPGPTstatus inledger-only update; noRootVMDBnativekeyUnitETLoperations.',oracleRefs=[ref(spec),ref(b/'evidence/PG30302-scenario-id-order12-independent-source-trace-join-v1/manifest.json')],source='eac60a4ca541670fa3ecc1747017c9b585d6d536',run='PG30310-SCENARIO-FILE-GAME-ORDER-DETAIL',workIds=['P01903_SSC344_SCENARIO_FILE_GAME_ORDER_DETAIL'],forecastRef=ref(fp),nextCommand='RegisterSSC344actualnextnumber beforeSS343detail; preserveUI223/V002/V004, no newRDUIconstraints/QA. Puredata only file+game context/source signed/N12target-order; explicitunknownvsnavigationboundary. Design-onlymain2docs, includeSSC343status limitedEntry12/Coreeac/Unit024/Cdoc048e withoutunacceptedcode/evidence. Thennewowner/source/Test12 andnormal alreadypriced, continuePGPT noordinarydesignstop.');wr(i/'2486_scenario_file_detail_start.json',c);print(json.dumps(dict(actualExit=0,newComponent=main,estimate=est,remaining=f['revisedRemainingPp'])))
