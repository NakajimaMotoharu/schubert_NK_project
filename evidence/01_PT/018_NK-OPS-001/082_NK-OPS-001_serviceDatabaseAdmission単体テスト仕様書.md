# NK-OPS-001 service database admission単体テスト仕様書

Program `NK-OPS-001`、PG283/SSC-082。対象 `ServiceDatabaseAdmission.<init>/verify`。RD SYS-002/004・DAT-001、UI212/243/253、SS342の専用role・SS343 §5.2/SSC-082・既存§6.6のInspectorと区別する。SQL oracleは固定literal `current_user`/`session_user`/`current_database()`/`pg_is_in_recovery()`、API期待role `schubert_app`、Web期待role `schubert_web_session`であり、Production methodを使って期待値を作らない。

環境はLinux/JDK25.0.4/Maven wrapper、隔離起動したPostgreSQLとmigration済みrole、`ApiLogDatabaseFixture`、public JDBC interfaceを包む`MaintenanceJdbcProbe`。fixtureのDB URLは隔離port・lowercase DBとし、秘密実値・DB dumpは保存しない。接続はTestがtry-with-resourcesで所有し、本部品は借用して閉じない。

| Test ID | 目的・入力/操作 | 独立期待値・観点 |
| --- | --- | --- |
| PT-OPS-DBADMIT-001 | API/Web各固定roleで実PG接続し、admissionを実行 | 固定SQL実値が各role、URLのDB、recovery=false、autoCommit=true/readOnly=false。接続は検証後もopen |
| PT-OPS-DBADMIT-002 | admin/cross-role、transaction中、readOnly接続を投入 | SQLState `08001`/固定非秘密文言、cause/suppressedなし。呼出側所有Connectionは未close |
| PT-OPS-DBADMIT-003 | 4列のnull/不一致、0/2 row、getAutoCommit/isReadOnly/prepare/execute/result close/statement close故障 | 全て固定非秘密SQLException、失敗値/SQL/URLを例外へ出さない。全branch・例外境界 |
| PT-OPS-DBADMIT-004 | null service/URL/connection、loopback URL正負とport1/65535境界 | nullはNPE、未知host/port0・65536・先頭0、大小文字DB、query/fragment/userinfo/長名を拒否。正規境界だけ受理 |

並行状態を保持しないimmutable部品であり、別接続の並行処理・pool上限は既存DBPOOL PTと後続実結線PTで検証する。再送は本部品対象外、DB/JMSの実readyとみなさない。実行commandは `sh tools/quality/030_run_pgpt_verify.sh <新run ID>`、保存検証は `python3 -B tools/quality/018_collect_verified_evidence_set.py <run ID>` と `--validate-only`。対象commit、日時、終了code、coverage、関連SSC/BUG、入力・期待・実際、sanitized evidence path/hashは083結果と同Program `evidence/manifest.json` に記録する。failed/flaky/skipped/not-runは合格に算入しない。
