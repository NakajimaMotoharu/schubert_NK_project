# BUG-013 / YKT-011 静的解析gate再現

- 発見: 2026-09-06 23:58:29 JST、base `4b4540f`＋未commit Web sender/dispatcher。
- Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am clean verify`
- Protocol69/Web48はfailure/error/skipped 0。coverage4指標100%だが、SpotBugsが`WebLogDispatcher.dispatch`のmulti-catch内`instanceof WebLogPayloadException`へ`BC_IMPOSSIBLE_INSTANCEOF`を1件報告しexit1。正式PASSへ算入しない。
- 両例外の動作はPTで正しく分類されたため、認証失敗が実際に成功へ変わる障害とは区別する。抑止やgate緩和は行わず、型別catchでerror codeを確定する。
- 横展開検索: `src/*/src/main/java`のmulti-catchと`instanceof .*Exception`（24行）。API OutboxはThrowable helper、API/Web duplicateは一般例外graph、API InboundTransactions/Web ArtemisReplyConsumerはExceptionでの共通受信隔離catchであり当該形式でない。その他multi-catchはその場でinstanceof分類なし。修正後に全module静的解析と両error codeの実DB再試験で確認する。
- 実行log本文・DB dump・固定電文・暗号鍵・credentialは保存しない。

再試験: `aceac18`の正式Run `PT-IDEM-20260907-01`でProtocol69/API93/Web48/CHR41全251件成功、全coverage100%、SpotBugs0。暗号拒否/JMS例外を別catchにし、対応error codeのSQL後条件は変更せず両方再試験した。BUG-013/YKT-011完了（2026-09-07）。
