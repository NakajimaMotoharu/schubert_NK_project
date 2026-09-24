# NK-OPS-001 credential ID契約単体テスト仕様書

Program NK-OPS-001、PG280/SSC-081。Class/method `ServiceCredentialId.forService/service/fileName/kind`。RD SYS-002/004、UI243/253、SS342 §4.2・343 §6。対象はWeb/API必須LoadCredentialの固定ID/形式種別だけ。実file読取・秘密byte/ACL/OS配布は後続gate。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-CREDID-001 | API Unit/SS343手組5 literal | API catalog | `db-api,mq-api,api-context-aes-current,api-inbox-response-aes-current,operation-hmac-current`の固定順、前2 password/後3 key |
| PT-OPS-CREDID-002 | Web Unit/SS343手組5 literal | Web catalog | `db-web,mq-web,web-session-aes-current,web-revoke-aes-current,web-log-aes-current`の固定順、前2 password/後3 key |
| PT-OPS-CREDID-003 | 両catalog | service判定・変更試行 | 全10 IDは重複なし、各IDは所属serviceのみ、Listは変更不可。SS342秘密分離 |
| PT-OPS-CREDID-004 | null service | `forService(null)` | NPEを正常な空listにしない |

正常/異常/null/サービス分離を確認。byte形式・境界・並行/再送は本catalogに非該当、後続reader/codecで実施する。期待IDはUnit/SSから独立転記しProductionで生成しない。coverage除外なし。選択commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-storage -Dtest=ServiceCredentialIdTest test`。正式command/日時/commit/coverage/結果/BUG/証跡path/hashは077と同Program manifest/resultsへ記録。
