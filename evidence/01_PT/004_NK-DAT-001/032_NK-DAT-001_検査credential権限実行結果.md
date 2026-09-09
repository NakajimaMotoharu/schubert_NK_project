# NK-DAT-001 検査credential権限実行結果

探索1は2026-09-09 12:27:23 JST、35.844秒、exit0。dev-foundation/900410bd後の未commit実装。新8＋AES8＋Protocol5＋Storage16=37件PASS、failed/error/skipped0。InspectorCredentialAccessはline30/method7/class1/branch28/instruction179の全missed0、NullAway/Spotless/Enforcer PASS、SpotBugs0。031/PT113～120の全期待値を確認。正式24は本sliceを含まず、正式root/証跡が揃うまで完了にしない。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InspectorAesCredentialTest,InspectorCredentialAccessTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inbox-credential-access-explore-1.log。正式環境/branch/source/hashはmanifestで固定する。

型mode全bit反転、44byte ACL全352bit反転×file/dir、UID unsigned範囲、単一link/54～69byte、RO/空・null/alias/100並行を独立goldenで確認。native属性の出所・実credential file読取/close/systemd/親gateは別未完了。
