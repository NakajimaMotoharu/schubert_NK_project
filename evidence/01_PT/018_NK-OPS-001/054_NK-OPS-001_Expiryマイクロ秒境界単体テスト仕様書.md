# NK-OPS-001 Expiryマイクロ秒境界 PT仕様

PG248/BUG-239、`ArtemisExpiryPurgeClient.observe/purgeObserved/selectorCutoff`、PT-OPS-MQ-026/028。RD MQ-009/OPS-009、UI251 §8、SS341 §9・SS331 §8.2。SSは「Broker expiry timestamp < run原本開始時刻−7日」と厳密に規定し、`BatchRun`はµs精度、Artemis `_AMQ_ACTUAL_EXPIRY`は整数msである。上位仕様の変更はない。

| Test ID | 前提・入力・操作 | Productionと独立した期待値・根拠 |
|---|---|---|
| PT-OPS-MQ-026追補 | 認証有効の隔離実Artemisで実Expiry属性`t`を取得。runを`t+7日`、`t+7日+500µs`、`t+7日+1ms`の順に作り、観測だけの件数と最後の実削除を確認 | SS341のstrict `<`より順に対象0/1/1。観測は削除0、最後に1件削除・残0。期待は実broker属性と固定500µs/1msの手計算で作り、Production selector関数は使用しない |
| PT-OPS-MQ-028 | 固定run `2026-09-24T00:00:00.000500Z`、fake管理返信1件/10byte/対象1。`observe`後`purgeObserved`。さらに1970-01-07T23:59:59.999500Zの負epoch境界を観測 | 厳密比較`t(ms)<cutoff(µs)`は整数閾値`ceil(cutoff(ms))`との`t<閾値`に等価。前者は`1789603200001`、後者は`0`。両呼出しのselectorが同じ固定閾値。`toEpochMilli()`のfloor値`…000`/`-1`では不合格 |

正常/境界/負epoch/固定run、並行drift・null/異常/例外は既存PT-OPS-MQ-023/024/027と組み合わせる。最大year9999は`BatchRun`/`Instant`の既存有効範囲と整数msの安全域であり、selector値の算術overflowを発生させない。Broker管理応答の整数ms以外は管理clientで拒否する。TDD REDは`/tmp/PG248-red.log`選択6件中2失敗（期待1/実0、期待`…001`/実`…000`）であり不認定。GREENは修正後別sourceで再試験する。Failed/flaky/skipped/not-runを合格算入しない。

選択実行: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl :schubert-nk-batch -Dtest=ArtemisExpiryPurgeClientTest test`。正式のcommit・branch・日時・環境・command/exit、Test ID別入力/期待/実際、coverage/static・hashは対の055と`evidence/manifest.json`へ固定する。秘密情報/生message/session/credentialは保存しない。
