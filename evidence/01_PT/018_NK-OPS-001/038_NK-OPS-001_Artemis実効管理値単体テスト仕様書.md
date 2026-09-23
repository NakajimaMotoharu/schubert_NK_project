# NK-OPS-001 Artemis実効管理値 PT仕様

PG235、RD MQ-001/002/009/010・SYS-004、UI231/251、SS321 §2/3/13・342 §4。対象は`ArtemisManagementReadinessClient.verifyBroker/read`と固定redacted例外。限定Ops credentialでcallerが開いたCore sessionを借用し、management Addressへのread-only照会結果をSS321 literalと照合する。アプリroleをmanagementへ昇格させない。

| Test ID | 事前条件・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MQ-005 | SS321の隔離File Journal実Broker、Core management read | Broker名`schubert-nk-broker`、persistence true、NIO、journal file10MiB/min4/pool20、global512MiB、duplicate cache20,000/persist true、max disk90%、実使用率<90%。借用sessionはcloseされず、存在しない属性は固定redacted失敗。期待はSS321 §2/3の表から手列挙 |
| PT-OPS-MQ-006 | 各管理値1項目ずつ誤値へ変異。Disk値0.899999/0.9、負、NaN、Infinity、文字 | 正値だけ通過、90%以上と不正型をすべて拒否。対象値以外を固定し判定漏れを検出 |
| PT-OPS-MQ-007 | null session/reader、欠落値、非整数値、provider例外に秘密形文字列 | nullはfail-fast、実行中の故障は固定redacted例外・原因非公開。借用sessionをcloseしない |
| PT-OPS-MQ-008 | Production broker.xmlをsecurity=trueで起動。実行時生成した合成credentialの`nk_ops`と`nk_api`で同じ管理操作 | Opsだけが`activemq.management.#`に一時・非durable Address/Queueを作成・削除して11管理値を照会できる。完了後に一時Addressは0件。app roleは一時Queue作成/管理値照会を拒否。SS321 §10/SSC-075が独立oracle |
| PT-OPS-MQ-009 | management応答を返さない公開Core proxy、checked interrupt fault | `ClientConsumer.receive(2000)`で有限待ち、nullは固定redacted失敗。producer/consumer close各1、一時Queue delete1、借用session close0。interrupt flagは復元。timeout値はSS321 §10/SSC-075から独立指定 |

選択実行: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -Dtest=ArtemisManagementReadinessClientTest test`。Java25/Maven3.9.12/隔離Artemis2.56.0/`dev-foundation`。期待値はProduction methodから作らず、SS321 literal・SSC-075と試験内の独立Mapを使う。正常/境界/異常/例外/null/所有権・負roleを対象とし、業務Queueの再送を変更しない。Core管理helperは一時reply Address/Queueを作るため、業務状態不変と資源cleanupを区別する。Program全体および本番Ops credential配布、journal recovery error、acceptor、全ACL/Address設定、Queue閾値、Expiry purge、実NK CHRは別gate。Coverage、日時、commit、exit、関連BUG-232/SSC-075/YKT-185、証跡hashは039と`evidence/manifest.json`へ正式run後に記録する。failed/flaky/skipped/not-runは合格に算入しない。
