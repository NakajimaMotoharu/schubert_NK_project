# NK-BAT-001 backup検証確定caller実行結果

正式認定: PT-WEB-20260920-03/source1d5b44ad26736366950936653914f67e7e096fe2/dev-foundation、2026-09-20 02:01:07～02:16:34 JST、Maven15:26/exit0。全1463PT、failed/error/skipped0、6Java全line/method/class/branch100%、Production5静的解析未解決0、固定path3method限定review（coverage除外なし）、38scope/48負canary成功。新caller8PTを認定、Batch96class/583method/3665line/1899branch全missed0。SSC067のcaller限定範囲を完了し、実archive生成/7世代/親全体/PGPT/IT/STは未完了。raw log SHA256 `ab8d49270ce7dda80d962d63ef87b919eabb639740c73236309df8309cd9aea9`、sanitized証跡/実行環境/input/expected/actual/test/hashは017/evidence/manifest.jsonへ収録。以下は探索履歴。

PG184/SSC067・070/PT-BAT-274～281。選択PT成功、全reactor正式認定前。正式完了数への加算はまだ行わない。

初回 `/tmp/pgpt-pg184-green.log`: 2026-09-20 01:53:39 JST終了、14.697秒/exit1。testCompileのassertThrows条件式が異なる例外Class型の型推論に失敗し、Batch試験未実行。期待例外は変更せずClass<? extends RuntimeException>の明示で解消。初期試験作成時のコンパイル不備でProduction動作障害ではない。SHA256 `2e52ba487e600795e0902abe92aa82e3c314378f320f4d294aa9710eff52a2d9`。

再実行 `/tmp/pgpt-pg184-green2.log`: 2026-09-20 01:58:15 JST終了、33.072秒/exit0。Storage ResourceScope8＋新caller8＝16 PT成功、failed/error/skipped0。新caller 1class/4method/33line/8branch全missed0。NullAway/Enforcer/Spotless/SpotBugs成功、coverage除外/静的解析抑止追加なし。SHA256 `49e113fd268f3d239791ab64cf2009e1c302a9fda1762ba4f9043a20571a14b2`。

独立fixtureの161 IO/274 clock観測、全IO障害、全期限/割込位置、4file/全FD保全、SQL literalで両RUNNING/両SUCCESSと固定microsecond時刻を確認。commit応答不明後のDB実成功・再試行で元end再取得、破損fileでDB呼出0、別Connection競合と非lock所有者拒否も成功。公開traceはtarget/backup-completion-traces/PT-BAT-281-completion.txt、期待値は070と独立collector literalに対応。実archive生成・運用root配布・親全体・IT/STの成功ではない。

環境Ubuntu26.04.1 amd64/Linux7.0.0-31/JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、branch dev-foundation、親commit9094cdbd＋未commit PG184 source。正式sourceは全reactor前のcommitで固定する。

実行command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,BackupBundleCompletionTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。先行spotless:apply成功。raw logは一時領域、正式sanitized結果・manifest/hashは全reactor後に収集する。

collector拡張時の初回019は新classをshared-module独立fixtureへ未追加で1 ERROR、合格へ算入せず登録を追加。新8methodの欠落/重複/未知/失敗/skip/flakyとtrace全byte改変canaryも追加する。旧359件を新367件として認定しない。
