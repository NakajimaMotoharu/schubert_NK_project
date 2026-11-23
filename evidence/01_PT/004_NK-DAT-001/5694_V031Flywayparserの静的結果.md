# V031のFlyway文分割・トランザクション分類

PG43680／PT-DB-ACL031-S05。固定source `aeeb6bd49eac49162902d408cc6f491f19b5bbde`、JDK 25.0.4、Maven依存のFlyway core／PostgreSQL parser 13.4.0。入力はPG43666で照合済みのV031と同じSQL（SHA-256 `1b481fdb50b84c1bb6204144d04813f6f362013394cada067085d457a90ce3a3`）。

| 順 | SS331／SSC-479から独立に固定した期待値 | 当parserの分類 |
|---:|---|---|
| 1 | SET ROLE NK_OWNER | transaction内可 |
| 2 | ALTER DEFAULT PRIVILEGES FOR ROLE NK_OWNER REVOKE EXECUTE ON ROUTINES FROM PUBLIC | transaction内可 |
| 3 | RESET ROLE | transaction内可 |

コンパイル・実行とも終了0。parserが返す3文の文字列、順番、transaction分類、参照SQL数0を照合した。検証器は文解析器だけを呼び出し、JDBCドライバとDB接続なし、SQL実行0。静的な事前確認として扱う。実PostgreSQL構文・既定ACL・既存ACL、新規／V030更新のPTは未実行。BUG-3721／YKT-2921の実DB終了条件は残る。

[実行manifest](../018_NK-OPS-001/evidence/PG43680-v031-flyway-sql-parser-v1/manifest.json)にコマンド、固定入力、原終端・出力のpathとSHA-256を記録した。
