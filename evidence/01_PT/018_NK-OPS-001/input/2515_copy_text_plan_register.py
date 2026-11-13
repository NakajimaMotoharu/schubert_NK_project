"""Register and price a missing pure COPY text encoder; never DB connection or COPY execution."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO';q=d/'600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/PostgresCopyTextEncoder.java';test=main.replace('/main/','/test/').replace('.java','Test.java');assert not (r/main).exists() and not (r/test).exists();spec=r/'evidence/01_PT/019_NK-MIG-001/017_COPYtext製造・独立十二byte仕様.md';assert not spec.exists();spec.write_text('''# PostgreSQL COPY text encoder：製造と独立12 byte仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT004005/DAT004、UI254、SS331§2/343§10.1.4。既manifest/ID/file/entry対応はCOPY送信用field encodingを提供しないため、PostgresCopyTextEncoderを新規製造する。Java25/JDK/JSpecifyだけ、Source/DDL/外部電文/業務文字列値を変更せず、driver/DB/FS/SQL実行なし。原本masterやDBdumpをfixtureへ使用しない。

根拠: [PostgreSQL18 COPY・Text Format](https://www.postgresql.org/docs/18/sql-copy.html)（2026-11-14照合、同頁Text Format§）、Current program/database/generate_scenario_sql.pyのcopy_value/copy_rowは参照codeのみ。現行generatorやmaster/DBを実行・採取せず、expectedをその関数から生成しない。

既default FORMAT text/DELIMITER TAB/NULL backslash-Nの送信dataだけをUTF8で作る。encodeRow(List<nullable String>)とencodeRows(List<List<nullable String>>)はnull fieldをraw\\N、空文字を空field、literal backslash-Nを二重backslash＋Nへ分離。backslash/TAB/LF/CR/BS/FF/VTはそれぞれ\\\\/\\t/\\n/\\r/\\b/\\f/\\vのASCII列へescape。列間TAB、一行LF、header/SQL/terminatorは付けない。literal backslash-periodもescapeし、データをCOPY終端やSQLへ変換しない。文字列の数値解釈/trim/NFC変換は行わず、既callerの業務別NFC/control/byte・DDL型/参照検証を代用しない。NUL/未対応surrogateは固定安全IllegalArgumentExceptionで拒否し、正しいpairはそのままUTF8化する。

null outer/List/rowはNPE契約拒否、null fieldは有効値。rowは一列以上、複数rowは列数一致。空outerはzero bytesであり移行成功ではない。入力はouter及び各rowをprivate snapshot、外部へ保持/公開せず、返却byteは毎回別所有。stateless/並行呼出の可変共有なし、toStringは固定redaction。許可root/DB/transaction/COPY結果の権限や証明を発行しない。

PT-MIG-COPY001..012:
001 手書きASCII二row（1 TAB A LF/2 TAB B LF）、単一row両API。
002 null/空/literal backslash-Nはhex5c4e TAB TAB 5c5c4e LF。
003 backslash/TAB/LF/CRの手書きescape bytes。
004 BS/FF/VTのescapeとquote/ordinaryASCII非変換。
005 あ/é/音符U1F3B5の固定UTF8 hex、e+combining acuteを勝手にNFC化しない。
006 literal backslash-periodとSQL風文字列をfield textとして保持、終端を付けない。
007 null outer/single row/inner row拒否、null fieldは002。
008 empty outer zero bytes、empty row/二row目empty/列数不一致拒否、同列数正常。
009 NUL先頭/中間、孤立high末尾・high+ASCII/high+high/孤立low拒否、正pairと境界文字を許容。
010 mutable元row/outerと返却byteの所有分離。
011 安全固定例外/cause/suppressed無し、数字風leadingzero/符号/空白を保持、固定redaction。
012 所有8worker64task、Future各5秒/finallyshutdownNow-await10秒assert、未終端fail。全expectedはbyte literal/独立UTF8表、Production methodでexpectedを作らない。

全1physical、RootNullAway/lintWerror/全PMD/CS/SB・sourceごとの適用性、固定Git whole12一回/独立CRC初期化/単一exec/全四counterを確認。手除外/抑制/旧exec合算0。実PostgreSQL解釈/driver/pg_temp/COPY/transaction/全件数/権限/actualCurrent/RootVMnative/全451/ITSTは別未受入。

追加不足.9/2.7/5.4: 詳細.1/.3/.6＋製造whole12定義.5/1.5/3を一群.6/1.8/3.6 cap4、normal.3/.9/1.8 cap3。元費用/群開始見積り/SV原上限を保持、専有実費/token不明null。
''')
p=d/'481_PGPT詳細WBS.json';v=ld(p);o=next(x for x in v['tasks'] if x['id']=='WBS-P019-03');assert main not in o['ownedArtifacts'];o['ownedArtifacts'].append(main);o['evidencePlan']['candidateTestFiles'].append(test);o['evidencePlan']['plannedCopyTextSSC346']=dict(state='REGISTERED_NOT_PRESENT',spec=ref(spec),actualRuntimeQualification=False);wr(p,v);p=d/'485_WBS網羅性・受入対応.json';v=ld(p);assert not any(x['path']==main for x in v['artifacts']);v['artifacts'].append(dict(kind='JAVA',path=main,owner='WBS-P019-03',costOwner='WBS-P019-03',sha256=None,acceptance='NOT_RUN',state='REGISTERED_PLANNED_NOT_PRESENT',relatedSsc='SSC-346',testIds='PT-MIG-COPY001..012',historicalPath=None));wr(p,v);p=d/'486_WBS現行実績.json';v=ld(p);v['inventorySha256']=sha(d/'485_WBS網羅性・受入対応.json');v['plannedCopyTextSSC346']=dict(path=main,sourceCreated=False,newAcceptance=0,normalTestsExecuted=0);wr(p,v)
old=q/'1695_WBS65予実・原argv五件source是正通常保留版440.json';f=ld(old);est=dict(low=.9,base=2.7,high=5.4)
for k,val in est.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+val,3)
f.update(previousForecast=ref(old),revision='441-MISSING_POSTGRES_COPY_TEXT_ENCODER_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='P01903_MISSING_COPY_TEXT_ENCODER',estimate=est,reason='SS34310.1.4 COPY encoding not implemented by inventory/ID maps. Pure data UTF8/NULL/escape/scalar codec needed; actualDB/COPY/driver/transaction remain held, no physical DB or Current source execution.'));br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp']);fp=q/'1697_WBS65予実・COPYtext製造追加版441.json';assert not fp.exists();wr(fp,f)
c=ld(i/'2500_entry_placement_start.json');c.update(groupId='PGPT-WBS65-SSC346-COPY-TEXT-DETAIL-AND-MANUFACTURE-20261114',recordPath=str((q/'1698_WBS65COPYtext詳細製造開始.json').relative_to(r)),scope='MissingpureCOPYtextencoder only; detail.1/.3/.6+sourcewhole12 .5/1.5/3 = .6/1.8/3.6cap4. Ownerregistered beforecode/SSC346design-onlymain beforemanufacture. UTF8exact/null-vs-empty/literal slash/controlescapes/strictscalar/raggedrowrefusal/stateless; no normalization/businessvalidation/DB/SQL/driver/FSRootVMnativekeyUnit execution. Normal.3/.9/1.8 remains.',oracleRefs=[ref(spec),ref(b/'evidence/PG30462-target-adapter-prior-whole3-unchanged-no-replay-v1/manifest.json')],implementationArtifactPaths=[main],implementationCanonicalPlans=[ref(d/'481_PGPT詳細WBS.json'),ref(d/'484_WBSコスト枠・細分化.json')],source='24fff256ecba4b544780816a4e2d02c1c134bd08',run='PG30472-COPY-TEXT-MANUFACTURE',estimate=dict(low=.6,base=1.8,high=3.6),capPp=4,workIds=['P01903_SSC346_COPY_TEXT_DETAIL_AND_SOURCE_WHOLE12'],forecastRef=ref(fp),nextCommand='PublishSSC346SS343+914internaldetail-onlymain first; thennewregisteredpureJDKJSpecifyMain/Test12 with independentbytegoldens, GJFCS/inventory/Gitfix. Callercolumn-domainvalidation andactualPostgresCOPY/RootVMnative/HOLDremain. TargetAdapter oldwhole3 unchangedreuseonly; argv5normaloutsideclosedScopeheldguardunchanged. Continuepastordinarygroup/report; normalalreadypriced .3/.9/1.8 andfreshquota/hourly06:22:20JST.');wr(i/'2516_copy_text_start.json',c);print(json.dumps(dict(actualExit=0,sourceRegistered=main,estimate=est,remaining=f['revisedRemainingPp'])))
