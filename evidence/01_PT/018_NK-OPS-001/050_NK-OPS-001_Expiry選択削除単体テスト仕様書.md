# NK-OPS-001 Expiry選択削除 PT仕様

PG244。対象: `ArtemisExpiryPurgeClient.purge`/`Result`/`ManagementOperations`、`ArtemisManagementReadinessClient.expiryOperation/putExpiryOperation`、`ArtemisExpiryPurgeException`。RD MQ-009・OPS-009、UI251 §8、SS321 §10/12・341 §9、SSC-076/BUG-236/YKT-187、PG-D-244。Java25/Artemis2.56.0。これは保守専用Core sessionを借用する単体処理であり、親のBroker health/lock/credential/`batch_runs`記録/criticalによるAPI起動判断を代替しない。

| Test ID | 目的・事前条件・fixture・入力/操作 | Productionと独立した期待値・根拠 |
|---|---|---|
| PT-OPS-MQ-023 | 固定`BatchRun`開始2026-09-24T00:00:00Z、fake管理返信3件/300byte→対象2件→削除2件→1件/100byte。対象0件、Queue0件も試す | SS341の7日保持よりcutoffは2026-09-17T00:00:00Z/1789603200000ms。selectorは固定`_AMQ_ACTUAL_EXPIRY < 1789603200000`、対象2・削除2・推定byte200・実byte差200。対象0は`removeMessages`呼出0。expectedはOS日付計算と独立fixtureから固定し、Production methodから生成しない |
| PT-OPS-MQ-024 | fake管理返信の対象>全体、削除差異、前後件数不一致、byte増加、各負値、推定byte積overflow、provider秘密値例外、null依存/session/runをそれぞれ注入 | 不整合は成功結果を返さず、固定redacted `ArtemisExpiryPurgeException`。null境界はNPEを入口で拒否し、NPEをcatchして正常化しない。借用sessionをcloseしない。SS321/341の前後照合 |
| PT-OPS-MQ-025 | numeric応答Integer/LongとString/Double/Boolean/null、管理operationの空/null/未知selector、`removeAllMessages`、管理message writer例外 | 数値2型だけ許し、不正/未知/空filterは管理送信前に拒否。writer秘密例外は固定redacted。Artemis公開契約では空filterが全件削除となるため固定非空selector以外を禁止 |
| PT-OPS-MQ-026 | Production broker.xmlを認証有効の隔離Artemisに読み込む。Web roleが同期requestへ試験文を送信し、隔離broker内部で期限切れrouteを決定的に発火。実Expiry messageの`_AMQ_ACTUAL_EXPIRY`を独立に読み、run開始=expiry+7日、+7日1msを順に適用 | 同時刻は`<`条件不一致で保持1件、+1msでは対象/削除1件・残0件、byte前>0/後0、一時reply Address残0、借用session開。実Expiry属性・Queue countからexpectedを算出し、Production selector生成methodはexpectedに使わない |

正常/境界/異常/例外/null/再送は上記で検証。並行Broker到着時は前後件数不一致をfail closedするfake観点に限定し、親の起動排他・再実行は後続PT。`countMessages`・`removeMessages`は各2秒応答上限と一時reply cleanupを既存共通管理clientで共用する。Failed/flaky/skipped/not-runを成功に算入しない。

選択実行command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl :schubert-nk-batch -Dtest=ArtemisExpiryPurgeClientTest test`。正式全reactor/静的/全4coverage/48scope/hash・日時/branch/commit/exit/input/期待/実際/関連台帳/hashは051と`evidence/manifest.json`に固定する。資格情報、raw token/session、試験本文を保存しない。
