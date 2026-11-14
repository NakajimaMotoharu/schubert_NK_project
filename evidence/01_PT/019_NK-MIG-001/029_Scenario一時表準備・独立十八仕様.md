# Scenario一時表準備・独立18仕様

NK-MIG-001/MIG003005006/MIG-DAT004005/DAT004/FUN004、UI254、SS311/331/34310.1.4 SSC352、WBS-P01903.02。

SS343 §10.1.4のCOPY前提となる二つのpg_temp staging表を、ScenarioStagingTablesが既に認証された借用Connection上に準備する。標準java.sqlだけを用い、PostgreSQL vendor SDKを必要としない。接続作成/URL/秘密/認証/権限変更や実DB試験の許可を意味しない。接続所有者は単一利用・期限/取消・正規migration actor・空target・原本保全・全transaction rollback/discardを保証する。本部品はautoCommit=falseを必須とし、setAutoCommit/commit/rollback/Connection.closeを呼ばない。

固定二SQLだけを順に実行する。CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM schubert.script_files WITH NO DATA。次にCREATE TEMP TABLE nk_mig_script_entries ON COMMIT DROP AS SELECT id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM schubert.script_entries WITH NO DATA。PostgreSQLのtemporary relation解決でpg_tempに配置し、qualified sourceだけを参照、generated body_search/identity/default/index/constraint/行は複製しない。型はsource DDLに追随する。FK/CK/NFC/件数・全asset照合/空targetへのinsertは後続必須であり、この二DDLだけでは成功保証しない。

IF NOT EXISTS/既存表再利用/DROP/再試行/修復を行わず、表名衝突等は元SQLExceptionで停止する。単一Statementを自分で作成し30秒queryTimeoutを設定、各executeUpdateの結果が0以外なら固定SQLExceptionで停止する。null Connectionは固定IllegalArgumentException、autoCommit=true・null Statementは固定SQLException。Statementは成功/SQL/Runtime/Error全経路でtry-with-resources終了し、close失敗で成功にしない。主障害/close障害の抑制関係はJavaの規定どおり保持、exceptionやSQL引数をloggingしない。toStringは固定redacted。

PT-MIG-STAGE001..018: 001独立二SQL全literal/列順/二回0、002timeout先行/Statement終了一回/借用Connection非所有、003null入力、004autoCommit拒否、005autoCommit元SQL障害、006create元SQL障害、007null vendor Statement、008timeout失敗時close、009第一DDL失敗/第二未実行、010第二DDL失敗、011第一DDL非zero(-1/1)、012第二非zero(-1/1)、013close失敗非成功、014主SQLとclose SQL抑制、015RuntimeとErrorの元例外/close、016再呼出は新Statement/元SQL不変・conn非変更、017finite8worker64task/Future5/finallyshutdownNow-await10、018固定redaction/失敗後別独立入力の正常性。fixtureはJava Proxyのjava.sql.Connection/Statementだけ、ネットワーク/driver/DB/FS/Root/鍵/permit/native/aru操作0。

必要closureは独立1Main/1physical/whole18だけ。新18定義、Root通常静的/NullAway/lintWerror/同一source・単一exec・独立CRC/init/XML/四counter100/実Code一致を要求する。元成功113の確認再演0、SDK禁止条件を変更しない。追加不足.8/2.4/4.8未較正を、詳細+PG18 .55/1.65/3.3cap4と必要normal18 .25/.75/1.5cap2へ分離。元費用/SV上限保持、専有費・実token null。実DB/ETL/全451/Rootnative/Actual4/HOLD未受入。
