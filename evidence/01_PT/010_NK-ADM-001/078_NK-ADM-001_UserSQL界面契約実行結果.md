# NK-ADM-001 User SQL界面契約・実行結果

2026-10-26 08:47 JST。仕様077、Program NK-ADM-001、UserQueryRequest/UserQueryRepository。source `dac963b29f62c0da68ca9d71f61db986a02d28a1`、branch dev-foundation。新PT-ADM-SQL001～008の八methodと既Core四/Response四、計16method/3suite。全16成功、failed/error/skipped/aborted/container failure各0。新規16件ではない。全体回帰・DB受入・正式認定は未更新。

## 実行・独立照合

公開証跡の共通prefixは `../018_NK-OPS-001/evidence/provisional/`。commandは各工具をrepoから `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<工具>.py` で実行、実子command/開始終了日時/OS/JDK/依存hashはmanifestのbegin/stages/receiptへ格納。Linux amd64 7.0.0-38-generic、JDK25.0.4+7、Maven3.9.12、JUnit5.13.4/platform1.13.4、JaCoCo0.8.15/ASM9.10.1、PMD7.28.0/Checkstyle14.3.0。導入記録の既toolchainを利用、新installなし。

|証跡/工具|真正結果|manifest SHA256|
|---|---|---|
|PG10038-user-sql-precommit-static-v1 / pg10038_user_sql_precommit_static|rawPMD6/CS0/processing0/exit1、新Testの旧hash、製品PT0|ae1bd69a1732bc3840aab6ae36d25b97d61ae790def208f5837d406bc91fac99|
|PG10039-user-sql-precommit-static-v2 / pg10039_user_sql_precommit_static_v2|rawPMD2/CS0/processing0/exit1、修正後の当Test hash|a9b7090a51267b2f9fef5c0ad6d94f40668fc9590ad7dc38b688e239c65b7b03|
|PG10040-user-sql-six-compile-v1 / pg10040_user_sql_six_compile|六module正常compile/package0、NullAway/Werror、PT0|37f90bd83ad135df52b631b603eb0b2859a9b21d86984615ea0829d46c3a2cf5|
|PG10042-user-sql-preflight-v1 / pg10042_user_sql_preflight|当16method/3suite・完全Main二unit・固定source/input照合0|b6de15c5c0eeb42d2bef1015ffa4ef0d77032b82cf750c8c01831b195c2aad16|
|PG10044-user-sql-host-v1 / pg10044_user_sql_host|実16/3、全成功0、一session append=false|8448e171c3e9b713bfdb3cfaa08c257945b1722db59725d7eaf2025b2031bc5c|
|PG10047-user-sql-post-v2 / pg10047_user_sql_post_v2|全XML/exec/CRC/session/二unit全物理counter照合0、禁止product probe0|a7d6c23e71cc2da5463bba8d88a64a9188ad47c859badfb098aab287882daf4c|
|PG10048-user-sql-quality-post-v1 / pg10048_user_sql_quality_post|全Main1843同byte・旧Test1922同byte＋新3class、当static hash一致0|6677ce92b1eae1e9f7f9da18566c428905fa86dba7e0a6b374f5e866fad8aa19|

当Test SHA256=`6b548e31a90ca745bc376d62f0b01b3d140059b23c5cda92b66bc2c0f8d3b84e`。固定入力と独立expectedは077/同TestのSQL001～008へ一意対応。XML実method名/結果は10044/10047、actual SQL/bind/UTC/secret非選択/borrowed transaction/解放順の各assertionが成功。実credential・実session・実DBは使用/格納なし。JaCoCo session名は自己試験用labelで認証sessionではない。

## 当source、一runの実coverage（旧exec合成なし）

|完全source unit/CRC64|line covered/total|method|class|branch|四100|
|---|---:|---:|---:|---:|---|
|UserQueryRequest / f28d7f65ed5a0732|62/62|13/13|1/1|18/18|実測100%|
|UserQueryRepository / 5359746fb8c80761|125/134|17/18|1/1|32/52|未達|

RepositoryのSQL例外/不正DB値などは未実行。実PostgreSQL構文・plan/整合性/lock/並行/DB後条件は本interface fixtureで実証していない。Graph9二Main/鍵Codec等の保持対象probeは0。通常DB試験・native/CHR/全scope451はHOLD/未完のまま。ここで二unit全体四100としない。

## 障害・静的適用性・限界

BUG1789/YKT1540：raw6中の四規約違反をTest-local同値記述へ是正（fix dac963b29）。残二はraw保持。line282 UseProperClassLoaderはstandalone host公開JDK interface proxyでJavaEE管理対象外。line290 UseConcurrentHashMapはmethod毎一fixture・同一thread/private Map、JUnit並列false/thread生成なしで非該当。10048で当source/static/正常byte/実PTを束縛。抑制追加0、raw PMDを0と報告しない。

BUG1790/YKT1541：旧suite2の準備guard残存を16/3定数へ是正、最初の拒否1はSLOT/JUnit起動前。是正後10044は最初の実JUnitで成功。重複PT0。

BUG1791/YKT1542：10046独立集計helperにだけRepository完全名誤記。compile-report実0、measure実1/timeout=false、stderr SHA=`387d1af8f79d49e853e4da8047dfb364f4d2c8d2cc9bc3670e261f3432dd96de`。元工具/receipt（work/pgpt-runs/PG379/pg10046-user-sql-post-v1）保持。別V2の10047で名前集合/SourceFile/CRCを修正し同exec/XMLを独立測定、製品/JUnit再実行0。元1を成功へ書換えない。

現Java1801/Main965/Test836。新Testの集約trace登録は次工程、現集約1798/1800は旧5012の測定で当sourceの率ではない。正式1964PT/53scope、個別受入17/190、新受入0、工数完成率null、QA051final/全HOLD不変。通常group/commitで止めず次の独立作業へ進む。
