# NK-ADM-001 Log SQL界面契約・実行結果

2026-10-26 08:58 JST、仕様079/群2287、source `6cd6ae7efc495f17e1ebb79291f26c7a90f99dc7`、dev-foundation。新PT-LOG-SQL001～008八method＋既Plain八method=実16/2suite全成功。SQL002は七optional128mask（128新Test IDではない）、SQL004はUI235独立2088byte goldenと一致。全failed/error/skipped/aborted/container異常0。

## command・環境・元manifest

repoから `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<対応工具>.py`。実command/開始終了UTC/OS/JDK/dependency/input/exec/XMLの各hashは下記manifest/stagesへ保存。Linux amd64 7.0.0-38-generic、JDK25.0.4+7、Maven3.9.12、JUnit5.13.4/platform1.13.4、JaCoCo0.8.15/ASM9.10.1/PMD7.28/CS14.3、既toolchain使用。

共有公開pathは `../018_NK-OPS-001/evidence/provisional/<以下>/manifest.json`。

|run/工具profile|真正結果|SHA256|
|---|---|---|
|PG10060-log-sql-precommit-static-v1 / pg10060_log_sql_precommit_static|rawPMD2/CS0/processing0/exit1、Test-only固定hash/base dac|62b36da8038b8702f2d05e5d0a28e059e2b58107499d7a9cecf03eb1254d53ef|
|PG10062-log-sql-six-compile-v1 / pg10062_log_sql_six_compile|正常六compile/package0/NullAway-Werror、製品PT0|2dcf40f6e754c945996de612411200237048d64afcae6080e376be644308bfe0|
|PG10064-log-sql-preflight-v1 / pg10064_log_sql_preflight|固定16宣言/2class/完全Main二unit/当source0|6b4a2831d85fa55dea0436daf6b289b49f6de3c8f54f70b49f72f1df868fa2c5|
|PG10066-log-sql-host-v1 / pg10066_log_sql_host|一JUnit/一session append=false・当16/2全成功0|3aab22d3ca1942cfe3c44098e641472ecff2109bdd3107d4749650c703a4c05b|
|PG10068-log-sql-post-v1 / pg10068_log_sql_post|全XML・CRC・exec/session・禁止product probe0/集計0|f909af4a8703b53aeef2903f23968393a88cfbff0efb713e231d90338f7ba8b2|
|PG10070-log-sql-quality-post-v1 / pg10070_log_sql_quality_post|当static-source一致/全Main1843同byte/旧Test1925同byte＋新3class/実0|2b7f32dbc5b85eeaddab5574313344418c3369ee7d545aebf4aad3e9ef524e05|
|PG10071-log-preflight-display-fix-v1 / pg10071_log_preflight_display_post|旧工具全文hash保全・表示一行だけ是正/全guard不変・metadata0/PT再演0|87f675f0c089dfb6ac39a933a3cc286057019d5b5f614a00481c59be25f7b9e1|

当Test hash `fffab98555572a0d0bae42485026c9607104d8d2812e2ca63a3c8bf732e59127`。各SQL001～008入力/独立expectedは079/同Testへ対応、actual=各assertion成功/実XML。実SQL/bind/rowは自己synthetic値で実DB/credential/log内容を格納しない。parallel=false/借用ConnectionのgetAutoCommit/isReadOnly/prepare以外0、RS→PS一回close、正常128mask/typed UTC/row projection/原page保持を確認。

## 当一run・完全二unitの実coverage

|unit/CRC64|line|method|class|branch|判定|
|---|---:|---:|---:|---:|---|
|LogRequest / 1500f98217023781|46/46|12/12|1/1|6/6|四指標100%|
|LogQueryRepository / ec477a734fc7a06f|107/113|18/18|1/1|22/38|全四100未達|

Repository例外・不正DB行/実PostgreSQL構文/plan/lock/並行/整合性/後条件は未実証。元DB試験はHOLDを維持。Graph9二Main/鍵関連等の禁止product probe0、旧exec/native合成0。原User四100はdacの別runであり当source全体へ移植しない。

## 静的適用性・工具障害

rawPMD二はline343 UseProperClassLoader（standalone自己public-interface proxy/非JavaEE）とline351 UseConcurrentHashMap（method毎serial私有Map/JUnit parallel=false/线程生成なし）の個別非該当。10070で当source/正常byte/実16と束縛。raw1を0へ偽装せず、新抑制なし。

BUG1792/YKT1543：10064 manifest/catalog/guardは正しく2suite、最後の表示だけ旧3が残存。起票後にqualified元工具全文を10071/qualified-original-tool.pyへ元invocation SHA一致で保全、表示一行だけcatalog/cases/physical集合から導出へ是正。AST/全非表示byte不変・真正manifest/実XML2を照合。元preflight/JUnit再実行なし。source凍結前の実装中header API表記整理はTDD準備、製品不具合ではない。正常compile中の早期preflight読取はmanifest未生成FileNotFound/出力作成前1、同compileの終了を待ち初回実preflight0、重複build/JUnit0。

現Java1802/Main965/Test837、新Log SQL pathは集約trace未登録。次の新規Question等とbatch登録して管理tool複製/旧行全文重複を抑え、所有/費用/旧成功/二UNKNOWNは変えない。正式1964PT/53scope、個別17/190、新受入0、工数null、QA051final/全安全HOLD不変。実経路の代替成功・工程全完了を宣言しない。
