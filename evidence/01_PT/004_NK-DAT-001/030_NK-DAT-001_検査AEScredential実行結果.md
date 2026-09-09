# NK-DAT-001 検査AEScredential実行結果

最新正式判定: PT-WEB-20260909-24/source3e325f49、dev-foundation、2026-09-09 12:17:13～12:23:32 JST、exit0。全902件（Protocol80/Storage34/API506/Web241/CHR41）、failed/error/skipped0、5 Java moduleのline/method/class/branch100%、NullAway/Enforcer/Spotless PASS、SpotBugs0。新8 PT105～112は全PASS、line42/method8/class1/branch22全missed0。8collector/21scopeの全hash・trace負canary、V001～013/Current baseline不変、秘密pattern scan0hitを確認。evidence/inbox-aes-credential/manifest.json SHA-256 `f53afc02bc86b7f0971755c09871d30d1bac317be7f4c372eead20294138af4d`。BUG-096/YKT-087はsource3e325f49で修正、全testCompileと再試験で完了。SS343 §6.2/031の権限判定・実IO/ACL/native/main/親gateは未完了。以下は探索時の履歴。

探索2で新8件と依存21件が成功。2026-09-09 12:16:26 JST、30.575秒、exit0。対象はbe4e0e32後の未commit実装、dev-foundation。正式23は本sliceを含まず、正式24のclean verify・証跡確定までは合格完了へ算入しない。

## 1. 探索と障害

探索1はtestCompileで明示close2箇所の警告を検出、exit1。新8件は未実行（BUG-096/YKT-087、修正前起票be4e0e32）。探索2はplain try/finallyへ修正し、close後拒否・二重close・100並行copy/closeの期待値を維持。警告抑止なし、411へ予防規則追加。依存Protocol5/Storage16、新AES8、failed/error/skipped0。SpotBugs bug/error0、NullAway/Enforcer/Spotless成功。

探索command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InspectorAesCredentialTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log `/tmp/pgpt-inbox-aes-credential-explore-2.log`。環境は正式manifestで固定する。

## 2. Coverage・期待値

InspectorAesCredential: line42/42、method8/8、class1/1、branch22/22、instruction201/201。029/PT105～112の独立入力と元key期待値、format/length/改行/version/Base64/32byte/canonical/null/破棄分岐を確認。過長・不足・不正padding bitは同一decoded keyでも拒否。入力消去は成功・失敗とも全0をassert。コピーは独立し、close後取得不可。内部Arrays.fillの全経路をcoverageで確認するが、JVM/JCA内部コピーの物理消去までは保証しない。

正式結果・source・hashは次の全体gate後に追記する。実IO/ACL/credential provisioning/親main・実NK CHR・IT/STは合格範囲外。
