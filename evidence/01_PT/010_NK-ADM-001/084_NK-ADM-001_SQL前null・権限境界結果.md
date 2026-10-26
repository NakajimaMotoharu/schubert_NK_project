# SQL前境界・実行結果

2026-10-26 12:28 JST、仕様083/014-007。source `d4ba0fcbe8855b9674413d395b46d2de7bb2ded9`、branch dev-foundation、Production Main21d7c3042不変。新Test IDはADM-PRE001～004、LOG-PRE001～003、QRY-PRE001～006の計13/3suite。原JUnitはPG10206、実compile-launcher/JUnit各終了0、found/started/succeeded13、failed/error/skipped/aborted0。再演0。

実command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg10206_pre_sql_boundary_host.py`。環境はLinux amd64 7.0.0-38-generic、JDK25.0.4+7-1-26.04-Ubuntu、Maven3.9.12、JUnit5.13.4/platform1.13.4、JaCoCo0.8.15/ASM9.10.1。実引数/dependency hash/時刻は下記manifestのbegin/stages、compileはPG10202の六module正常終了0/PT0/NullAway-Werror。試験に実DB/VM/ネットワーク/鍵/外部serviceを使用しない。

|証跡（018_NK-OPS-001/evidence/provisional配下）|SHA-256|
|---|---|
|PG10200-pre-sql-boundary-static-v1/manifest.json|304002cdde4e5114ead0b8eec4421c302b14eb2a3d3159fdb59e421f4293194f|
|PG10202-pre-sql-boundary-six-compile-v1/manifest.json|a050b88ec51ec64a18d0abd5adf5ea2bf64304a496735acb40f4da8091dfa8f2|
|PG10204-pre-sql-boundary-preflight-v1/manifest.json|2ff834c4411928d402f0cdc1f67aa579edca4d6bf6566cd256c82623df55502c|
|PG10206-pre-sql-boundary-host-v1/manifest.json|6ae5f9a5f80539efa065ccf388c8b719c5d4bcc748dc12de57bf9a94fce6837e|
|PG10207-pre-sql-metadata-correction-v1/manifest.json|432c3fea41180595aeadfef8f5fb0fb6de208ee6f509be6b03725146805ec25d|
|PG10208-pre-sql-boundary-post-v1/manifest.json|69ad4f6834f20955c7bf1b76609c5960c3eab0dd2b0d3fa7f2ce54c93f9fb21b|

独立postは原XML三/一意13ID・method集合/各件期待値assertion/一exec・session/全対象CRCを照合。JDBC guard三のlambda命令hit0、各SQL専用helper命令hit0、保留Main二/別module等probe0。全Main1843同byte、既Test1931同byte、新三sourceに対応する六Test physicalだけ追加、旧source成功や旧coverageを合成0。

|当runでの完全Repository source-unit|Line hit/total|Method hit/total|Class hit/total|Branch hit/total|
|---|---:|---:|---:|---:|
|UserQueryRepository|17/134|6/18|1/1|1/52|
|LogQueryRepository|5/113|2/18|1/1|0/38|
|QuestionQueryRepository|14/170|4/30|1/1|2/64|
|内包RowMapper interface|0/0|0/0|0/0|0/0|

前三classは未達、no-Code interfaceは測定PASSでなくN/A。SQL後条件・row異常・並行/再送・実DB等は本runで未実行/HOLDを保持し、全P010/P014/451へ受入を拡張しない。

PMD raw16/CS0/processing0/exit1は保存。CloseResource13は実Connectionを開かない自己Proxyで任意呼出しを禁止するfixture、UseProperClassLoader3はJavaEEでないJDK公開interfaceのstandalone Proxyとして各file/lineを10208へ個別記録、抑制0/適用違反0。原hostのnewTestIds4だけはBUG1804/YKT1555へ修正前起票し、原工具/hash/manifestを保持して10207で一意catalog13へ追記訂正、PT再演0。関連SSC追加なし。

正式1964PT/53scope・既受入17/190・工数率null・QA051final保留を維持。今回増分は新13Test IDの限定成功であり、新WBS受入13件ではない。traceは次の三path batchへ接続する。
