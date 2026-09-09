# NK-DAT-001 検査AEScredential実行結果

2026-09-09 最新確定: dev-foundation/source20af737d、正式PT-WEB-20260909-42（19:47:16～19:54:18 JST）、全1075件（Protocol80/Storage50/API634/Web241/Batch29/CHR41）PASS、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのSpotBugs0/NullAway・Enforcer・Spotless PASS（CHR runnerのSpotBugsは未設定）。12collector・35証跡scopeの同run/source/branch/hash/参照、017の1件・019の14件負canary成功。DB26部品240 PT＋batch2部品29 PT＋OPS2部品16 PT＝30部分成果285件確定。PG-D-146の実Linux flock8 PT（実コマンド双方向競合、32並行、FD/例外回収、inode差替え）を追加し、BUG140/YKT110を再試験完了。正式41はbranch1不足で不合格・後続3module未実行として保存。親root lockfile検証PG-D-147はSS/PT仕様のみ未合格。親inactive/実backup/DB引渡し/root設定publish・全cleanup監査・通常Question writer/replay・RERUN-001は残る。BUG-014/UIC-006/SSC-049/052継続、加重見積約4割（35～50%、456）、試験件数だけで加点しない。週間残18%。元dev-web Scenario3fileは保全・不算入、CHR41はrunner PTであり実NK互換gateではない。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/inbox-aes-credential/manifest.jsonの現行SHA-256は `0b2f79ca17ffe5e56d70e98cf86a08279d0af2f071e7721619396f8bd438ff57`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

探索2で新8件と依存21件が成功。2026-09-09 12:16:26 JST、30.575秒、exit0。対象はbe4e0e32後の未commit実装、dev-foundation。正式23は本sliceを含まず、正式24のclean verify・証跡確定までは合格完了へ算入しない。

## 1. 探索と障害

探索1はtestCompileで明示close2箇所の警告を検出、exit1。新8件は未実行（BUG-096/YKT-087、修正前起票be4e0e32）。探索2はplain try/finallyへ修正し、close後拒否・二重close・100並行copy/closeの期待値を維持。警告抑止なし、411へ予防規則追加。依存Protocol5/Storage16、新AES8、failed/error/skipped0。SpotBugs bug/error0、NullAway/Enforcer/Spotless成功。

探索command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InspectorAesCredentialTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log `/tmp/pgpt-inbox-aes-credential-explore-2.log`。環境は正式manifestで固定する。

## 2. Coverage・期待値

InspectorAesCredential: line42/42、method8/8、class1/1、branch22/22、instruction201/201。029/PT105～112の独立入力と元key期待値、format/length/改行/version/Base64/32byte/canonical/null/破棄分岐を確認。過長・不足・不正padding bitは同一decoded keyでも拒否。入力消去は成功・失敗とも全0をassert。コピーは独立し、close後取得不可。内部Arrays.fillの全経路をcoverageで確認するが、JVM/JCA内部コピーの物理消去までは保証しない。

正式結果・source・hashは次の全体gate後に追記する。実IO/ACL/credential provisioning/親main・実NK CHR・IT/STは合格範囲外。
