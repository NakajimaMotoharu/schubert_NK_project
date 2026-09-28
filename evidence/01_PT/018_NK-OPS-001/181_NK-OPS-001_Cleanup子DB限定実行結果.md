# 181 NK-OPS-001 Cleanup子DB限定実行結果

2026-09-28 JST、PG328/SSC-104、branch `dev-foundation`、source `ac709cda50478f877d254f85ade45fe3410f3298`。RD OPS-009/BAK-001、UI251、SS341 §3/7・343 §6。PT-OPS-CDB001～009、既存MDB001～012/ROOTBOM001～009回帰。Linux/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0。

| 入力・期待根拠 | 実際・判定 |
|---|---|
| 固定loopback/role/schema/null・閉鎖、row余剰/欠落、callback後状態、割込・close故障。SS341の接続順と固定SQL/別backend観測から期待値を独立算出 | CDB001～009 全PASS。実PostgreSQLで子専用`schubert_batch`接続、別backend advisory競合false→close後true。callback前schema拒否/role違反時0呼出 |
| 実六列projectionを別管理接続で読み、SCHEMA+V001～V023の24行と最終023を独立確認してtest-only releaseへ束縛 | CDB009公開constructorは構築時read1、子session内fresh read2、正常帰還。これは委譲の限定PTであり、実署名/BOM・本物Unitのoracleではない |
| `CleanupDatabaseSession`と内部`CleanupSchema`の4指標 | 前者 line119/119・branch58/58・method17/17・class1/1、後者line6/6・method2/2・class1/1、定義branch0/0。いずれもmissed0、除外0 |
| Production security変更の全回帰 | 6module clean2,284PT/337suite、F/E/S0。内訳 Protocol80/Storage149/Bootstrap175/API742/Web555/Batch583、SpotBugs全0、build exit0。報告commandは179記載と同一sourceでJaCoCo reportもexit0 |
| Production全体100% | Protocol/Storageは四指標missed0。Bootstrap branch37/line11/method4、API 1/19/3、Web 1/19/3、Batch branch0/line42/method19が未網羅。全module class missed0 |

BUG-310は初回fixtureのnullable lock投影がNPEとなり選択38件F1（修正前起票）、明示null分岐後はCDB005でProduction固定IOException/callback0/所有者close、限定39件＋依存16件 F/E/S0/static0。BUG-311は最初の証跡manifestに一時`.part` pathが349件残っていたためhash検証失敗（修正前起票）。最終pathへ修正後、349file＋source5 hash不整合0、既存PG326 manifest348file不整合0、全provisional81 manifestで`.part/.tmp/.staging`参照0、sanitized JUnitのproperties/output/failure/skip0、秘密pattern scan0。YKT-243/244は台帳へ根拠を記録する。

証跡: `evidence/provisional/PG328-six-security/manifest.json` SHA256 `51aab47dff5ffaa9c38181de4e2996842aa0c7fc0b4b8bf18504367e80a2477c`、外部原始logはmanifestにSHAのみ記録しGitへ格納しない。実行日時/OS/tool/branch/commit/command/exit/入力・期待・実際/coverage/関連BUG/SSC/file hashはmanifest参照。実親M/A・backup両現物・真正子Unit・DELETE・Artemis起動/CHRは未実施、正式source/run/48.3%見積は据置。
