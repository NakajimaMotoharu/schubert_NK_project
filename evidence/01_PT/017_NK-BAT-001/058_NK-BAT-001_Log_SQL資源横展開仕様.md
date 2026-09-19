# NK-BAT-001 Log SQL資源横展開仕様

2026-09-20、PG178/SSC063/BUG195/YKT154。仕様先行、未実装・未試験。関連RD OPS009/DAT009、UI251、SS341§7.2/331§3.9/332、003の既存BAT026/029を拡張する。新JUnit件数や完成部品の増算を目的としない。

## 1. 対象・独立期待値

LogCleanupService.executeのSessionLease、SessionLease.acquire/closeの各Statement/ResultSet、計5所有release。実PG18の公開JDBC proxyでbodyとcloseへ独立したThrowableを指定する。close故障は実closeを実施した後に注入し、close回数、lock所有、借用Connection非close、commit/rollback、固定診断を独立assertする。同じProduction methodからexpectedを計算しない。

| Test ID | 対象・操作 | 期待値 |
|---|---|---|
| BAT026 | acquireのrow.next→resultClose、executeQuery→statementClose、unlockの同2組、execute body→lease close | 未知Runtime/NPE/Error primaryの同一物をcloseからもthrowしても元identityを保持。self-suppressionのIllegalArgumentExceptionへ変えない。全取得資源は1回close、borrowed connection0回 |
| BAT026 | 上記各bodyを既知SQL/Repository/停止理由、closeを未知3型 | 未知cleanup自身を非正常伝播。固定停止や成功へ変換しない。内外の全closeを維持 |
| BAT026 | primary未知、close別未知またはSQL | primary同一性、secondaryは固定CleanupStoppedException/DATABASE_FAILUREだけ、raw provider cause/messageを新規suppressedへ保持しない |
| BAT026 | 既存LOCK_BUSY/TIME_LIMIT/INTERRUPTED/BACKUP_GATEとSQL close失敗 | 003で承認済みprimary reason・causeなし/suppressed0を維持。割込はflag保持 |
| BAT029 | body成功＋close未知/SQL、取得失敗＋外側close、prepare失敗 | 結果を返さず適切な未知identity/固定DB失敗。取得済みだけclose。実lockの解放または失敗connection破棄必須を確認 |

fixtureの同一Throwableは各反例で新しく生成し、前反例のsuppressedを流用しない。未知3型はIllegalStateException/NullPointerException/AssertionError、実inputに秘密情報を使わない。null拒否・empty/hold10000/期限・再開・実lock競合・並行は既存018～029を全て再実行する。Resource helperをreflectionで直接呼ぶ試験はしない。

## 2. 境界・実行・完了条件

対象sourceは次の修正commitへ固定する。まず修正前BAT026/029の反例を実行し期待identityとの差を保存する。Sourceは正式02認定までは変更せず、他Mavenとの同時実行もしない。選択commandは既定JAVA_HOME/M2で `./mvnw -o --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,LogCleanupServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`、明示 `-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository` を使用する。正式はclean verify/全collector/同run source・hash・46負canary。後続059へ日時/OS/tool/branch/commit/command/exit/入力期待実際/coverage/証跡hashを記録する。

全line/method/class/branch100%、NullAway/Spotless/SpotBugs等成功、failed/error/skipped0を要求する。新たな解析抑止/coverage除外、正常結果への例外変換は禁止。本件は資源closeだけであり、Log transaction回復と各Repository・API JDBCの広域候補を解決したとはしない。BUG195/YKT154/SSC063、基盤全体、PGPT、IT/STは対応中のまま。
