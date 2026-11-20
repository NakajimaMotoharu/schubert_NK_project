# CLNQUERY010 実行結果

Core `cdb649a5f054bc2ceed72ef57e55605f14a590d1`、Java 25、Ubuntu host、WBS-P017-07.01、YKT-2359。試験開始前のPG40866は直接依存BatchStepが未指定でコンパイル終了1、PTは未実行。固定closureにBatchStepを加えたPG40868で初回PTが成功した。

| Test ID | 成功 | 失敗・スキップ | 変種 | 既試験再実行 |
|---|---:|---:|---:|---:|
| CLNQUERY010 | 1 | 0 | 4 | 0 |

固定SQL次辺から元Errorが伝播し、文取得前の解放0と行取得後の行→文の一回解放を確認した。実PostgreSQLと実削除は未実行。局所coverage測定は未実行で、正式受入の判断は別途実施する。[PG40866 準備中断](../018_NK-OPS-001/evidence/PG40866-cleanup-query-jdbc-next-owner-v3/manifest.json) [PG40868 成功証跡](../018_NK-OPS-001/evidence/PG40868-cleanup-query-jdbc-next-owner-v1/manifest.json)
