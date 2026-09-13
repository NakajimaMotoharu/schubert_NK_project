# NK-OPS-001 Systemctl照会・共通終了scope PT追補

## 2026-09-13 選択実行結果（正式待ち）

設計先行8d767725/dev-foundation。redは10:44:34 JST/8.172秒/exit1、STOP014で期待IllegalState同一→実self-suppression IllegalArgumentException（/tmp/pgpt-pg173-red.log、SHA256 0ea80905202808f6ea6e222f6275b160f26013c267b267a53a929bc52c8a0edc）。修正後10:46:09/26.537秒/exit0、Storage8＋Batch16=24 PT成功、84compound全通過、failed/error/skipped0（/tmp/pgpt-pg173-green.log、SHA256 909785045d44dba01547c501d7eb9b2790342f3ff4ee253033ea9547703dc184）。NullAway/Spotless/SpotBugs未解決0。

選択coverage: SystemctlStateSource2class/14method/69line/10branch、InspectorUnitProbe4/20/106/20、共通ProcessResourceScope1/1/13/10がすべてmissed0。Probeの契約を変更せずscopeを抽出し、両collector subjectへ共通型を追加して追跡する。試験数/完成部品数は増算しない。全reactor認定待ち。

command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,SystemctlStateSourceTest,InspectorUnitProbeTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check。cwd=work/pgpt-foundation、未commit作業treeを後続source/formalで固定。実サービスの起動/停止・live process queryをPTへ流用せず公開合成fixtureのみ。

PG173/SSC063・BUG195/YKT154、実装前仕様。OPS009・UI251・SS311/341/343。Source7fc1b9b6までの変更を未認定のまま増算しない。対象SystemctlStateSource.read/close、ProcessResourceScope.use、InspectorUnitProbe.execute。既存STOP014 closeFailuresとUNIT015で追跡。

SSC063継続/PG173・BUG195/YKT154: SystemctlStateSourceのstdout/stdin/stderr・照会process TERMを、InspectorUnitProbeと同じ既知Stop/IO/Interrupted対未知Runtime/Errorのclose優先順位へ統一する。同じ例外のself-suppressionを禁止し未知bodyを同一identity＋固定Stop secondary、既知body＋未知cleanupは未知cleanupと割込flagを保持する。Probeの既存狭いscopeをpackage内ProcessResourceScopeへ移し両照会から利用する。Systemctlの全getter取得後null検査・逆順stdio close・最後に生存childだけTERM・5秒/固定8引数/1025byte上限・固定環境を変更しない。戻す予定の読取byteは全cleanup成功前に返さず失敗時消去する。サービス変更/SIGKILL/外部診断やcredentialの出力は禁止。ConfigurationGroupResolver/Future/JDBCの残候補は別段。

## 独立反例

STOP014内に4cleanup位置（stdout/stdin/stderr/TERM）×3unknown型（IllegalStateException/NPE/AssertionError）×7primary（同一未知wait、known readIO、timeout、Interrupted、badExit、oversize、成功）=84case追加。未知wait時は同一identity・固定StopGate(COMMAND_FAILURE) secondary1。既知primary＋未知cleanupは同一cleanup・secondary0、Interruptedだけflag保持。成功＋未知cleanupも成功でなく同一未知。cleanup位置1回・全stdio1close・生存childのみdestroy1（終了済は0）・force kill0を独立assertする。read済bufferはoversize/成功後cleanup失敗でも全zero。expectedをProductionから作らない。

TERM caseでは既存fixtureのquery終了時とcleanup時の生存状態を独立制御し、生存子へのdestroy故障を実際に注入する。他の単一failure/null/getter/5秒・1024/1025境界/固定command・環境とProbe UNIT009～016の全caseを再試験する。例外分類の全branchを共通scopeと両callerのPTで確認し、原因/suppressedにraw診断を残さない。

84compoundは既存JUnit Test ID内であり新JUnit加算0。共通helper抽出自体を新しい機能完成部品としない。未実行/failed/flaky/skippedを成功にしない。

## 実行・証跡

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12（421）。変更前STOP014 red、変更後SystemctlStateSourceTest/InspectorUnitProbeTest/ResourceScopeTest・全reactor・4coverage100%/NullAway/Spotless/SpotBugs、全41負canary・38scope整合。source/branch/command/日時/exit/BUG/SSC/hashとcoverageは本書・018/017正式manifestへ固定する。Current baseline不変更。GroupResolver/Future/JDBC/親実子/実NKCHR/IT/STは未完了。
