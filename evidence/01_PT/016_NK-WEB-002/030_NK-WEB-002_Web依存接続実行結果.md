# NK-WEB-002 Web依存接続 PT実行結果

PG221、PT-SCR113～116。2026-09-24 JST、JDK25.0.4/Maven3.9.12/Linux、`dev-foundation`未commit差分で選択4件は最終exit0、failed/error/skipped0。command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-web -Dtest=WebDependencyReadinessTest test`。隔離PG/Flyway Web roleとSS321 broker設定を使い、provider SQL/IAE/JMSの秘密本文を固定例外でredactする。初回のfixtureではQueue欠落でもJMS consumer生成が成功し得たため、Queue存在をこのPTで証明したとは扱わず、SS321 management実効設定を別必須gateとしてPG-D-221へ記録した。最終fixtureはbroker停止拒否を確認する。失敗した探索runは合格に算入しない。

正式全reactor、4coverage、静的解析、41scope/manifest/hash、実NK CHR-A01/L01は未認定。正式run後に対象commitと結果を追記する。秘密値・raw session/token・master dataは保存しない。接続probeはProduction親起動やQueue実効設定の代用ではない。
