# Inspector六Main例外graph・読取位置の製造仕様

Program NK-DAT-001、owner WBS-P004-04。RD DAT-001～011/OPS-009、UI212/241/251、origin/main SS311/312（SSC329/330）/324 12.1/341/343 6.9/352。元全24source対応は4229、独立期待値は以下で固定する。BUG2825/2826/2827/2829、YKT2359/2399。source製造の追加価格 .5/1.5/3pp、上限4ppは版366へ計上一回。動的試験・actual4.class/Root/native/DB/credential操作はHOLD。静的/逆変換確認をPT PASS又は実測coverageへ加算しない。

|Test ID（未実行）|対象|入力・独立期待値|
|---|---|---|
|INSP-GRAPH-2825-01..04|InboxResponseInspector.isStructurallyValid|通常構造不正→既false。既知snapshot/protocol/IAE/ISEのcause又はsuppressedに元Error→byte wipe後に同一Error。循環graphは既共有classifierで一回訪問。SQL/削除/再送を追加しない。|
|INSP-GRAPH-2826-01..06|InspectorApplication.execute / InspectorProcess.checkParent / InspectionRunExecutor.stopReason|各parent Guard既知IOのcause/suppressed Error→同一Error、通常IO→従来credential例外又はTIME_LIMIT。元割込/30分/one-shot/鍵とrootのowned cleanup順は不変。閉じたpure parser/鍵copy既知ISE/InboxCleanup由来cause無しcatalogは非該当。|
|INSP-GRAPH-2827-01..05|InspectorLauncher.run|callback credential/algorithm/IO内Error→同一Error、非fatal→70/50、閉じたconfiguration.Invalid→70。receipt print/checkError→terminal→closing順・OS wrapper契約は不変。|
|INSP-READ-2829-01..07|InspectorEnvironmentReader.readFile|初期position0/size期待値、正数readはcount=buffer差=channel差、EOF-1は両位置不変、最終position=expected。0/負不正/oversized count/位置異常/EOF移動→UNAVAILABLE。正常bytesは不変。ResourceScope SS333のtyped primary/secondary優先・一回close/全byte wipeを維持。|

製造確認は全6元source保全、最小差分の逆変換一致、Root Checkstyle/GJF、公開sourceの境界別reviewで行う。Compiler/NullAway/SpotBugs/通常PT/coverage/実経路は未実施であり残条件。上表の期待値は元メソッドから算出しない。実行可能wholeの資格成立後に欠落した例外/境界/並行試験を別見積りで追加する。元190、F02/F03、451をこの製造だけで閉じない。
