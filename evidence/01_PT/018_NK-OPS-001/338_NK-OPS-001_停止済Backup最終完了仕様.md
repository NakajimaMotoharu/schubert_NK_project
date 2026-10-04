# NK-OPS-001 停止済Backup最終完了 単体テスト仕様書

Program/class/method：MorningCompletionEvidence.verify/constructor、MorningProcessMainの同cycle引継ぎ、既存MorningBackupUnitCycle.completedReceipt/recheckCompletedBackup、BackupUnitReceiptGate.requireStoppedResult。関連RD OPS009/BAK001/DAT009、UI251、SS341342343 SSC135136185186187、QA047、BUG704/YKT506。現在は仕様先行、試験未実行・合格0。

## 目的と独立oracle

Backupは実cycle内で明示停止済み、Cleanup/ExpiryはKEEP_ACTIVEという違いを維持する。同じcycleの停止前fresh receipt、正常stop client、bus/kernel/busの停止後実値、元baseline/同budget/ownerを最終完了へ引き継ぐ。Productionを呼んで期待値を生成しない。fixtureの18fieldは手書きBUS/KERNEL literal、receipt生成に使う本番parser/gateは被試験対象であってoracleではない。期待order/identity/exit/状態は固定列で独立記載し、coldを成功0へ補完しない。

| Test ID | 入力・操作・事前条件 | 独立期待値/境界・異常 |
|---|---|---|
| PT-OPS-STOPCOMP001 | Backup fresh正常0/30の実receiptを観測→stop client0→全kernel空→元receipt同一/停止後profile→request/intent退役を経た同cycleでcompletion.verify。new/reused/failedのDB literalを使う | 0はSUCCESS、真正非0は既存WARNING/六SKIP。停止前receipt.requireStillPresentは停止後active/exited→inactive/deadで拒否する旧再現を保持し、修正後は同cycle停止後検証で受理。DB前後・Cleanup/Expiry保持検査を省略0 |
| PT-OPS-STOPCOMP002 | 完全GC cold、同Invocation/exit/start/endの正常停止profile、foreign Invocation、部分cold、変質値、非空kernel、owner故障、元budget期限前/境界 | 完全cold又は同停止profileだけ元cycle/元fresh receiptを保持した場合に受理。未知/別generation/不一致/未終端/期限0はIOException、正常完了・原本DONEへ加算0 |
| PT-OPS-STOPCOMP003 | 未完了cycle、別cycleのcompletedReceipt、元receipt差替え、same actual cycleでの停止後再読故障、DB/cleanup/expiryの故障、null各component/verify引数 | cycle.completedReceiptの参照同一が必須、値同一receiptで代用不可。所有を捏造するno-op gateをnativeへ使わない。null契約はconstructor/境界で拒否。既存DB full-row/receipt拒否を維持、NPE正常扱い0 |
| PT-OPS-STOPCOMP004 | 当変更群のsource固定fresh全6＋同source正規署名候補→一回外部Morning→同Root ordinary/API/Web/Caddy→typed退役→原本DONE→全outer、native byte照合 | Maven actual0/FES0/static全6zero、変更対象全counter0、全source/hash/JUnit照合。同source native全後条件・CHR/DIF・秘密/traceまで未確認なら受入false。旧11cのA01 PASS/3268PTや親UNKNOWNを新sourceへ流用0 |

追加機能ではなく同S3/D05経路の是正。既存cycle全fault/receiptGate全境界/CompletionChecks TX非再入/CompletionEvidence全row/launch所有を関連選択へ集約し、変更群全回帰を他機能前に完走する。試験command/run/source/日時/環境/coverage/実際値・BUG/SSC・証跡hashは339と安全manifestで確定し、failed/skipped/not-runは合格へ算入しない。

## 現在の実証と非受入

PG463/source11c1feb1c0b51543f98c28e3f54213274648f06fの真正親f010f29e17ec4e5e9a38378185041e3e/944286、両Root→ordinary/5info/socket/Caddy TLS200、実CHR-A01 actual0/PASSを観測。08:13現在のthreadはpublishCompleted line271 retain、私有heapのframe-root IOExceptionはsource固定literal `backup receipt unavailable`、backtraceはBackupUnitReceiptGate→TerminalReceipt.requireStillPresent→MorningCompletionEvidence→publishCompleted。現在Backupは同e8d59b…/inactive/dead/正常0/全MainControl0/job空。この証拠は旧sourceの障害再現で、新是正合格ではない。原heap/DB/owner/tokenは非格納。原30分期限08:29:09を延長しない。
