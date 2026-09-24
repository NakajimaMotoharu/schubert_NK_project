# NK-OPS-001 Expiry管理権限 PT仕様

PG243。対象は`src/deployment/artemis/etc/broker.xml`、`ArtemisRoleReadinessClient.approved/verify`、`ArtemisExpiryManagementAuthorizationTest.opsMq022MaintenanceCanOnlyInspectAndRemoveSelectedExpiryMessages`。RD MQ-001/002/009/010・OPS-001～017、UI251 §8、SS321 §10/12・341 §9、SSC-076/BUG-236/YKT-187。Productionと試験はArtemis 2.56.0・Java25。これはRBAC限定のPTであり、7日selector生成・実message削除・`batch_runs`・起動可否の完了を意味しない。

| Test ID | 事前条件・fixture・入力/操作 | Productionと独立した期待値・根拠 |
|---|---|---|
| PT-OPS-MQ-022 | 隔離EmbeddedArtemisにProduction `broker.xml`を読込み、ランダム資格情報のOps/保守/Web roleでCore管理電文を送る。`nk.expiry.q`の非空`_AMQ_ACTUAL_EXPIRY < 1`を`countMessages`/`removeMessages`に渡し、DLQ/同期Queueの同操作、Expiryの`removeAllMessages`、Broker全role照会を試す。終了後、一時管理reply Address残存を調べる | UI251・SS321/341とSSC-076の固定行列: 保守はExpiry選択count/removeだけ許可、DLQ/他Queue/全件削除/Broker照会は拒否。Webは管理拒否、Opsの既存Broker照会/個別DLQ操作は維持。認証・権限はArtemis実Broker応答から判定し、Production判定methodをexpected生成に使わない。管理reply残存0 |

Config oracleの`ArtemisBrokerConfigurationTest`は全matchとrole permissionの過不足・management RBAC有効を固定表で検査する。`ArtemisRoleReadinessClientTest`は実Brokerで12 matchと全12 permissionの独立変異を拒否する。正常/境界/異常/null/並行/再送観点のうち、本sliceは認可の正常・拒否と一時reply cleanupのみ。空/null selector、7日境界、並行削除・再送は保守Production処理の次PTへ保留し、本仕様の合格に算入しない。

実行command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl :schubert-nk-batch -Dtest=ArtemisExpiryManagementAuthorizationTest test`。正式全reactor/coverage/静的解析/48scope/hashの結果、対象commit・実行日時・exit・manifest hashは049および`evidence/manifest.json`へ追記する。資格情報、raw token、session IDは証跡へ保存しない。
