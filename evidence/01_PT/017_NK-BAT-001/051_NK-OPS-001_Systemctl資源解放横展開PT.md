# NK-OPS-001 Systemctl照会・共通終了scope PT追補

PG173/SSC063・BUG195/YKT154、実装前仕様。OPS009・UI251・SS311/341/343。Source7fc1b9b6までの変更を未認定のまま増算しない。対象SystemctlStateSource.read/close、ProcessResourceScope.use、InspectorUnitProbe.execute。既存STOP014 closeFailuresとUNIT015で追跡。

SSC063継続/PG173・BUG195/YKT154: SystemctlStateSourceのstdout/stdin/stderr・照会process TERMを、InspectorUnitProbeと同じ既知Stop/IO/Interrupted対未知Runtime/Errorのclose優先順位へ統一する。同じ例外のself-suppressionを禁止し未知bodyを同一identity＋固定Stop secondary、既知body＋未知cleanupは未知cleanupと割込flagを保持する。Probeの既存狭いscopeをpackage内ProcessResourceScopeへ移し両照会から利用する。Systemctlの全getter取得後null検査・逆順stdio close・最後に生存childだけTERM・5秒/固定8引数/1025byte上限・固定環境を変更しない。戻す予定の読取byteは全cleanup成功前に返さず失敗時消去する。サービス変更/SIGKILL/外部診断やcredentialの出力は禁止。ConfigurationGroupResolver/Future/JDBCの残候補は別段。

## 独立反例

STOP014内に4cleanup位置（stdout/stdin/stderr/TERM）×3unknown型（IllegalStateException/NPE/AssertionError）×7primary（同一未知wait、known readIO、timeout、Interrupted、badExit、oversize、成功）=84case追加。未知wait時は同一identity・固定StopGate(COMMAND_FAILURE) secondary1。既知primary＋未知cleanupは同一cleanup・secondary0、Interruptedだけflag保持。成功＋未知cleanupも成功でなく同一未知。cleanup位置1回・全stdio1close・生存childのみdestroy1（終了済は0）・force kill0を独立assertする。read済bufferはoversize/成功後cleanup失敗でも全zero。expectedをProductionから作らない。

TERM caseでは既存fixtureのquery終了時とcleanup時の生存状態を独立制御し、生存子へのdestroy故障を実際に注入する。他の単一failure/null/getter/5秒・1024/1025境界/固定command・環境とProbe UNIT009～016の全caseを再試験する。例外分類の全branchを共通scopeと両callerのPTで確認し、原因/suppressedにraw診断を残さない。

84compoundは既存JUnit Test ID内であり新JUnit加算0。共通helper抽出自体を新しい機能完成部品としない。未実行/failed/flaky/skippedを成功にしない。

## 実行・証跡

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12（421）。変更前STOP014 red、変更後SystemctlStateSourceTest/InspectorUnitProbeTest/ResourceScopeTest・全reactor・4coverage100%/NullAway/Spotless/SpotBugs、全41負canary・38scope整合。source/branch/command/日時/exit/BUG/SSC/hashとcoverageは本書・018/017正式manifestへ固定する。Current baseline不変更。GroupResolver/Future/JDBC/親実子/実NKCHR/IT/STは未完了。

