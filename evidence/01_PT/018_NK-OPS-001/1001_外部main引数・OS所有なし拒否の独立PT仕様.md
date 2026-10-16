# 1001 外部main引数・OS所有なし拒否 独立PT仕様

NK-OPS-001/OPS009/UI251/SS341342343、実`RootServiceLauncher.main`・`MorningProcessMain.main`・`CleanupProcessMain.main`。着手前にPG4662六XMLの**実method**を確認：Root main miss5line/4branch・同lambda miss1line/1method、Morning main miss2line/1method、Cleanup main miss2line/1branch。未網羅が残るnative privilege/profile分岐を今回合格にしない。

| Test ID / ExternalEntryRejectionTest method | 入力 | 独立期待値 |
|---|---|---|
| ENTRYREJECT001 / rootArgumentErrorsExitSeventyBeforeAnyAdmission | Root Mainへ空配列/OTHER/api小文字/WEB＋extra | OS CLI終了70、stdout/stderr空、作業directory生成物0 |
| ENTRYREJECT002 / evenExactApiWebArgumentsCannotAcquireOsOwnershipFromAnOrdinaryJvm | 当hostの普通owned child JVMへAPI又はWEB。env全空、OS Unit/親permit/manager INVなし、agentは普通Maven用でreserved native profileではない | Root自分のOS所有を獲得できず終了30、秘密診断非出力。引数だけでnative readinessや業務処理を許可しない |
| ENTRYREJECT003 / malformedMorningAndCleanupArgumentsNeverSelectBusinessWork | Morning --unknown/--resume＋非UUID、Cleanup --unexpected/--expiry＋extra | 終了70、業務callback前の引数拒否。**Morning/noargs・有効resume・実Backup・ADMINは発行しない** |

ProcessBuilderの固定argvでshellなし。childは当host Test専用PID/Process所有、30秒正常終了又は同子への通常TERMだけ、実VM/Unit/jobは操作0。全env空/空TempDir・generic JaCoCo同run agentで実public mainを呼ぶ。期待終了値/空出力/生成物なしはSSの固定終了契約から手書きし、Productionでexpected算出しない。agentはOS admissionを付与しない。許可されたnativeアクセスJVM flagは親module既定と同じであり、OSのUID/Unit/permitを偽造しない。

runner **pg4684_external_entry_rejection_selected.py** は元関連10suite＋新三methodの11suiteを全六projectに明示指定し、全source inventory/XML FES0/not-run0と実main3methodへの同run採取を確認。proof/environment全条件0も維持。実commandは既PYTHONPATHで当runner一回。固定snapshot/実command/終了値/owner/input hashes/XML hashes/log SHA/coverageはPG379/pg4684-external-entry-rejection-selected-v1。対象は純host negative entry契約であって新native streamや真正Root起動ではない。結果は実行後追記、現時点not-run。
