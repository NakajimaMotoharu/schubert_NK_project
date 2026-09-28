# 180 NK-OPS-001 Cleanup子DB単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象は `CleanupDatabaseSession` constructor/`execute`/close、`RootReleaseAdmission.verifyCleanup`、`MorningDatabaseSessionTest.Probe`。関連RD OPS-009/BAK-001、UI251、SS341 §3/7・343 §6、SSC-104/PG328。Test ID: PT-OPS-CDB001～009。既存 MDB001～012とROOTBOM001～009を回帰する。

前提: 固定loopback URL `jdbc:postgresql://127.0.0.1:<独立ポート>/schubert_nk`、`BatchDatabaseFixture` の実PostgreSQL、固定SQLによるrole/grant・Flyway、独立observer Connection、synthetic root/releaseは接続前置拒否の検証だけに使用する。資格情報は実値ではなく試験専用公開fixture、証跡には複写しない。mock JDBCでは各query/close/ロック状態を記録する。期待値はProductionの判定methodではなく、固定SQL literal、`pg_locks`と別backend `pg_try_advisory_lock`、SS341の状態遷移から算出。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| CDB001 | URLのlocalhost/別DB/query/port境界、null ports、wrong root、実PGに固定子actorだが合成releaseのschema不一致 | 不正URLは構築拒否、nullは明示NPE、wrong actorは拒否。合成schema不一致はcallback0・固定IOException、fresh release読取増加 |
| CDB002 | valid role・autoCommit/RW/read committed・single-row投影、schema→lock→callback→postcheck、owner close | callback1、roleは両方`schubert_batch`、DB名固定、nonrecovery、`pg_locks`保有前後true、全JDBC owner/secret close |
| CDB003 | role/database/recovery、state、row余剰/欠落、null projection | callback0、固定拒否・全close |
| CDB004 | schema拒否/lock取得失敗/held照会不一致 | callback0、固定拒否、取得済資源close |
| CDB005 | JDBC nullable lock値および別投影null注入 | fixture NPEでなくProduction固定IOException、callback0、所有者close。BUG-310/YKT-243再発防止 |
| CDB006 | callback null/IOException/未知例外、callback後のautocommit/readOnly/isolation/lock改変 | 成功を返さず固定または元の例外契約、後条件違反を成功にしない、owner close |
| CDB007 | 実PostgreSQLの別backendで同一advisory取得競合・終了後再取得 | 子が保有中のobserver取得false、子close後true。別backendの独立SQL結果 |
| CDB008 | 割込、Connection close失敗、既知/未知一次異常との二次close競合 | 成功を返さず例外の優先順位を守る、secret owner close |
| CDB009 | 実PostgreSQLの別管理接続で固定六列投影を読み、SCHEMA+V001～V023の24行・最終version023を独立確認してtest-only合成releaseへ束縛。公開子constructor/`execute` | constructor時のrelease read1、子DB session中のfresh read2、callback成功/全close。PG schema projectionで委譲経路を実行する限定試験であり、承認署名/BOMの独立oracleとはしない |

正常、境界、異常、例外、null、並行、再送はCDB001～009/MDB001～012/ROOTBOM001～009で確認。test-only `Probe`のnullable Boolean投影は明示分岐でinjectし、無意味なassertやcoverage除外を行わない。実行command/OS/JDK/Maven/日時/branch/対象commit/終了code/入力・期待・実際/四指標/BUG/SSC/evidence hashは181とmanifestで特定する。Cleanup parent M/A・両backup現物・本物Unit/実DELETEは本PTの合格範囲外で、受入済みに算入しない。
