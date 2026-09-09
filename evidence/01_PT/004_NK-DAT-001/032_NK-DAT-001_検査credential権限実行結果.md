# NK-DAT-001 検査credential権限実行結果

最新正式判定: PT-WEB-20260909-27/source4bbb32de、2026-09-09 13:27:18～13:33:40 JST、dev-foundation、exit0、全930件・5 Java module全4種coverage100%・静的解析0。当scopeの全Test ID成功、evidence/credential-access/manifest.json SHA-256 `57c7c99bb12ad6fbace2ff1e47c22d3cfbb4d228253a711514f2d2b1ac3a99c0`。全24scope同時点性/hash/参照と017/019負canaryを確認済み。BUG-098～100/YKT-089の再試験と正式26の集約非合格は458参照。内部sliceのみ合格、main/親gate/7参照/全Program完了ではない。以下は旧正式・探索履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、dev-foundation、2026-09-09 12:40:24～12:46:41 JST、exit0。全918件（Protocol80/Storage42/API514/Web241/CHR41）、failed/error/skipped0、5 Java moduleの4種coverage100%/静的解析0。新8 PTは全PASS、line30/method7/class1/branch28/instruction179全missed0。evidence/credential-access/manifest.json SHA-256 `c592639b76e48b5605ccca4dd9b96c5839d6f412f15cead5d6e498451d374a3a`。8collector/23scopeのhash/trace/負canary、V001～013/Current baseline不変、秘密pattern scan0hit。BUG-097/YKT-088はsource6dd862d0・本正式runで再試験完了。file reader/実systemd/main/親gateは未完了。以下は探索履歴。

探索1は2026-09-09 12:27:23 JST、35.844秒、exit0。dev-foundation/900410bd後の未commit実装。新8＋AES8＋Protocol5＋Storage16=37件PASS、failed/error/skipped0。InspectorCredentialAccessはline30/method7/class1/branch28/instruction179の全missed0、NullAway/Spotless/Enforcer PASS、SpotBugs0。031/PT113～120の全期待値を確認。正式24は本sliceを含まず、正式root/証跡が揃うまで完了にしない。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InspectorAesCredentialTest,InspectorCredentialAccessTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inbox-credential-access-explore-1.log。正式環境/branch/source/hashはmanifestで固定する。

型mode全bit反転、44byte ACL全352bit反転×file/dir、UID unsigned範囲、単一link/54～69byte、RO/空・null/alias/100並行を独立goldenで確認。native属性の出所・実credential file読取/close/systemd/親gateは別未完了。
