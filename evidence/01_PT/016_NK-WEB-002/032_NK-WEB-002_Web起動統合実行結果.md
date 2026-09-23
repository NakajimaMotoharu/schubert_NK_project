# NK-WEB-002 Web起動統合 PT実行結果

PG222、PT-SCR117～119。2026-09-24 JST、JDK25.0.4/Maven3.9.12/Linux、`dev-foundation`未commit差分で選択3件は最終exit0、failed/error/skipped0。command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-web -Dtest=WebApplicationTest test`。実隔離PG18/Flyway Web role・組込みArtemis・loopback Tomcatと承認済みsecurity chainでLogin GET、CSRF、cookie、匿名DB row、direct403、依存故障時のHTTP未bindを検査した。初回探索ではcookie名を一般名`SESSION`と誤想定し、SS314の`SCHUBERT_NK_SESSION`にPT oracleを直した。初回探索失敗は合格算入しない。

正式run、source commit、Java4coverage、静的解析、全41scope、manifest/path/hashは未実施。PG/PT合格とは未認定。SS321管理APIでのQueue実在・実効設定、Production credential、API listener、実NK CHR-A01/L01、IT/STは別残件。
