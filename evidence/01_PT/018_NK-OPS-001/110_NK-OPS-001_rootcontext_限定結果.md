# Root起動context限定結果（PG296・未認定）

dev-foundation/3dce07ce4＋新rootcontext/test、2026-09-27 19:42:47 JST、Batch clean verify exit0。420PT（前412＋ROOTCTX8）、fail/error/skip0、全6counter missed0、SpotBugs0/NullAway/Werror。
command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch clean verify
Linux7.0.0-34/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。

native014: Ubuntu26.04/Linux7.0.0-31/Java25.0.4、schubert-nk-api.service名のroot transient Unit/ProtectSystem=strict/NoNewPrivileges/Home/PrivateTmpでactual context→A→context再確認exit0。初回probeはplatform依存class配置不足で失敗、補完後のみ成功。これは工具で業務API起動ではない。
初回compile/TDD fault oracle補正/static portabilityレビューは正式に算入しない。selected最後8PT・対象全counter0/静的0後module全回帰。nativeのraw PID/Invocation/journalはGit外、provisional PG296はpublic結果/hashだけ。正式source858713c0b/run24/1964PT/53scope・48.3%据置。
