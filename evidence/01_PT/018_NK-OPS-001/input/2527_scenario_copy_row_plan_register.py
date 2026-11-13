"""Price/register concrete script_entries COPY row validation; no DB/host migration operation."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO';q=d/'600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/ScenarioEntryCopyRow.java';test=main.replace('/main/','/test/').replace('.java','Test.java');assert not (r/main).exists() and not (r/test).exists();spec=r/'evidence/01_PT/019_NK-MIG-001/019_ScenarioEntry十二列COPY行・独立十二仕様.md';assert not spec.exists();spec.write_text('''# Scenario Entry COPY rowの12列検証：独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT004005/DAT004/FUN004、UI223/242§4.4/254、SS331§2/V002・SS343§10。既COPY encoderは列別の型/nullable/byte/NFC制約を扱わないため、ScenarioEntryCopyRowを新規製造。実Current抽出/ID-map連結/全件数/game-FK/DB/transaction/driver/pg_temp/COPYは別未受入、外部hostはaru新規利用禁止・haruka構築/個別条件未確認HOLDを維持する。

Inputはnullable Stringを要素に持つnonnull Listで、既V002の非generated 12列順を固定: id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at。body_searchはgeneratedなので含めない。列数12以外拒否、mandatory9列はnull拒否、optionalはline/speaker/labelだけ。Listをprivate copy＋変更不能wrapperで保持、返却fields/columnNames変更不可、copyBytesは既encoderへ渡すだけでbyte別所有。固定redaction・安全例外/cause無し、元文字列を修正/trim/暗黙再採番しない。

Target id/file/order及びnonnull speakerはcanonical positive N12 decimal、gameは1/2。entryIndexはcanonical0..IntegerMAX、nonnull lineNumberは1..IntegerMAX。内部送信のcanonical表現なのでleadingzero/sign/空白/小数を受け付けず、外部ID仕様は変更しない。typeはdialogue/narrationだけ、dialogueはspeaker必須、narrationはspeaker null。

Bodyはnonnull NFC/validUTF8かつ1..4096byte、nullable labelはNFC/validUTF8・0..128byte、rawBlockはnonnull NFC/validUTF8で当DDLにないbyte上限を加えない。column別control検査はlabelをinline（ISO control不可）、body/rawBlockをmultiline（TAB/LF/CRだけ可、それ以外のISO control不可）として、Currentの改行を含むbody表示とCOPY escapingを保つ。NUL/孤立surrogateは拒否、非NFCを黙って変換しない。原本内容を読まず、実移行data適合性を推定しない。

created_atはcallerがtransaction内で共通採取したInstantのcanonical UTC文字列を入力（toStringと完全一致）。年0001..9999・µs精度、parse不能/非canonical offset又は余剰fractionは安全拒否。row同士の共通Instant・実DB型/FK/全件数はこの値クラスの受入ではない。

PT-MIG-ROW001..012:
001 手書き12列/完全COPY bytes、column orderからgenerated body_search除外、dialogue speaker有/NFCラベル/本文改行を固定。
002 narration speaker nullとline/label null、空label/rawBlock許容、nullと空のCOPY区別。
003 N12/ゲームの下上境界、各列0/負/N12超/leadingzero/sign/空白/小数/未知game拒否。
004 index0/IntegerMAX・line1/MAX、負/MAX+1・line0/空拒否。
005 type null/未知/Dialogue大小違い、dialogue speaker null/narration speaker有の個別拒否。
006 Body ASCII4096/4097、あ1365+ASCII1=4096/あ1366=4098、label128/129・multi byte上端、rawBlock4097以上も切捨てない。
007 nonNFC/孤立surrogate/NUL・ISOcontrolの全field別拒否、body/raw TAB/LF/CR許容・inline labelでは拒否。UTF16 fixtureはchar配列から作り既PMD defectを再現しない。
008 mandatory全9列null・optionalとcolumns数11/13/nullouter、固定安全例外でraw値非露出。
009 時刻year0001/9999・µs、年0/10000・ns/offset/非canonicalfraction/不正値拒否。
010 入力変更/返却List/columnNames/byteの所有分離。
011 文字列trim非実施・安全toString、encoder null拒否・失敗後次の独立値に影響なし。
012 所有8worker64task、Future各5秒/finallyshutdownNow-await10assert、全expectedは固定列/ASCII/UTF8 hex・独立byte算術、Production methodでexpected生成しない。

新Row1＋支援Copy1の全2physical/同source・通常static・全Row12/Copy12の24を単一execで必要変更群の全closure品質として初実行、newdefinitionsはRow12のみ（既Copy12の新定義加算0）。旧exec合算/除外/抑制0、実JVMCodeと既定counterを独立postで確認。旧Current/実DB/RootVM/native/全451/CHR/ITSTを代用しない。

追加不足1/3/6: 詳細.1/.3/.6＋製造whole12定義.5/1.5/3を一群.6/1.8/3.6cap4、normal必要24 .4/1.2/2.4cap4。元費用/群開始見積り/SV上限を保持、専有実費/token null。
''')
p=d/'481_PGPT詳細WBS.json';v=ld(p);o=next(x for x in v['tasks'] if x['id']=='WBS-P019-03');assert main not in o['ownedArtifacts'];o['ownedArtifacts'].append(main);o['evidencePlan']['candidateTestFiles'].append(test);o['evidencePlan']['plannedScenarioCopyRowSSC347']=dict(state='REGISTERED_NOT_PRESENT',spec=ref(spec),actualRuntimeQualification=False);wr(p,v);p=d/'485_WBS網羅性・受入対応.json';v=ld(p);assert not any(x['path']==main for x in v['artifacts']);v['artifacts'].append(dict(kind='JAVA',path=main,owner='WBS-P019-03',costOwner='WBS-P019-03',sha256=None,acceptance='NOT_RUN',state='REGISTERED_PLANNED_NOT_PRESENT',relatedSsc='SSC-347',testIds='PT-MIG-ROW001..012',historicalPath=None));wr(p,v);p=d/'486_WBS現行実績.json';v=ld(p);v['inventorySha256']=sha(d/'485_WBS網羅性・受入対応.json');v['plannedScenarioCopyRowSSC347']=dict(path=main,sourceCreated=False,newAcceptance=0,normalTestsExecuted=0);wr(p,v)
old=q/'1702_WBS65予実・COPYtext新十二通常後版443.json';f=ld(old);est=dict(low=1,base=3,high=6)
for k,val in est.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+val,3)
f.update(previousForecast=ref(old),revision='444-MISSING_SCENARIO_ENTRY_COPY_ROW_VALIDATION_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='P01903_MISSING_SCENARIO_ENTRY_COPY_ROW',estimate=est,reason='Generic COPY encoder has no column-specific validation. New row connects V002 twelve typed fields/nullable/NFC-byte constraints to same-source pure encoder; actualDB/loader/allcounts/FK remain originalunaccepted. Host switch adds no permissions or runtime work.'));br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp']);fp=q/'1705_WBS65予実・ScenarioEntryCOPY行製造追加版444.json';assert not fp.exists();wr(fp,f)
c=ld(i/'2516_copy_text_start.json');c.update(groupId='PGPT-WBS65-SSC347-SCENARIO-COPY-ROW-DETAIL-AND-MANUFACTURE-20261114',recordPath=str((q/'1706_WBS65ScenarioEntryCOPY行詳細製造開始.json').relative_to(r)),scope='Newpure12-columnScenarioEntryCopyRow: ownerfirst/SSC347beforecode, detail.1/.3/.6+manufactureRow12 .5/1.5/3 = .6/1.8/3.6cap4. N12/game/int/nullable/type-speaker/NFC/UTF8byte/control/bodyraw/timestamp/immutablefields. ExistingCopyencoderreuse. No actualDB/driver/SQL/COPY/FSRootVMnativekeysUnit/aru newop/haruka test start. AlreadypricednormalneededRow12+Copy12 same-source24 .4/1.2/2.4 remains.',oracleRefs=[ref(spec),ref(b/'evidence/PG30522-copy-text12-independent-source-trace-join-v1/manifest.json')],implementationArtifactPaths=[main],implementationCanonicalPlans=[ref(d/'481_PGPT詳細WBS.json'),ref(d/'484_WBSコスト枠・細分化.json')],source='e9e5d0f0031742bbc604503deb6417b7b7829ac4',run='PG30542-SCENARIO-COPY-ROW-MANUFACTURE',estimate=dict(low=.6,base=1.8,high=3.6),capPp=4,workIds=['P01903_SSC347_SCENARIO_COPY_ROW_DETAIL_AND_SOURCE_WHOLE12'],forecastRef=ref(fp),nextCommand='PublishSSC347SS343+914detail-onlymain BEFOREcode, combineSSC346limitednormalstatus/PG30516-18/Coree9e5/result0dbdb withoutunacceptedcode. ManufactureRow/List12 validation andwhole12literalTests, GJFCS/inventory/GitfixedCore. OneclosedSource2/physical2 normalwhole24needed fornewRow-to-encoder composition, notoldCopyconfirmation/oldexecmerge. aru newopsprohibited/harukaPMOpending/noexternalstart; otherHOLDunchanged. Continuepastordinarygroup/report, freshquota/hourly07:22:22JST.');wr(i/'2528_scenario_copy_row_start.json',c);print(json.dumps(dict(actualExit=0,sourceRegistered=main,estimate=est,remaining=f['revisedRemainingPp'])))
