# NK-OPS-001 Artemis実効acceptor PT仕様

PG240。RD MQ-001/002/009/010・SYS-004、UI231/251/253、SS321 §2/10/13・342 §2/4、SSC-075。対象`ArtemisAcceptorReadinessClient.verify`、共有`ArtemisManagementReadinessClient.acceptors/acceptorStarted`。実BrokerのOps credentialで稼働acceptorの実効JSONとstartedを読む。承認済み固定値は`core`1件、Netty TCP、host`127.0.0.1`、port`61616`、protocols`CORE`のみ、extra propsなし。Application roleに管理権限を渡さない。これはacceptor限定gateでありjournal復旧/全role/Queue閾値/Expiry purge/親起動/実NK CHR-L01ではない。

| Test ID | 事前条件・fixture・入力/操作 | 独立期待値と根拠 |
|---|---|---|
| PT-OPS-MQ-013 | 隔離Artemis 2.56.0を認証有効・TCP loopback Core1件で起動、Ops sessionで実管理応答と`started`を取得。App roleで管理照会を試す | SS321/342の実効acceptorが固定1件/loopback/CORE/started=true。返却後も借用Ops session開、管理一時Address残存0。App roleは固定redacted拒否 |
| PT-OPS-MQ-014 | 公開JSONのname/factory/scheme/host/port/protocols/extraPropsおよび配列件数、欠落/追加/誤型/未知属性を1項目ずつ変異 | SS321 §2/13の固定listenerからの逸脱は全て拒否。`0.0.0.0`、IPv6 wildcard、AMQP混在、追加acceptorを拒否。期待値は実装から生成せず本仕様のliteral |
| PT-OPS-MQ-015 | null session/reader、null/malformed response、started=false/null、provider/encoder fault、borrowed ownership | NPEを境界契約で拒否し、管理異常は秘密causeなし固定例外。借用sessionをcloseせず、既存2秒/一時reply cleanupを共有。failed/skippedは合格にしない |

選択: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -Dtest=ArtemisAcceptorReadinessClientTest test`。正式全reactor、Java6 coverage/静的、018 OPS collector、全scope/hash、負canaryを確認。OS/JDK/Maven/branch/commit/実行時刻/exit/input/expected/actual/coverage/BUG/SSCとevidence hashは043/manifestに記録。実credential値、管理応答のraw secret、session/tokenは保存しない。

並行は起動前に単一Ops管理sessionで直列検査する設計（複数thread共有なし）、再送は管理要求が2秒で失敗し上位が起動を中断・再試行する契約であり、この単位が業務message再送をしない。PT-OPS-MQ-013では実roleで正常/拒否後に一時reply残存0を確認し、共通期限・cleanup故障分岐はPT-OPS-MQ-008/009を同じ全reactorで回帰する。
