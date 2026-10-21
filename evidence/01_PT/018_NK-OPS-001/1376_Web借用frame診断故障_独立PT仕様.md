# Web借用frame UNKNOWN診断故障の独立PT仕様

NK-WEB-002/NK-OPS-001、SS313342354/SSC325、BUG1578/YKT1320、Test EXEC325001。追加発見をPG6386の合否へ混ぜない。現c341全4052は元39169実行中、全Main/Test不変更。SSC325 design-only PR187/source `1ce62afa931557d5b1d5911988958f16ee9a3830` →origin/main `8ed98d49d47093f217e6e6dc58a6c3c744361989`、06:09:37Z通常merge/fetch確認。四文書14insertだけ、未受入code/tool/evidence混入0、self approve/admin/protection迂回0。artifact attachment一回は100件上限で失敗、再送/既attachment削除なし。

## 独立oracle・scope

WebRuntimeExecution.executeのdummy start/await/stop/closeと固定診断だけ。自己所有最小child JVMでclose IO/RTE/Error×PrintStream診断通常/RTE/Errorの9入力、各modeでstart/await/stop/close各一回・固定「WEB cleanup unconfirmed」一回・再close0・escaped0/外側finally0を、1200ms観測後と割込後1200msで独立AtomicInteger/Thread生存から検証する。expectedは固定文字列/明示counter/順序で、Production呼出から生成しない。正常/null/start-await失敗は既二Testを変更せず関連回帰で検証する。

Driverのworkerは不活性dummy daemonのみ。JDK/java agentは当runの実引数を引き継ぎ、child probeを同runへ記録、coverage流用0。空env/TempDir出力/40秒wait、超過時は本人のProcess handleだけ終了。実Web/DB/JMS/VM/Root/current/key/intent/permitへの接続/起動/停止なし。子の通常終了はdummyの廃棄であり、実native解放の実証にしない。未特定拒否を探る操作ではないのでPT_DEFAULT。

## 事前準備と実行順

一@Testのdraftは [fixture](../../../tools/quality/fixtures/pg6396/WebRuntimeExecutionRetentionTest.java)、SHA256 `41a93f49afd61416cdab910710afa088e5301406d93bc8320787a6b600356e00`。まだsrcへ未反映・PG/PT完了加点0。当原22 XML a996be27のclasspath propertyだけを読み、JDK25.0.4 javac --release25 -proc:noneで同byte draftのsyntax/import check終了0（生成先 `/home/mini/codex/project1/work/pgpt-runs/PG379/pg6396-draft-syntax-only-v1`）。Production/Test実行0・正規Maven/null/staticgateの代用0・生成classをPTへ流用0。新red工具定義二0、WHOLE_QUALIFICATION_SHA=Noneなので全4052真正独立資格前の実行を拒否する。

まず元6386真正終端→6388原全artifact・当source資格/traceを保全する。その後だけTest draftをsrc/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrapへapply_patchし、正規format/一Testだけdiffguard・実4052資格hash固定、clean commit/push。PG6396新onlyred15/9（baseline12/既Execution2/新1、9入力を9試験へ水増ししない）を一回実行し反例と未到達を保存する。旧sourceのMainを変えずredを確認後、固定診断の保護・取得前finite policy・同frame5fenceを当一MainへPG、同oracle＋関連Life/共通retentionでgreen/静的/JVM・必要同源全体へ進む。現在未実行。失敗/not-run/flaky/skippedをPASSへ算入0。

WBS-P018-06主/関連P018-05,F03、群WEB_OUTER_FRAME_DIAGNOSTIC325（event1568）開始.5/1.5/4pp凍結。これは追加発見/今後の是正を区別する見積りで、原/v4の減額・完成率・親参照の追加費ではない。実N/T/専有費/工数null、正式1964/53・17/190/QA051final/PTALT不明代替0/保全HOLDを維持。通常unit/レビュー/commitで停止せず、元全体待機中は独立source点検を継続する。
