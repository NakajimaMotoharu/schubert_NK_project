# SSC-027 Scenario snapshot DB置換

対象: JdbcInboxCoordinator.replaceScenarioSnapshot、JdbcScenarioSnapshotReplacementTest、PT-IDEM-SR01～SR03。実装前にSSC-027とProgram PT仕様へ登録。DB専用部品であり、全段階service/実file/JMS/起動完了ではない。

独立oracleはSS324 LP形式をtest側DataOutputStreamで構成しJCE-HMACを計算、本番Flyway/限定app roleの隔離PostgreSQLへSQL投入する。29byteの合成cipherは暗号正常性を主張しない。旧/新byteはliteral、時刻は受信2026-09-08T00:00:00Z・完了00:00:01.123456Z・翌日同時刻期限。正常/rollback/別connection未commit不可視・同旧結果2並行1成功・stale拒否、19列全体の失敗後不変を検証する。正常時は暗号/keyだけ変化し他17列は保持。

全state/ref/layout/version/time、欠落行/欠落cipher、owner/correlation/canonical/key/HMAC、29byte各位置の改変を拒否。必須JDBC NULL、全public NULL、transaction mode、get/prepare/bind/update0/2/例外・適用後例外・close/複合closeを検証。Temporary bind byteはfinally全zero、入力recordの所有byteは不変。Connection/TXはcaller所有、例外の公開時sanitizeは後続stage責務。

探索01は新test内の未参照TWR変数4箇所で-Werror。変数をtry外へ保持し既存変数resource構文へ変更した（警告抑制/無意味assert追加なし）。探索02の3methodは成功。これらは正式clean verifyの合格件数に算入しない。正式runのsource/command/日時/環境/coverage/JUnit/hashはmanifestと002へ記録する。
