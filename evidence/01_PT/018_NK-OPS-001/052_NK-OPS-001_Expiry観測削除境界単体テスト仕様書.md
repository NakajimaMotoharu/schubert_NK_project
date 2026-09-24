# NK-OPS-001 Expiry観測・削除境界 PT仕様

PG247、`ArtemisExpiryPurgeClient.observe/purgeObserved`・`Observation/Result`、PT-OPS-MQ-023/024/026/027。RD MQ-009/OPS-009、UI251 §8/11、SS321 §12・341 §9、SSC-076/077/078、BUG-236/237/238、YKT-187/188/189。Java25/Artemis2.56.0。削除前に親がV022の監査stageを**durable commit**するため、観測と破壊操作を別呼出しにする。借用sessionの所有、親DB commit、same-run再開、health/critical起動判断は本単体の対象外。

| Test ID | 目的・前提・fixture・入力/操作 | 独立期待値と根拠 |
|---|---|---|
| PT-OPS-MQ-023 | 固定run 2026-09-24T00:00Z、管理返信3件/300byte・対象2件を`observe`し、削除呼出0を確認後、同観測で`purgeObserved`。0件と対象0件も実行 | SS341の7日計算でcutoff 1789603200000ms、selector `_AMQ_ACTUAL_EXPIRY < 1789603200000`。事前対象2/推定200byte、削除2、事後1件/100byte。期待は固定fixtureの算術から算出しProduction methodを呼ばない |
| PT-OPS-MQ-024 | 対象>全体、削除差異、前後件数/byte不整合、負数、積overflow、秘密値を含むprovider故障、null入力 | 観測/削除のいずれも成功結果を返さず、固定redacted例外。nullは入口NPE。NPEを正常扱いせず借用sessionを閉じない |
| PT-OPS-MQ-026 | 認証有効の隔離実Artemisへ期限切れmessageをroute。同時刻/7日+1msのrunを使い、観測後・削除前にQueue件数を独立に再読 | 同時刻保持1、+1msで対象1/削除1/残0。実`_AMQ_ACTUAL_EXPIRY`から独立に境界を計算。観測では削除されず、管理reply Address残0 |
| PT-OPS-MQ-027 | forged cutoff/負値/対象過大/推定不一致・積overflow、観測後count/byte/selected drift、provider故障を注入 | fixed runとの不一致と削除前driftは`removeMessages`呼出0のままredacted拒否。V022に実際のstageがあると推定してはならず、親が後続でDBを証明する |

正常・境界・異常・例外・null・再送前driftは上記で検証する。並行変更は事前再観測で拒否するが、管理API読み取り後からremoveまでの原子的隔離は本単体では保証しない。親はAPI/Web停止・Queue health、run固定、DB durable stage/事後commit、故障再開を追加で検証する。ExpectedはSSの固定7日とfixture literal/実broker属性に依拠し、production結果から生成しない。Failed/flaky/skipped/not-runを合格算入しない。

選択実行: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl :schubert-nk-batch -Dtest=ArtemisExpiryPurgeClientTest test`。正式run/対象commit/coverage/静的/結果・入力/期待/実際、Test ID別証跡・hashは対の053と`evidence/manifest.json`。資格情報、token、raw session、試験message本文は保存しない。
