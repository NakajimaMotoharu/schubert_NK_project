# 起動proof限定結果（PG295・正式未認定）

2026-09-27 19:18:41 JST、dev-foundation/7cdb25f3d＋PG294/295 dirty。Bootstrap clean verify exit0、79PT/失敗0/エラー0/skipped0、全6counter missed0（instruction2686/branch248/line514/complexity233/method109/class19）、SpotBugs0/NullAway/Werror。追加proof8件。
command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-bootstrap spotless:apply clean verify
環境Linux7.0.0-34/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。初回選択8PT成功でもEI_EXPOSE_REP1によりexit1、未認定。Mapの不変copy返却後上記module全体を再試験、抑制/coverage除外なし。

collector固定owner表へ新main/testを明示登録、未知bootstrapをrejectする既存契約は維持。新packetは既存serviceから未参照、機能受入/全security結線後の全Production・全scopeは未実行。root/native packet admission・現在permit・実NKは未達、formal1964PT/中心48.3%は増やさない。source/XML/coverage/hashはprovisional/PG295/manifest.json。credential/token/実Invocation/PID等は格納しない。
