# NK-DAT-001 検査credential権限実行結果

最新正式判定: PT-WEB-20260909-29/source4ec50a45、2026-09-09 14:12:02～14:18:24 JST、dev-foundation、exit0、全950件・5 Java module全4種coverage100%・静的解析0。当scope全Test ID成功、evidence/credential-access/manifest.json SHA-256 `fb2f527806d5bfce8bb7017e68e217f80bdf5283d96654e3caea7a75fdf7283f`。全26scope同時点性/hash/参照と017/019負canary成功。BUG-105～108/YKT-093～095再試験完了。BUG-104/SSC-051のSQL永続走査は039/040で成功、親batch接続は未完了。main/親gate/7参照/全Program完了は残件。本slice合格と工程全体の合格は区別する。以下は旧正式・探索履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、dev-foundation、2026-09-09 12:40:24～12:46:41 JST、exit0。全918件（Protocol80/Storage42/API514/Web241/CHR41）、failed/error/skipped0、5 Java moduleの4種coverage100%/静的解析0。新8 PTは全PASS、line30/method7/class1/branch28/instruction179全missed0。evidence/credential-access/manifest.json SHA-256 `c592639b76e48b5605ccca4dd9b96c5839d6f412f15cead5d6e498451d374a3a`。8collector/23scopeのhash/trace/負canary、V001～013/Current baseline不変、秘密pattern scan0hit。BUG-097/YKT-088はsource6dd862d0・本正式runで再試験完了。file reader/実systemd/main/親gateは未完了。以下は探索履歴。

探索1は2026-09-09 12:27:23 JST、35.844秒、exit0。dev-foundation/900410bd後の未commit実装。新8＋AES8＋Protocol5＋Storage16=37件PASS、failed/error/skipped0。InspectorCredentialAccessはline30/method7/class1/branch28/instruction179の全missed0、NullAway/Spotless/Enforcer PASS、SpotBugs0。031/PT113～120の全期待値を確認。正式24は本sliceを含まず、正式root/証跡が揃うまで完了にしない。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InspectorAesCredentialTest,InspectorCredentialAccessTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inbox-credential-access-explore-1.log。正式環境/branch/source/hashはmanifestで固定する。

型mode全bit反転、44byte ACL全352bit反転×file/dir、UID unsigned範囲、単一link/54～69byte、RO/空・null/alias/100並行を独立goldenで確認。native属性の出所・実credential file読取/close/systemd/親gateは別未完了。
