# NK-OPS-001 Web/API DB pool単体テスト仕様書

Program: NK-OPS-001/NK-DAT-001/NK-WEB-002。Class/method: `ApiJdbcPool.open(DataSource)`、`WebJdbcPool.open(DataSource)`。RD SYS-002/004・DAT-001、UI212/226/253、SS311/342 §5.2/343 §5.2、PG271。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-DBPOOL-001 | 隔離PostgreSQL18/Flyway schema/`schubert_app`。本番credential不使用 | 信頼済みPGSimpleDataSourceを渡し、実SQLで`current_user`/DB名・Web専用表の拒否を取得 | DDL V005 role/grant・SS342のAPI max8/min2・接続待ち3秒、Hikari設定値。Web専用表はSQLSTATE42501。SQLはProduction methodを期待生成に使わない |
| PT-OPS-DBPOOL-002 | 同fixture | 同時8接続を借り、9件目を要求、返却後再借用 | SS342/UI253の上限8。9件目は接続待ち3秒後に失敗し、返却後は再利用可能。実DB接続数はpool MXBeanで8を照合 |
| PT-OPS-DBPOOL-003 | 同fixture | null DataSource、存在しないdatabaseのDataSource | API null契約はNPE、実DB起動失敗は例外でready不可。遅延成功を許さない |
| PT-OPS-DBPOOL-004 | Web用隔離PostgreSQL18/Flyway schema/`schubert_web_session` | 信頼済みPGSimpleDataSourceから実SQL・API業務表の拒否 | DDL V005 role/grant・SS342/UI212のWeb max2/min1・接続待ち3秒を固定値で照合。業務表はSQLSTATE42501 |
| PT-OPS-DBPOOL-005 | 同fixture | 同時2接続を借り、3件目を要求、返却後再借用 | SS342/UI212の上限2。3件目は接続待ち3秒後失敗、返却後再利用可能 |
| PT-OPS-DBPOOL-006 | 同fixture | null DataSource、存在しないdatabaseのDataSource | Web null契約はNPE、実DB起動失敗は例外でready不可 |

正常・境界・異常/nullを上記で覆う。並行上限はAPI8保持/9件目拒否、Web2保持/3件目拒否。再送はDB poolに適用しない。Credentialの実systemd読取、role/URL admission、起動親/readiness、実NK CHRは別PTで未完了。HikariCP 7.1.0は[公式設定契約](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)に従い、依存取得元はMaven Central。実行command/日時・commit・coverage・証跡hashは059へ記録。Coverage除外なし。
