# NK-OPS-001 NSS group終了scope PT追補

正式PT-WEB-20260913-14/source b234a4b356a9b456d3fdd245dbd6baed568be426/dev-foundation、2026-09-13 10:51:57～11:08:12 JST、Maven16分13秒/exit0。1415件PASS（Protocol80/Storage66/API660/Web241/Batch327/CHR41）、failed/error/skipped0。6 Java全4coverage100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、3固定path限定review・coverage除外なし。15collector/38scopeの同run/source/hashと41負canary成功。PG171～174の306compoundを既存Test ID内で認定し新JUnit/部品増算0。BUG198/YKT157完了、BUG195/YKT154/SSC063はSQL残候補等のため継続。実NK Characterization/IT/ST/親全体は未完了。 実行command/環境/input/expected/actual/coverage/関連BUG/SSC・SHA256は本書および017/018各evidence/manifest.json、同runの各JUnit XMLを正とする。以下は正式前の仕様・探索履歴。

## 2026-09-13 選択実行結果（正式待ち）

設計先行073ec1c6/dev-foundation。red 10:49:17 JST/7.204秒/exit1、GID005で期待IllegalState同一→実self-suppression IllegalArgumentException（/tmp/pgpt-pg174-red.log、SHA256 7d444774254c658a22a2174c5a4956e4bbec8fc44ac97152c6d42802b822d41b）。修正後10:50:28/33.698秒/exit0、Storage8＋Batch32=40 PT成功・84compound通過・failed/error/skipped0（/tmp/pgpt-pg174-green.log、SHA256 dc7950c94fb861e8c54d8ed178cedf158f6c557414f25e897efe470ba24ceefd）。NullAway/Spotless/SpotBugs未解決0。ConfigurationGroupResolver2class/26method/113line/66branch全missed0。Systemctl/Probe/EnvironmentFilesの関連回帰も成功。全reactor認定待ち。

command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,ConfigurationGroupResolverTest,InspectorEnvironmentFilesTest,SystemctlStateSourceTest,InspectorUnitProbeTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check。cwd=work/pgpt-foundation、未commit作業treeは次のsource/formalへ固定。84compoundは既存1JUnit内、PG171～174計306compoundを新JUnit数へ増算しない。

PG174/SSC063・BUG195/YKT154、修正前仕様。ConfigurationGroupResolver.resolve/readResult/scope、GID005 stdioFailureMatrix、OPS009/UI251/SS343 §6.12・411。SSC063継続/PG174・BUG195/YKT154: ConfigurationGroupResolverの3stdio・reader executor・join前TERM・最外TERMを明示scopeにする。IO/Interrupted primaryと未知Runtime/Error cleanupの競合は未知cleanup優先、Interrupted flag保持、未知primaryとcleanupは元identity＋固定IOException secondaryとする。IOだけの失敗は既存固定IOException、非同期readResultのRuntime固定診断・Error identity・NSS65537byte境界・5秒/全getter後null検査/TERM-before-join/全buffer消去を維持。StopGate専用scopeでIOExceptionを別の公開例外へ変換せず、このclass内のchecked IO用scopeを使う。executorは所有reader終端までjoinし、TERM無効・OS/NSS無応答を成功と扱わない。JDBC契約の横展開は別途残す。

## 独立反例とoracle

GID005内へ4cleanup位置（closeOutput/closeInput/closeError/TERM）×7primary（同一未知wait、readIO、timeout、Interrupted、badExit、oversize、成功）×3unknown型（IllegalStateException/NPE/AssertionError）=84 compoundを追加。すべて同一合成Throwableで注入し、未知bodyはidentity＋固定IOException secondary1、その他はcleanup identity＋secondary0、Interruptedのみflag保持。全stdio1close、destroy1（生存fixture）、forceDestroy0、全観測65537byte配列zero・元RECORD不変更を独立assertする。close注入とwaitのpositive到達を記録する。

JDK実executorは外部fault portを増やさず、既存native large-output/reader ownership/concurrency testでTERM-before-join・reader完了後だけ消去する。未知read例外は既存の固定「configuration group reader failed」へ変換、Errorは同一identity維持を既存GID005で再確認する。将来のJDK内部join故障を合成で全網羅したとは主張しない。scope自身の全条件/既知IO+IO・未知+IOは既存と追加PTで網羅する。

84caseは既存Test ID内、新JUnit数/部品数増算0。failed/未実行/flaky/skippedは合格としない。新たなトラブルは915/916へ先行起票。

## 実行・正式証跡

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12（421）。変更前GID005 red→変更後ConfigurationGroupResolverTest/InspectorEnvironmentFilesTest/SystemctlStateSourceTest/InspectorUnitProbeTest/ResourceScopeTest、全reactor/4coverage100%/NullAway/Spotless/SpotBugs、41負canary/38scope整合で検証。run/source/branch/command/日時/exit/BUG/SSC/hash/coverageは本書と017/018manifestへ固定する。Current baseline・外部仕様・coverage除外は変更しない。JDBC/親/実backup/IT/ST未完了。
